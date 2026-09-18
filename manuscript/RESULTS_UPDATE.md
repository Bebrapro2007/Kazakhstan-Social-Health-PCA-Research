# Final manuscript synchronization

The repository now reproduces the analytical numbers reported in `Research paper draft 2.docx`, Word revision 3, modified 2026-09-18 20:27 UTC. The source SHA-256 and 75 numerical targets are recorded in `paper_numbers.json`. Earlier manuscript drafts and legacy exposed-only mortality outputs are superseded.

- Table 2: five RQ1 comparisons based on six regional means, with exact two-sided permutation p-values across 20 allocations.
- Table 3 / Figure 2: full-period versus 2011-2021 group differences; disability difference changes from +0.2443 to +0.0646 percentage points.
- Table 4: exposed-only PCA coefficients with PC1 infant-mortality positive and PC2 disability positive.
- Table 5: baseline, original-indicator, and PCA-reduced mortality models with 4, 9, and 6 parameters. R-squared = 0.0840 / 0.3112 / 0.2639; RMSE = 0.1023 / 0.0887 / 0.0917.
- Section 3.3: overall KMO 0.5099, disability KMO 0.216; Bartlett chi-square(10) 75.56, conventional p < 0.001; explained variance 49.18% + 26.03% = 75.21%.
- Section 3.4: independently refitted 2011-2021 original/PCA models have R-squared 0.5015/0.4714 and RMSE 0.0782/0.0805; PCA retains lower AIC/BIC, with KMO 0.493.
- Figure 4: the repository observed-versus-fitted mortality plot now includes all three specifications.

See `results/RESULTS_SUMMARY.md` and `docs/AUDIT_NOTE.md`. `analysis/verify_results.py` checks manuscript precision plus code/CSV/Excel/figure consistency. These checks do not establish agreement with any subsequent manuscript revision.
