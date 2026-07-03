# Critical Review: "When Emotions Flare: Solar Rhythms, emotions and cycles of political revolution"

## 1) Replication target and scope
- Target source: https://digitalrepository.unm.edu/geog_fsp/3
- Period target from abstract: 1900–2014
- Core claim to reproduce: 395 revolutionary episodes and a clustering around solar maxima
- Our run used RED Episode Dataset v1.0 (public Princeton mirror), SILSO monthly sunspot means, and the script-based annualized revolution-index proxy.

## 2) What was successfully reproduced
- Data extraction pipeline is runnable and outputs are reproducible in this repo.
- Solar proxy construction was replicated (annual mean from SILSO monthly values; smoothed and local-max detection).
- Event aggregation by start year for [1900, 2014] is functioning.

## 3) Critical reproducibility gap
- Paper-reported episodes in period: 395 (from abstract and repository landing page)
- Public RED v1.0 start-year episodes in [1900, 2014]: 343
- Total included rows in parsed timing sheet: 345 (2 start in 1899, 0 post-2014)
- This is a substantial discrepancy of 52 episodes and cannot be closed from the current public bundle/metadata we have access to.

## 4) Replication outputs (from this run)
- Output directory: `/solar-revolutions/outputs`
- `replication_summary.json`: `red_v1_included_1900_2014 = 343`, `paper_reported_episodes_1900_2014 = 395`.
- `contingency_analysis.csv` contains 4 specs (annual threshold, ±2-year window, p90, p85).
- Best matching overlap under this reconstruction:
  - Solar window: TP 12, TN 61, FP 38, FN 4, Sensitivity 0.75, Specificity 0.616
  - Solar threshold at local maxima level: TP 13, TN 62, FP 37, FN 3, Sensitivity 0.8125, Specificity 0.626
- These are directional diagnostics only; they do not reproduce the full inferential setup of the paper because full-text methods are not accessible in the current environment.

## 5) Methodological risks (important)
- Full text and data construction details behind the paper’s model are inaccessible (PDF endpoint returns 403 in this environment), so key choices could differ from our implementation.
- Revolution intensity measure is highly sensitive to normalization choices; without the exact definition, “high revolution” year identification is uncertain.
- The reproduction assumes start-year only from RED, which is less granular than possible event-span treatment.
- Solar/earth-physics mapping choices (smoothing window, maxima detection, classification thresholding) can materially alter associations.

## 6) Overall assessment
- Partial replication is possible and transparent, but the headline findings are not fully reproduced from this article’s declared public sources alone.
- The dominant blocker is an unresolved data definition mismatch (395 vs 343 episodes) plus unavailable full-text methods.

## 7) Notebook confirmation verdict
- The Jupyter notebook reproduces the full stated workflow in this repository (data pulls, preprocessing, sunspot treatment, and overlap/calibration calculations) and is rerunnable.
- It does **not** fully confirm the paper's reported results because the public RED v1.0 reconstruction available in this environment does not match the paper’s 395 episodes (it yields 343 for 1900–2014).
- Therefore, the result is documented as a **partial replication** with explicit gaps, not a definitive confirmation.
