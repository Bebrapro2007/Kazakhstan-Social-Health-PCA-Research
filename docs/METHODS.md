# Methods summary

## RQ1: regional comparison

The main analysis uses six regions during 2011-2024 (84 region-year rows). Each region is first reduced to its arithmetic mean over the selected period. Group means give equal weight to the three regional means in each project class; annual rows are not independent geographic units. The five manuscript indicators are cancer morbidity, infant mortality, circulatory-disease morbidity, registered disability, and unemployment. Mortality is also exported as a supplementary descriptive comparison.

The manuscript's exploratory two-sided exact permutation check enumerates all 20 ways to assign three of the six regional means to the exposed-classified group. The statistic is the exposed-minus-comparison mean difference; the p-value is the fraction of allocations with an absolute difference at least as large as observed, including the observed allocation. A numerical tolerance includes equal statistics. Labels were not randomized, so these p-values do not establish a radiation effect. Welch statistics remain in the CSV as secondary diagnostics and are not the manuscript's exact p-values.

## RQ2: exposed-only PCA and mortality models

The main sample contains 42 observations from East Kazakhstan+Abay, Karaganda, and Pavlodar. Crude all-cause mortality is registered deaths / project population x 100, on a numeric percentage scale. Mortality never enters PCA.

The five predictors are standardized within the exposed-only sample using population-standard-deviation z-scores. PCA is fit to those five columns. Overall and variable-specific KMO statistics and Bartlett's test describe suitability; Bartlett's conventional p-value assumes independent rows and is approximate for this repeated-region panel. PC1 and PC2 are retained. Component signs are fixed for reproducible interpretation: the infant-mortality coefficient is positive on PC1 and the disability coefficient positive on PC2. This changes neither explained variance nor OLS fitted values.

Three OLS models use the same observations and controls:

1. Baseline: `Mortality ~ Region + Year`.
2. Original-indicator: `Mortality ~ 5 original indicators + Region + Year`.
3. PCA-reduced: `Mortality ~ PC1 + PC2 + Region + Year`.

Each specification includes an intercept, a centered linear year trend, and Karaganda/Pavlodar indicators, with East Kazakhstan+Abay as the reference. The models contain 4, 9, and 6 fitted parameters respectively, including the intercept. Year is a linear trend, not a set of year fixed effects. HC3 covariance is used for coefficient standard errors, confidence intervals, and p-values. It does not change fitted values or solve serial correlation within the three regions.

Comparison uses in-sample R-squared, adjusted R-squared, RMSE, AIC, and BIC. RMSE is `sqrt(mean(residual**2))` in mortality percentage points, without a degrees-of-freedom adjustment. AIC/BIC use the ordinary Gaussian OLS likelihood. These metrics are not out-of-sample forecasting evidence.

## Pre-2022 boundary sensitivity

Repeat both analyses on 2011-2021, before the 2022 administrative reforms: 66 all-region rows and 33 exposed-region rows. RQ1 recalculates six regional means and all 20 permutation allocations. RQ2 refits the scaler, all five principal components, diagnostics, and all three OLS models entirely within the 33-row sample; the full-period PCA is not reused. Year is centered within each sample.

This period restriction checks sensitivity to the project boundary treatment; it does not reconstruct missing denominators or establish complete geographic harmonization. AIC/BIC comparisons are meaningful between models fitted to the same sample. Do not compare their absolute values across the full and shorter periods.

## Reproduction and consistency checks

`analysis/run_analysis.py` regenerates tables. `analysis/export_workbook.py` writes the same full-precision values to `results/research_results.xlsx` using public Python dependencies. `analysis/make_figures.py` plots the CSV values and embeds their source hashes in the PNG files. `analysis/verify_results.py` checks manuscript precision, independently reconstructed model fits, CSV/Excel agreement, and figure source hashes. Rounded display values are not used as analytical inputs.
