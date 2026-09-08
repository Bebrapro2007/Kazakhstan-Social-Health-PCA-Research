# Kazakhstan Regional Health Indicators and PCA (2011-2024)

Reproducible research repository for an exploratory ecological panel study of regional health and socioeconomic indicators in Kazakhstan.

## Research design

The project contains **two distinct analyses** built from the same regional data source.

**RQ1 - regional comparison.** Six regions are compared from 2011-2024: three project-classified exposed regions (East Kazakhstan+Abay, Karaganda, Pavlodar) and three comparison-classified regions (Akmola, Almaty Region, Kostanay). The primary comparison uses **region-level means** so repeated annual rows are not treated as 84 independent geographic units.

**RQ2 - PCA and mortality model comparison.** The analysis is restricted to the **three exposed-classified regions** (42 region-year rows). Five predictors are standardized and reduced with PCA. Crude all-cause mortality is the observed outcome and is **not included in PCA**. Two OLS specifications are compared:

1. Original-indicator model: cancer morbidity + infant mortality + circulatory-disease morbidity + disability + unemployment + centered year trend + region fixed effects.
2. PCA-reduced model: PC1 + PC2 + centered year trend + region fixed effects.

HC3 covariance estimates are used for standard errors and p-values. HC3 does not change fitted mortality values.

## Current audited RQ2 results

| Metric | Before PCA | After PCA |
|---|---:|---:|
| N region-year rows | 42 | 42 |
| Model parameters | 9 | 6 |
| R-squared | 0.3112 | 0.2639 |
| Adjusted R-squared | 0.1443 | 0.1617 |
| RMSE | 0.0887 | 0.0917 |
| AIC | -66.27 | -69.48 |
| BIC | -50.63 | -59.05 |

PCA diagnostics for the exposed-only data:

- Overall KMO: **0.5099** (borderline; interpret PCA as exploratory)
- Bartlett chi-square(10): **75.5632**, p < 0.001 under the conventional independent-row reference distribution
- PC1 explained variance: **49.18%**
- PC2 explained variance: **26.03%**
- PC1 + PC2 cumulative explained variance: **75.21%**

The reduced model is more parsimonious and has better AIC/BIC, but lower R-squared and slightly higher RMSE. These are **in-sample** results, not validated forecasting performance.

## Important audit note

A previous exposed-only working file used a mortality series for 2011-2021 that did not match `registered deaths / population x 100`. This repository **does not use that legacy mortality series**. Observed mortality in `data/processed/` is recomputed from the supplied official deaths workbook and the project population denominator for every region-year. See `docs/AUDIT_NOTE.md`.

## Repository structure

```text
.
├── README.md
├── CITATION.cff
├── requirements.txt
├── .gitignore
├── analysis/
│   ├── run_analysis.py
│   └── make_figures.py
├── data/
│   ├── source/       # supplied official/statistical workbooks + legacy files
│   └── processed/    # repository-ready CSV datasets
├── results/
│   └── tables/       # generated RQ1/RQ2 output tables
├── figures/          # publication-ready PNG figures
├── docs/
│   ├── DATA_DICTIONARY.md
│   ├── METHODS.md
│   ├── AUDIT_NOTE.md
│   └── SOURCES.md
└── manuscript/
    └── RESULTS_UPDATE.md
```

## Reproducing the analysis

Python 3.11+ is recommended.

```bash
python -m venv .venv
```

Windows:

```bash
.venv\Scripts\activate
pip install -r requirements.txt
python analysis/run_analysis.py
python analysis/make_figures.py
```

macOS/Linux:

```bash
source .venv/bin/activate
pip install -r requirements.txt
python analysis/run_analysis.py
python analysis/make_figures.py
```

The analysis reads `data/processed/rq1_all_regions_audited.csv` and regenerates tables under `results/tables/`.

## Interpretation boundary

This is an **exploratory ecological study**. The exposed/comparison labels are project classifications, not individual radiation dose measurements. The analysis does not identify a causal radiation effect. Only six independent geographic regions are included in RQ1, and RQ2 contains only three exposed-classified regions observed repeatedly over time.

## Suggested citation

See `CITATION.cff` and edit the author details before public release if necessary.
