# Solar-Revolutions Reproducibility Pack

This folder contains a reproducibility attempt for:

- Andreas Hernandez et al., “When Emotions Flare: Solar Rhythms, emotions and cycles of political revolution” (2025)
- DOI/landing: https://digitalrepository.unm.edu/geog_fsp/3

Goal
- Reproduce core claims with public materials and make every step explicit:
  - 395-episode sample used in the paper vs public RED v1.0 (345 included + 131 excluded)
  - yearly revolution-index construction
  - high-solar/high-revolution overlap and contingency-style performance metrics
  - reproducibility gap log

Requirements
- Python 3.10+
- `requests`, `numpy`, `pandas` (optional for extended plotting)

Run
- `python reproduce_solar_revolution_analysis.py`

Outputs
- `outputs/replication_summary.json`
- `outputs/episode_year_counts.csv`
- `outputs/contingency_analysis.csv`
- `outputs/replication_notes.md`

Dashboard ingest
- Source archive: `data/revolutionary_episodes_v1.0.zip`
- Browser export: `python scripts/build_red_browser.py`
- Public browser JSON:
  - `dashboard/public/api/red/manifest.json`
  - `dashboard/public/api/red/episodes.json`
  - `dashboard/public/api/red/annual-summary.json`
- App route: `/red`

Google Colab
- Use `solar_revolutions_repro.ipynb` directly in Colab.
- In Colab, set `SOLAR_REPO_ROOT` to your notebook checkout path, or clone this repo into `/content/solar-revolutions`.
- The notebook auto-detects `/content/solar-revolutions`, local repo roots, and current working directory, and writes to `outputs/` under the detected root.

How to use data
- The script downloads:
- Paper PDF from UNM Digital Commons
- RED v1.0 dataset archive from the public Dropbox link on Princeton page via Discuss Data metadata
  - Monthly smoothed sunspot data from SIDC SILSO (if available)

Notes
- This workflow is intentionally conservative and logs any missing/recoverable assumptions.
- It should be rerunnable without edits.

Status of notebook confirmation
- The Jupyter notebook reproduces the public-data pipeline and outputs, but it does **not** fully confirm the paper's headline result from public sources alone.
- The public RED v1.0 reconstruction used in the notebook yields 343 episodes for 1900–2014 versus the paper-reported 395, leaving a 52-episode unresolved gap.
- As a result, the notebook supports a **partial, transparent replication** rather than full validation of the paper's claimed episode counts and exact model behavior.

- critical_review.md
