# Kazakhstan Regional Health Indicators and PCA (2011-2024)

Reproducible research repository for an exploratory ecological panel study of regional health and socioeconomic indicators in Kazakhstan.

## Research design

**RQ1 - regional comparison.** Compare three project-classified exposed regions (East Kazakhstan+Abay, Karaganda, Pavlodar) with three comparison-classified regions (Akmola, Almaty Region, Kostanay). The 2011-2024 panel has 84 region-year rows. Comparisons first average each region over time, leaving six independent geographic units. The manuscript reports an exploratory exact two-sided permutation check over all 20 allocations of three regions to each group. The existing Welch statistics are retained only as secondary diagnostics.

**RQ2 - PCA and mortality models.** Use the 42 rows from the three exposed-classified regions. Standardize five predictors and retain PC1 and PC2. Crude all-cause mortality is the observed outcome, calculated as registered deaths / population x 100, and never enters PCA. Compare three OLS specifications with an intercept, centered linear year trend, and region fixed effects:

1. Baseline: `Mortality ~ Region + Year`.
2. Original-indicator: `Mortality ~ 5 indicators + Region + Year`.
3. PCA-reduced: `Mortality ~ PC1 + PC2 + Region + Year`.

HC3 covariance estimates provide coefficient standard errors and p-values. They do not change fitted mortality or correct serial correlation within a region.

## Audited full-period results

| Model | N | Parameters | R-squared | Adjusted R-squared | RMSE | AIC | BIC |
|---|---:|---:|---:|---:|---:|---:|---:|
| Baseline | 42 | 4 | 0.0840 | 0.0116 | 0.1023 | -64.29 | -57.34 |
| Original-indicator | 42 | 9 | 0.3112 | 0.1443 | 0.0887 | -66.27 | -50.63 |
| PCA-reduced | 42 | 6 | 0.2639 | 0.1617 | 0.0917 | -69.48 | -59.05 |

PCA diagnostics: overall KMO **0.5099**; Bartlett chi-square(10) **75.5632**, conventional p < 0.001; PC1 **49.18%**, PC2 **26.03%**, total **75.21%** explained variance. Disability KMO is **0.216**. Suitability is weak and the components remain exploratory.

Both predictor models improve on the baseline. The original-indicator model has higher raw R-squared and lower RMSE; the PCA model has the best adjusted R-squared, AIC, and BIC. All metrics are in-sample, and RMSE uses mortality percentage points. CSV and Excel values retain full precision; this page follows manuscript rounding.

## Pre-2022 boundary sensitivity

Repeat RQ1 and RQ2 on **2011-2021**, retaining 66 all-region rows and 33 exposed-region rows. Recalculate regional means and exact permutation checks. Refit standardization, PCA, and all three mortality models within the shorter sample.

| RQ1 exposed-minus-comparison difference | 2011-2024 | 2011-2021 |
|---|---:|---:|
| Cancer morbidity | +0.0673 | +0.0619 |
| Infant mortality | -0.0447 | -0.0251 |
| Circulatory morbidity | +0.1943 | +0.1264 |
| Registered disability | +0.2443 | +0.0646 |
| Unemployment | -0.0496 | -0.0182 |

For 2011-2021, the original-indicator model has R-squared **0.5015**, RMSE **0.0782**; the PCA model has R-squared **0.4714**, RMSE **0.0805**, and lower AIC/BIC. KMO is **0.493**. The disability group difference shrinks substantially. See the boundary sensitivity CSVs, workbook tabs, and `figures/rq1_boundary_sensitivity.png` / `figures/rq2_boundary_sensitivity.png` for all computed results, including the shorter-period baseline. Compare AIC/BIC within a sample, not across different periods.

## Data audit

An earlier working file's 2011-2021 mortality series did not match registered deaths / population x 100. This repository uses the audited mortality series for every region-year. The 2011-2021 restriction checks the effect of the project boundary treatment; it does not fully harmonize all post-2022 rate denominators. See `docs/AUDIT_NOTE.md` and `docs/METHODS.md`.

## Repository structure

```text
README.md, CITATION.cff, requirements.txt
analysis/     # calculations, workbook export, figures, verification
data/source/  # supplied statistical workbooks and legacy provenance files
data/processed/  # audited analytical CSV datasets
results/tables/  # full-period and pre-2022 CSV outputs
results/research_results.xlsx
figures/      # generated PNG figures
docs/         # methods, sources, data dictionary, audit note
manuscript/   # results update and recorded manuscript numerical targets
```

## Reproducing the analysis

Use Python 3.11+ and install `requirements.txt` in a virtual environment.

```bash
python -m venv .venv
```

Activate with `.venv\Scripts\activate` on Windows or `source .venv/bin/activate` on macOS/Linux, then run:

```bash
pip install -r requirements.txt
python analysis/run_analysis.py
python analysis/make_figures.py
python analysis/verify_results.py
```

The scripts read `data/processed/rq1_all_regions_audited.csv`. Verification checks the numerical targets recorded from the final manuscript in `manuscript/paper_numbers.json`, independently recomputes model-fit metrics, reconciles CSVs with every workbook result tab, and checks the figure source hashes. It fails on inconsistencies. It does not edit the manuscript or require a private runtime.

## Interpretation boundary

The exposed/comparison labels are project classifications, not individual radiation dose measurements. This exploratory ecological study identifies no causal radiation effect. RQ1 includes only six regions; RQ2 includes only three regions repeatedly observed over time. The models are not validated forecasts.

## Citation

`CITATION.cff` lists the sole project author, Akezhan Omashev.
