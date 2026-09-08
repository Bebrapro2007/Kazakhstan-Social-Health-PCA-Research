# GitHub upload checklist

Before making the repository public:

- [ ] Edit `CITATION.cff` with the author's full preferred name.
- [ ] Decide whether to add an open-source/data license. No license is included automatically.
- [ ] Confirm that redistribution of every workbook in `data/source/` is permitted. If not, remove restricted files and keep only source URLs/metadata.
- [ ] Do not upload the older exposed-only mortality outputs; they are superseded by this repository.
- [ ] Update the manuscript using `manuscript/RESULTS_UPDATE.md` before uploading a paper PDF/DOCX.
- [ ] Run `python analysis/run_analysis.py` and confirm the generated model comparison matches `results/tables/rq2_model_comparison.csv`.
- [ ] Run `python analysis/make_figures.py` and inspect all PNG files in `figures/`.
- [ ] Add a repository description such as: `Exploratory PCA and ecological panel analysis of regional health indicators in Kazakhstan, 2011-2024.`
- [ ] Add topics: `pca`, `statistics`, `kazakhstan`, `public-health`, `ecological-study`, `python`, `ols-regression`.
