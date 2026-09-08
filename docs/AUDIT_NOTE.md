# Audit note: mortality correction before GitHub release

During repository preparation, the exposed-only working dataset from the earlier PCA/OLS rerun was checked against the supplied official deaths workbook.

The working file contained a mortality series for 2011-2021 that did not equal:

`registered deaths / project population x 100`

For example, East Kazakhstan+Abay 2011 had been carried as approximately 0.7316% in the legacy exposed-only working file, whereas the supplied registered death counts and project population denominator yield approximately 1.1928%.

The repository therefore rebuilds observed mortality for **every region-year** from registered deaths and the project population denominator before running RQ1 or RQ2.

## Geographic rule used for death counts

- East Kazakhstan+Abay: East Kazakhstan deaths + Abay deaths for all study years.
- Karaganda: Karaganda + Ulytau deaths for 2011-2021, then Karaganda deaths alone for 2022-2024, matching the population series used by the project after the administrative split.
- Pavlodar: Pavlodar deaths.
- Akmola: Akmola deaths.
- Almaty Region: Almaty Region deaths.
- Kostanay: Kostanay deaths.

This correction materially changes the exposed-only OLS model comparison. The repository results supersede the earlier exposed-only model output.

## Current RQ2 comparison after correction

| Metric | Before PCA | After PCA |
|---|---:|---:|
| R-squared | 0.3112 | 0.2639 |
| Adjusted R-squared | 0.1443 | 0.1617 |
| RMSE | 0.0887 | 0.0917 |
| AIC | -66.27 | -69.48 |
| BIC | -50.63 | -59.05 |

Do not mix these values with the earlier exposed-only results.
