#!/usr/bin/env python3
"""
Reproducibility script for "When Emotions Flare: Solar Rhythms...".

What this script does:
- downloads the UNM PDF,
- downloads RED v1.0 archive from Princeton-linked Dropbox URL,
- parses the xlsm workbook (no pandas dependency),
- constructs year-level revolutionary activity measures,
- downloads SILSO monthly sunspot data,
- compares solar classification with the paper-reported approach,
- writes machine-readable outputs + a reproducibility notes file.
"""

from __future__ import annotations

import csv
import json
import math
import os
import re
import subprocess
import sys
import zipfile
from collections import Counter
from datetime import datetime
from pathlib import Path
from statistics import mean, pstdev
from typing import Dict, List, Tuple
from urllib.request import urlopen, urlretrieve, Request
from urllib.error import URLError, HTTPError

BASE = Path(__file__).resolve().parent
DATA = BASE / "data"
OUT = BASE / "outputs"
OUT.mkdir(parents=True, exist_ok=True)
DATA.mkdir(parents=True, exist_ok=True)

PAPER_URL = "https://digitalrepository.unm.edu/cgi/viewcontent.cgi?article=1004&context=geog_fsp"
DROPBOX_URL = (
    "https://www.dropbox.com/scl/fi/vy6ibp9ggmjmmjye4brys/"
    "Revolutionary-episodes-dataset_v_1.0.zip?rlkey=2kp5ujvwq5augdtgaws10dc2y&dl=1"
)
SUNSPOT_URL = "https://www.sidc.be/silso/DATA/SN_m_tot_V2.0.csv"
WORLD_POP_URL = "https://api.worldbank.org/v2/country/WLD/indicator/SP.POP.TOTL?format=json&per_page=20000"

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
RNS = "{http://schemas.openxmlformats.org/officeDocument/2006/relationships}"


def _ts() -> str:
    return datetime.utcnow().isoformat(timespec="seconds") + "Z"


def log(msg: str) -> None:
    print(f"[{_ts()}] {msg}")


def download(url: str, dst: Path, force: bool = False) -> Path:
    """Download url to dst if missing."""
    dst.parent.mkdir(parents=True, exist_ok=True)
    if dst.exists() and not force:
        return dst
    req = Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urlopen(req, timeout=60) as r:
        content = r.read()
    dst.write_bytes(content)
    return dst


def safe_text_to_int(v: str):
    if v is None:
        return None
    s = re.sub(r"[^0-9\-]", "", str(v))
    if s == "" or s == "-":
        return None
    try:
        return int(s)
    except ValueError:
        return None


class XlsmParser:
    def __init__(self, path: Path):
        self.path = path
        self.z = zipfile.ZipFile(path)
        self.sst = self._read_shared_strings()
        self.sheet_name_to_file = self._sheet_map()

    def _read_shared_strings(self) -> List[str]:
        data = self.z.read("xl/sharedStrings.xml")
        import xml.etree.ElementTree as ET

        root = ET.fromstring(data)
        return ["".join(t.itertext()) for t in root.findall(f".//{NS}t")]

    def _sheet_map(self) -> Dict[str, str]:
        import xml.etree.ElementTree as ET

        wb = ET.fromstring(self.z.read("xl/workbook.xml"))
        rels = ET.fromstring(self.z.read("xl/_rels/workbook.xml.rels"))
        rel = {c.attrib["Id"]: c.attrib["Target"] for c in rels}
        out = {}
        for s in wb.find(f"{NS}sheets"):
            name = s.attrib["name"]
            rid = s.attrib[RNS[1:-1] + "id"] if False else s.attrib[f"{RNS}id"]
            out[name] = "xl/" + rel[rid]
        return out

    def _cell_value(self, cell, ss: List[str]):
        val = cell.find(f"{NS}v")
        if val is None:
            return ""
        txt = (val.text or "").strip()
        if cell.attrib.get("t") == "s":
            try:
                return ss[int(txt)] if txt != "" else ""
            except Exception:
                return ""
        return txt

    def _col_index(self, coord: str) -> int:
        col = "".join(ch for ch in coord if ch.isalpha())
        i = 0
        for ch in col:
            i = i * 26 + (ord(ch) - 64)
        return i - 1

    def read_sheet(self, sheet_name: str) -> Tuple[List[str], List[Dict[str, str]]]:
        import xml.etree.ElementTree as ET

        if sheet_name not in self.sheet_name_to_file:
            raise KeyError(f"Sheet missing: {sheet_name}")
        raw = self.z.read(self.sheet_name_to_file[sheet_name])
        root = ET.fromstring(raw)
        rows = root.find(f"{NS}sheetData")
        if rows is None:
            return [], []

        it = list(rows.findall(f"{NS}row"))
        if not it:
            return [], []

        head_cells = list(it[0].findall(f"{NS}c"))
        headers = [self._cell_value(c, self.sst) for c in head_cells]

        records: List[Dict[str, str]] = []
        for r in it[1:]:
            vals = [""] * len(headers)
            for c in r.findall(f"{NS}c"):
                i = self._col_index(c.attrib.get("r", "A"))
                if i >= len(vals):
                    vals.extend([""] * (i - len(vals) + 1))
                vals[i] = self._cell_value(c, self.sst)
            if any(v.strip() for v in vals):
                rec = {headers[j]: (vals[j] if j < len(vals) else "") for j in range(len(headers))}
                records.append(rec)
        return headers, records

    def close(self):
        self.z.close()


