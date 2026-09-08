# Methods summary

## RQ1: exposed-classified vs comparison-classified regions

RQ1 uses all six regions from 2011-2024. Annual group means are provided for descriptive trend plotting. For the primary between-group comparison, each region is first reduced to its 2011-2024 mean, leaving three exposed-classified regional means and three comparison-classified regional means. Welch's t-test is reported only as an exploratory small-sample comparison; with three regions per group, inference is necessarily weak.

## RQ2: PCA only in exposed-classified regions

RQ2 uses 42 region-year observations from East Kazakhstan+Abay, Karaganda, and Pavlodar.

Predictors:

- cancer morbidity
- infant mortality
- circulatory-disease morbidity
- registered disability
- unemployment

Observed outcome:

- crude all-cause mortality percentage

### PCA suitability

The predictor correlation matrix is evaluated with overall and variable-specific KMO statistics and Bartlett's test of sphericity. Because annual observations are repeated within regions, Bartlett's conventional p-value is treated as approximate.

### Standardization and PCA

Predictors are standardized with z-scores. PCA is fit to the five standardized predictors only; mortality is excluded. PC1 and PC2 are retained for the reduced specification.

### OLS models

Original-indicator model:

`Mortality ~ 5 original indicators + centered linear year trend + region fixed effects`

PCA-reduced model:

`Mortality ~ PC1 + PC2 + centered linear year trend + region fixed effects`

East Kazakhstan+Abay is the reference region. HC3 covariance estimates are used for standard errors, confidence intervals, and p-values. HC3 does not solve serial correlation from repeated observations within only three regions; coefficient inference remains exploratory.

### Model comparison

The models are compared using R-squared, adjusted R-squared, RMSE, AIC, and BIC. These are in-sample metrics. Lower RMSE/AIC/BIC is preferred; higher R-squared/adjusted R-squared is preferred.
