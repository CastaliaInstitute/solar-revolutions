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
