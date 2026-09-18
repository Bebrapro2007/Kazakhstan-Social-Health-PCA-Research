# Results summary

## RQ1: six regional means

Annual observations are first averaged within each region. The manuscript compares five indicators using three regional means per group. Exact p-values enumerate all 20 possible allocations; labels were not randomized and the checks remain exploratory. Welch results are exported only as secondary diagnostics.

| Indicator | Exposed mean | Comparison mean | Difference | Exact p |
|---|---:|---:|---:|---:|
| Cancer morbidity | 0.2932 | 0.2259 | +0.0673 | 0.20 |
| Infant mortality | 0.8715 | 0.9162 | -0.0447 | 0.60 |
| Circulatory morbidity | 2.6673 | 2.4730 | +0.1943 | 0.60 |
| Registered disability | 4.1861 | 3.9418 | +0.2443 | 0.80 |
| Unemployment | 4.8362 | 4.8857 | -0.0496 | 0.50 |

## RQ2: 42 exposed region-year rows

Overall KMO = 0.5099; disability KMO = 0.216. Bartlett chi-square(10) = 75.5632, conventional p < 0.001. PC1 explains 49.18%, PC2 26.03%, total 75.21%. Mortality is excluded from PCA.

| Model | Parameters | R-squared | Adjusted R-squared | RMSE | AIC | BIC |
|---|---:|---:|---:|---:|---:|---:|
| Baseline: region + year | 4 | 0.0840 | 0.0116 | 0.1023 | -64.29 | -57.34 |
| Original-indicator | 9 | 0.3112 | 0.1443 | 0.0887 | -66.27 | -50.63 |
| PCA-reduced | 6 | 0.2639 | 0.1617 | 0.0917 | -69.48 | -59.05 |

Both predictor models improve on baseline in-sample fit. The original model has better raw R-squared/RMSE; PCA has the best adjusted R-squared/AIC/BIC.

## 2011-2021 sensitivity

The shorter-period RQ1 differences are cancer +0.0619, infant mortality -0.0251, circulatory morbidity +0.1264, disability +0.0646, unemployment -0.0182. The disability difference shrinks substantially.

Refitting exposed-only standardization/PCA on 33 rows gives KMO 0.493. The original model has R-squared 0.5015 and RMSE 0.0782; PCA has R-squared 0.4714 and RMSE 0.0805 and lower AIC/BIC. All three shorter-period models and complete diagnostics are exported in CSVs and Excel. Compare model criteria within each sample.

All values above follow manuscript rounding. Full-precision data underpin the workbook and figures. `analysis/verify_results.py` checks the recorded final manuscript targets and artifact consistency.