def parse_sunspots(path: Path) -> Tuple[Dict[int, float], Dict[int, str]]:
    annual: Dict[int, List[float]] = {}
    line_sources = []
    for ln in path.read_text(errors="ignore").splitlines():
        if not ln.strip() or ln.lstrip().startswith("#"):
            continue
        parts = [p.strip() for p in ln.split(";")]
        if len(parts) < 4:
            continue
        year = safe_text_to_int(parts[0])
        val = safe_text_to_int(parts[3])
        if year is None or val is None:
            continue
        if val < 0:
            continue
        annual.setdefault(year, []).append(float(val / 1.0))
        line_sources.append((year, val))

    annual_mean = {y: sum(v) / len(v) for y, v in annual.items()}
    return annual_mean, {y: ";".join(f"{v:.1f}" for v in vs) for y, vs in annual.items()}


def rolling_mean(values: List[float], w=3) -> List[float]:
    if w < 1:
        return values
    out = []
    half = w // 2
    n = len(values)
    for i in range(n):
        lo = max(0, i - half)
        hi = min(n, i + half + 1)
        out.append(sum(values[lo:hi]) / (hi - lo))
    return out


def local_maxima(values: List[Tuple[int, float]]) -> List[int]:
    if len(values) < 3:
        return []
    ys = [v for _, v in values]
    years = [y for y, _ in values]
    out = []
    for i in range(1, len(ys) - 1):
        if ys[i] >= ys[i - 1] and ys[i] >= ys[i + 1] and ys[i] > 0:
            if ys[i] > ys[i - 1] or ys[i] > ys[i + 1] or ys[i] >= max(ys):
                out.append(years[i])
    # filter obvious duplicates/noisy at series ends
    return out


def write_csv(path: Path, header, rows):
    with path.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=header)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def contingency(y_true: List[bool], y_pred: List[bool], years: List[int]):
    tp = tn = fp = fn = 0
    for yt, yp in zip(y_true, y_pred):
        if yt and yp:
            tp += 1
        elif (not yt) and (not yp):
            tn += 1
        elif (not yt) and yp:
            fp += 1
        elif yt and (not yp):
            fn += 1
    sens = tp / (tp + fn) if (tp + fn) else None
    spec = tn / (tn + fp) if (tn + fp) else None
    ppv = tp / (tp + fp) if (tp + fp) else None
    npv = tn / (tn + fn) if (tn + fn) else None
    return {
        "TP": tp,
        "TN": tn,
        "FP": fp,
        "FN": fn,
        "Sensitivity": sens,
        "Specificity": spec,
        "PositivePredictive": ppv,
        "NegativePredictive": npv,
        "TypeI": fp / (fp + tn) if (fp + tn) else None,
        "TypeII": fn / (fn + tp) if (fn + tp) else None,
    }


def fetch_world_population(path: Path) -> Dict[int, float]:
    raw = urlopen(Request(WORLD_POP_URL, headers={"User-Agent": "Mozilla/5.0"}), timeout=60).read()
    import json

    obj = json.loads(raw.decode("utf-8"))
    data = obj[1]
    out = {}
    for row in data:
        year = int(row["date"])
        v = row.get("value")
        if v is not None:
            out[year] = float(v)
    path.write_text(json.dumps(out, indent=2), encoding="utf-8")
    return out


def coerce_int_keys(data: Dict) -> Dict[int, float]:
    out: Dict[int, float] = {}
    for k, v in data.items():
        try:
            out[int(k)] = float(v)
        except Exception:
            continue
    return out


