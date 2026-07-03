# Solar Revolutions

Public, reusable data and methods for evaluating whether solar activity is associated with revolutionary episodes.

This repository separates three scopes:

1. **Paper-scoped replication**: RED 1.0 revolutionary episodes and SILSO sunspot activity.
2. **Paper-scoped follow-on statistics**: RED/SILSO correlations, lag scans, sensitivity grids, split-sample checks, and solar-cycle influence checks.
3. **Expanded-input follow-on research**: country-year exposure, local geomagnetic/radiation proxies, controls, alternative predictors, and event-history diagnostics.

## Use it

- Public page: <https://castaliainstitute.github.io/solar-revolutions/>
- Revolutions Colab notebook: <https://colab.research.google.com/github/CastaliaInstitute/solar-revolutions/blob/main/solar_revolutions_methods_results_colab.ipynb>
- Solar-inflation mechanisms Colab notebook: <https://colab.research.google.com/github/CastaliaInstitute/solar-revolutions/blob/main/solar_inflation_mechanisms_colab.ipynb>
- Astrology-input correlation Colab notebook: <https://colab.research.google.com/github/CastaliaInstitute/solar-revolutions/blob/main/astrology_input_correlations_colab.ipynb>
- All-vs-all input correlation Colab notebook: <https://colab.research.google.com/github/CastaliaInstitute/solar-revolutions/blob/main/all_vs_all_input_correlations_colab.ipynb>
- Data artifacts: [`api/`](api/)

## Key data files

- `api/red/annual-summary.json`: RED annual revolution summary.
- `api/input-data/climate_solar_activity.json`: SILSO monthly sunspot activity.
- `api/red/primary-specificity-endpoint.json`: headline specificity endpoint and sensitivity grids.
- `api/red/solar-shape-synchrony.json`: RED/SILSO shape, lag, phase, and event-study diagnostics.
- `api/red/country-panel-solar-model.json`: country-year exposure and fixed-effect diagnostics.
- `api/red/science-review-comparative-evidence.json`: expanded-input comparison against alternative predictors.
- `api/red/pca-ml-prediction.json`: PCA/ridge screens for all-input RED prediction and SILSO predicting each non-solar input.

## Current conclusion

The paper-style RED/SILSO relationship is reproducible and browsable, and the narrow exact-solar-maximum rule has high specificity. It is not sufficient evidence of causal solar influence or operational prediction. Stronger country-year and expanded-input tests remain exploratory / non-confirmatory.

## Exploratory SILSO-to-input finding

In the current one-predictor screen, SILSO solar activity most usefully predicts Shiller annual inflation among the displayed inputs: held-out `r ≈ +0.501`, held-out `R² ≈ +0.234`, and same-year `r ≈ +0.274`. This is a mechanism/confounding candidate, not causal proof. It should be followed up with lag tests, inflation controls in revolution models, placebo cycles, and non-U.S. price series before it is used to support the solar-revolution hypothesis. The new `solar_inflation_mechanisms_colab.ipynb` notebook starts that follow-up.


## Current falsification readout for solar-inflation

The solar-inflation hypothesis is currently substantially weakened. SILSO remains the strongest one-input predictor of Shiller annual inflation and beats shifted/synthetic placebo cycles, but it fails two stricter checks: it does not generalize to the available non-Shiller inflation outcomes, and rolling-origin validation is unstable with only 2 of 7 positive-R² windows and median rolling R² around -0.394.


## Astrology-input correlation screen

The `astrology_input_correlations_colab.ipynb` notebook answers whether catalog inputs correlate with the exploratory astrology proxies. It reports same-year Pearson/Spearman correlations, lag scans, astrology-family summaries, and circular-shift placebo checks so any apparent association is treated as exploratory rather than causal.


Current astrology-correlation readout: 528 same-year pairs were screened. The strongest raw pair was Uranus-Pluto hard-aspect proximity vs NAVCO injury proxy (`r=0.637`, `n=23`), but it did not beat its own circular-shift placebo at `p<0.05`. Seven of the top 25 raw pairs did beat circular-shift placebo; these are exploratory candidates only.


## All-vs-all correlation screen

The `all_vs_all_input_correlations_colab.ipynb` notebook computes pairwise correlations across all usable input series. Current run: 93 usable annual series and 4,030 same-year pairs. The raw leaders are mostly duplicate or same-construct measurements, so the notebook includes a deduplicated cross-module view for discovery.
