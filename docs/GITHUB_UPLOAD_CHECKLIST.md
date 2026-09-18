# GitHub upload checklist

Before making the repository public:

- [x] `CITATION.cff` lists the sole project author, Akezhan Omashev.
- [ ] Decide whether to add an open-source/data license. No license is included automatically.
- [ ] Confirm that redistribution of every workbook in `data/source/` is permitted. If not, remove restricted files and keep only source URLs/metadata.
- [ ] Do not upload the older exposed-only mortality outputs; they are superseded by this repository.
- [x] Synchronize analytical outputs with the recorded final manuscript; see `manuscript/RESULTS_UPDATE.md`.
- [x] Regenerate all three models, pre-2022 tables, and the workbook with `python analysis/run_analysis.py`.
- [x] Regenerate and visually inspect all figures; verify source hashes and numerical agreement with `python analysis/verify_results.py`.
- [ ] Add a repository description such as: `Exploratory PCA and ecological panel analysis of regional health indicators in Kazakhstan, 2011-2024.`
- [ ] Add topics: `pca`, `statistics`, `kazakhstan`, `public-health`, `ecological-study`, `python`, `ols-regression`.