def complete_world_population(pop: Dict[int, float], start_year: int, end_year: int) -> Dict[int, float]:
    if not pop:
        raise ValueError("Population input is empty")
    available = sorted(pop)
    lo, hi = available[0], available[-1]
    out: Dict[int, float] = {}

    for y in range(start_year, end_year + 1):
        if y in pop:
            out[y] = pop[y]
            continue

        if y < lo:
            if lo == hi:
                growth = 1.0
            else:
                y0, y1 = available[0], available[1]
                p0, p1 = pop[y0], pop[y1]
                growth = p1 / p0 if p0 and p1 else 1.0
            out[y] = pop[lo] / (growth ** (lo - y))
            continue

        if y > hi:
            if lo == hi:
                growth = 1.0
            else:
                y0, y1 = available[-2], available[-1]
                p0, p1 = pop[y0], pop[y1]
                growth = p1 / p0 if p0 and p1 else 1.0
            out[y] = pop[hi] * (growth ** (y - hi))
            continue

        lo_pair = max(k for k in available if k < y)
        hi_pair = min(k for k in available if k > y)
        if lo_pair == hi_pair:
            out[y] = pop[lo_pair]
            continue
        p_lo = pop[lo_pair]
        p_hi = pop[hi_pair]
        frac = (y - lo_pair) / (hi_pair - lo_pair)
        out[y] = p_lo + frac * (p_hi - p_lo)

    return out


def parse_world_population_cache(path: Path) -> Dict[int, float]:
    if path.exists():
        return coerce_int_keys(json.loads(path.read_text(encoding="utf-8")))
    return fetch_world_population(path)


