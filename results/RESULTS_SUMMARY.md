# Results summary

## RQ1 - group comparison

Primary group comparisons are based on six regional means (three regions per project group), not 84 independent rows.

| Indicator | Exposed mean | Comparison mean | Difference | Welch p (region means) |
|---|---:|---:|---:|---:|
| Cancer morbidity (%) | 0.2932 | 0.2259 | +0.0673 | 0.2700 |
| Infant mortality (%) | 0.8715 | 0.9162 | -0.0447 | 0.6925 |
| Circulatory morbidity (%) | 2.6673 | 2.4730 | +0.1943 | 0.5292 |
| Registered disability (%) | 4.1861 | 3.9418 | +0.2443 | 0.6867 |
| Unemployment (%) | 4.8362 | 4.8857 | -0.0496 | 0.5412 |
| Crude all-cause mortality (%) | 1.0523 | 0.9407 | +0.1116 | 0.4879 |

These p-values are exploratory because there are only three independent regions in each group.

## RQ2 - exposed-only PCA

- N = 42 region-year rows from 3 exposed-classified regions.
- Overall KMO = 0.5099.
- Bartlett chi-square(10) = 75.5632, p < 0.001 (conventional reference distribution).
- PC1 explained variance = 49.18%.
- PC2 explained variance = 26.03%.
- PC1 + PC2 cumulative variance = 75.21%.

### Model comparison

| Metric | Before PCA | After PCA |
|---|---:|---:|
| R-squared | 0.3112 | 0.2639 |
| Adjusted R-squared | 0.1443 | 0.1617 |
| RMSE | 0.0887 | 0.0917 |
| AIC | -66.27 | -69.48 |
| BIC | -50.63 | -59.05 |

Interpretation: the five-indicator model has higher raw in-sample R-squared and slightly lower RMSE, while the two-component model is more parsimonious and has better AIC/BIC and slightly higher adjusted R-squared.
