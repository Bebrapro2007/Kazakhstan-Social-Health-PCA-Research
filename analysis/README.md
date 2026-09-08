# Analysis scripts

## `run_analysis.py`

Regenerates all RQ1 and RQ2 CSV result tables from `data/processed/rq1_all_regions_audited.csv`.

## `make_figures.py`

Regenerates PNG figures from the result tables.

Run from the repository root:

```bash
python analysis/run_analysis.py
python analysis/make_figures.py
```

The scripts intentionally keep mortality outside PCA. `Mortality_pct` is the observed dependent variable for OLS.