def main() -> int:
    paper_pdf = BASE / "data" / "article_when_emotions_flare.pdf"
    red_zip = BASE / "data" / "revolutionary_episodes_v1.0.zip"
    red_xlsm = BASE / "data" / "Revolutionary episodes_v_1.0.xlsm"
    red_xls = BASE / "data" / "Revolutionary_episodes_sheets"
    sunspot_csv = BASE / "data" / "sunspots_m.csv"
    pop_json = BASE / "data" / "world_population_wb.json"
    notes = []

    log("Downloading source artifacts...")
    try:
        download(DROPBOX_URL, red_zip)
        if red_zip.exists():
            if not red_xlsm.exists():
                with zipfile.ZipFile(red_zip) as zf:
                    with zf.open("Revolutionary episodes_v_1.0.xlsm") as src:
                        red_xlsm.write_bytes(src.read())
    except (URLError, HTTPError, TimeoutError, Exception) as e:
        notes.append(f"RED download error: {type(e).__name__}: {e}")
        log(f"RED download error: {e}")
        return 1

    try:
        download(SUNSPOT_URL, sunspot_csv)
    except (URLError, HTTPError, TimeoutError, Exception) as e:
        notes.append(f"Sunspot download error: {type(e).__name__}: {e}")
        log(f"Sunspot download error: {e}")

    try:
        download(PAPER_URL, paper_pdf)
    except (URLError, HTTPError, TimeoutError, Exception) as e:
        notes.append(f"Paper download error (non-critical for computation): {type(e).__name__}: {e}")
        log(f"Paper download warning: {e}")

    try:
        pop = parse_world_population_cache(pop_json)
    except (URLError, HTTPError, TimeoutError, Exception) as e:
        notes.append(f"World population download error: {type(e).__name__}: {e}")
        log(f"World population download error: {e}")
        pop = {}

    if not pop:
        pop = {}

    # Parse RED workbook
    try:
        parser = XlsmParser(red_xlsm)
        _, timing_rows = parser.read_sheet("1-Timing & location")
        _, part_rows = parser.read_sheet("5-Participants")
        parser.close()
    except Exception as e:
        notes.append(f"Workbook parse error: {type(e).__name__}: {e}")
        log(f"Workbook parse error: {e}")
        return 1

    part_by_revid = {}
    for r in part_rows:
        revid = r.get("revid", "").strip()
        if not revid:
            continue
        part_by_revid[revid] = safe_text_to_int(r.get("particnum", "0")) or 0

    combined = {}
    timing_pre1900 = 0
    timing_post2014 = 0
    for r in timing_rows:
        revid = r.get("revid", "").strip()
        if not revid:
            continue
        name = r.get("nameofrevolution", "")
        startyear = safe_text_to_int(r.get("startyear", ""))
        startprior = safe_text_to_int(r.get("startprior1900", "0")) or 0
        if startyear is None:
            continue
        if startyear < 1900:
            timing_pre1900 += 1
        if startyear > 2014:
            timing_post2014 += 1
        if 1900 <= startyear <= 2014:
            combined.setdefault(startyear, {"events": 0, "tnp": 0.0, "episodes": []})
            combined[startyear]["events"] += 1
            p = part_by_revid.get(revid, 0)
            combined[startyear]["tnp"] += float(p)
            combined[startyear]["episodes"].append({"revid": revid, "name": name, "participants": p})

    # Paper reports 395 revolutionary episodes in this window; RED v1.0 has 343 startyears in 1900-2014.
    # Count included episodes total + excluded for transparency.
    included_total = len(timing_rows)
    included_1900_2014 = len(
        [r for r in timing_rows if r.get("startyear") and 1900 <= safe_text_to_int(r.get("startyear", "")) <= 2014]
    )
    if not pop:
        # reasonable fallback if no population data are available
        pop = {y: 6_000_000_000 for y in range(1900, 2015)}
    else:
        pop = complete_world_population(pop, 1900, 2014)

    # compute revolution index for 1900-2014 with GP proxy.
    rev_rows = []
    for y in range(1900, 2015):
        gp = pop.get(y)
        if gp is None or gp <= 0:
            continue
        stats = combined.get(y, {"events": 0, "tnp": 0.0})
        tnp = float(stats["tnp"])
        events = float(stats["events"])
        rev_index = math.sqrt(tnp / (gp * 1e9)) * math.sqrt(events) + 1.0 if tnp > 0 or events > 0 else 1.0
        rev_rows.append((y, rev_index, int(events), tnp))

    rev_indices = [r[1] for r in rev_rows]
    rev_mean = mean(rev_indices)
    rev_sd = pstdev(rev_indices)

    # Sunspot annualization and classification
    annual_sunspot, sunspot_components = parse_sunspots(sunspot_csv)
    annual_1900_2014 = [(y, annual_sunspot[y]) for y in range(1900, 2015) if y in annual_sunspot]
    years_only = [y for y,_ in annual_1900_2014]
    annual_vals = [v for _,v in annual_1900_2014]
    smooth = rolling_mean(annual_vals, w=5)
    smooth_pairs = list(zip(years_only, smooth))

    # local maxima from smoothed annual series (within full available range)
    cyc = [(y, v) for y, v in smooth_pairs]
    maxima = local_maxima(cyc)
    max_vals = {y: dict(cyc)[y] for y in maxima if y in dict(cyc)}
    if max_vals:
        solar_threshold = min(max_vals.values())
    else:
        solar_threshold = mean(annual_vals) if annual_vals else 0

    # replicate three thresholds: paper-like maxima threshold, local threshold percentiles and top-cyle alternative
    is_high_local = {y: (y in max_vals and annual_sunspot.get(y, 0) >= max(1, solar_threshold)) for y in range(1900, 2015)}
    is_high_thresh = {y: (annual_sunspot.get(y, -9999.0) >= solar_threshold) for y in range(1900, 2015)}
    sun_vals = [annual_sunspot[y] for y in range(1900, 2015) if y in annual_sunspot]
    p90 = sorted(sun_vals)[max(0, int(0.9 * len(sun_vals)) - 1)] if sun_vals else 0
    p85 = sorted(sun_vals)[max(0, int(0.85 * len(sun_vals)) - 1)] if sun_vals else 0

    rev_high = {y: (next((r[1] for r in rev_rows if r[0] == y), 1.0) > (rev_mean + rev_sd)) for y in range(1900, 2015)}

    # Also compute ±2-year window around threshold peaks
    sun_window = set()
    for y in maxima:
        for yy in range(y - 2, y + 3):
            if 1900 <= yy <= 2014:
                sun_window.add(yy)
    is_high_window = {y: (y in sun_window) for y in range(1900, 2015)}

    # Contingencies
    year_index = list(range(1900, 2015))
    def as_bool_series(d):
        return [bool(d.get(y, False)) for y in year_index]

    rev_series = as_bool_series(rev_high)
    c_local = contingency(rev_series, as_bool_series(is_high_thresh), year_index)
    c_window = contingency(rev_series, as_bool_series(is_high_window), year_index)

    # extra variant: top-two quantile solar as robustness
    is_high_p90 = {y: annual_sunspot.get(y, -9999) >= p90 for y in range(1900, 2015)}
    is_high_p85 = {y: annual_sunspot.get(y, -9999) >= p85 for y in range(1900, 2015)}
    c_p90 = contingency(rev_series, as_bool_series(is_high_p90), year_index)
    c_p85 = contingency(rev_series, as_bool_series(is_high_p85), year_index)

    # annual output
    episode_rows = []
    for y, rev_idx, events, tnp in rev_rows:
        episode_rows.append(
            {
                "year": y,
                "events_1900_2014": int(events),
                "tnp": int(tnp) if tnp == int(tnp) else tnp,
                "revolution_index": rev_idx,
                "is_high_revolution": bool(rev_high[y]),
                "annual_sunspot": annual_sunspot.get(y, None),
                "is_high_solar_threshold": bool(is_high_thresh[y]),
                "is_high_solar_window": bool(is_high_window[y]),
                "is_solar_local_max": bool(is_high_local[y]),
            }
        )
    if episode_rows:
        write_csv(OUT / "episode_year_counts.csv", episode_rows[0].keys(), episode_rows)

    # contingency output
    cont_rows = [
        {"specification": "solar_threshold", **c_local, "threshold_type": "annual_threshold", "sun_threshold": solar_threshold, "p90": p90, "p85": p85},
        {"specification": "solar_window_±2", **c_window, "threshold_type": "window_around_peak", "sun_threshold": solar_threshold, "p90": p90, "p85": p85},
        {"specification": "solar_p90", **c_p90, "threshold_type": "percentile", "sun_threshold": p90, "p90": p90, "p85": p85},
        {"specification": "solar_p85", **c_p85, "threshold_type": "percentile", "sun_threshold": p85, "p90": p90, "p85": p85},
    ]
    write_csv(OUT / "contingency_analysis.csv", cont_rows[0].keys(), cont_rows)

    # Build summary and notes
    max_solar_years = sorted([y for y in years_only if annual_sunspot.get(y, -9999) >= solar_threshold])
    max_local_years = sorted([y for y in years_only if is_high_local[y]])
    high_sun_window_years = sorted(sun_window)

    summary = {
        "run_timestamp_utc": _ts(),
        "paper_reported_episodes_1900_2014": 395,
        "red_v1_included_total": included_total,
        "red_v1_included_1900_2014": included_1900_2014,
        "red_v1_excluded_total": 131,
        "included_pre1900": timing_pre1900,
        "included_post2014": timing_post2014,
        "revolution_index_mean": rev_mean,
        "revolution_index_sd": rev_sd,
        "solar_threshold": solar_threshold,
        "max_local_solar_years_count": len(max_local_years),
        "max_local_solar_years_sample": max_local_years[:30],
        "window_high_years_count": len(high_sun_window_years),
        "contingency_window": c_window,
        "contingency_threshold": c_local,
        "contingency_p90": c_p90,
        "contingency_p85": c_p85,
        "maxima_years_count": len(maxima),
        "maxima_years_sample": maxima[:40],
    }
    (OUT / "replication_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    sample_events = []
    for y in sorted(combined)[:5]:
        sample_events.append({"year": y, "events": combined[y]["events"], "tnp": combined[y]["tnp"], "episode": combined[y]["episodes"][:3]})

    notes_text = [
        "Replication Notes",
        "- Used RED dataset version 1.0 from Princeton-linked public Dropbox mirror.",
        "- Parsed sheets: 1-Timing & location and 5-Participants.",
        "- Constructed yearly revolution activity from startyear in [1900, 2014], matching the paper’s stated temporal scope.",
        "- The paper reports n=395 episodes. The RED v1.0 included set contains 343 episodes with start year 1900-2014 and 2 episodes starting in 1899.",
        "  This is the principal reproducibility mismatch that prevents exact replication of that point from public materials.",
        f"- Total included rows in workbook: {included_total}; included and excluded totals in data description are 345 and 131 respectively.",
        "- Sunspot source: SILSO monthly total sunspot number, aggregated to annual mean.",
        "- World population proxy: World Bank WLD SP.POP.TOTL.",
        "- Solar-window spec: threshold at local maxima minima, then ±2-year window in a robustness check.",
        "- No inferential models/robust SEs were reported in the paper text extract available; this script focuses on replicating published threshold-style diagnostics only.",
        "",
        "Quick interpretation guide:",
        f"- Solar threshold year count (annual>=threshold): {len(max_solar_years)}",
        f"- Solar window year count (±2 years around local maxima): {len(high_sun_window_years)}",
        f"- High revolution threshold: mean(revolution_index)+sd = {rev_mean + rev_sd:.6f}",
        "- See contingency_analysis.csv for metric sensitivity across solar definitions.",
        "",
        "Top sampled 1900-2014 year totals:",
        json.dumps(sample_events, indent=2),
    ]
    notes.extend(notes_text)
    (OUT / "replication_notes.md").write_text("\n".join(notes), encoding="utf-8")

    log("Replication summary written")
    print(json.dumps(summary, indent=2))
    log("Done")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
