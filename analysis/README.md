# Analysis scripts

- `run_analysis.py`: recomputes full-period and 2011-2021 RQ1 comparisons, exact permutation checks, exposed-only PCA, and baseline/original-indicator/PCA-reduced HC3 OLS outputs.
- `export_workbook.py`: exports the analytical CSV values to the existing result workbook sheet structure, appending shorter-period outputs.
- `make_figures.py`: regenerates figures from CSVs and embeds the plotted source-file hashes.
- `verify_results.py`: checks manuscript precision, independently reconstructed fit metrics, CSV/Excel agreement, and figure source hashes.

Run from the repository root after installing `requirements.txt`:

```bash
python analysis/run_analysis.py
python analysis/make_figures.py
python analysis/verify_results.py
```

Mortality is the observed dependent variable and remains outside PCA. The shorter-period scaler and PCA are refit using only 2011-2021 observations.
