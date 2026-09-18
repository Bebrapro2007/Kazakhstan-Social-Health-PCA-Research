# Audit note: mortality correction and manuscript synchronization

## Earlier mortality correction

During repository preparation, the exposed-only working dataset was checked against the supplied official deaths workbook. Its 2011-2021 mortality series did not equal registered deaths / project population x 100. For example, East Kazakhstan+Abay 2011 was approximately 0.7316% in that legacy file, whereas supplied deaths and the project denominator yield approximately 1.1928%.

The audited processed datasets already use the corrected observed mortality for every region-year. This update does not change those datasets or raw workbooks. Analysis now checks the death/population identity before calculating results.

Death-count geography follows the original project denominator rule:

- East Kazakhstan+Abay: East Kazakhstan plus Abay deaths for all study years.
- Karaganda: Karaganda plus Ulytau deaths for 2011-2021; Karaganda alone for 2022-2024.
- Pavlodar, Akmola, Almaty Region, and Kostanay: their supplied regional death counts.

Some rate-based indicators cannot be fully reconstructed to constant boundaries with the supplied denominators. The 2011-2021 analysis checks sensitivity to that limitation; it is not full geographic harmonization.

## Final manuscript reference

Numerical verification uses `Research paper draft 2.docx`, saved on 2026-09-19 at 01:27 (+05), Word revision 3 / modified 2026-09-18 20:27 UTC. Its title is *Regional Health and Social Indicator Patterns and PCA-Based Mortality Modeling in Kazakhstan, 2011-2024*. SHA-256:

`67a877c9fa843ada673b0b1662e2effad0a30b6a73d550cc0c1d695d4bc2dbb8`

This is the latest locally saved version with the repository availability link. Older conversation attachments with original/PCA R-squared 0.5992/0.5922 are superseded. The final manuscript itself is not added to the repository; its reported analytical targets and source hash are recorded in `manuscript/paper_numbers.json`.

## Synchronization changes

The main analysis now includes the four-parameter region-and-year baseline, nine-parameter original-indicator model, and six-parameter PCA model. The manuscript's RQ1 exact p-values are computed by enumerating all 20 region-label allocations. Existing Welch statistics remain secondary diagnostics; they must not be substituted for the paper's exact p-values. PC1/PC2 signs match the manuscript coefficient table.

Both RQ1 and RQ2 are repeated for 2011-2021. The shorter-period scaler and PCA are refit on the 33 exposed rows. CSVs include all three models and underlying diagnostics, coefficients, scores, and fitted values. The Excel workbook preserves existing tab names/order and appends the sensitivity outputs. Figures use the same CSV values and retain their source hashes.

| Full-period model | R-squared | Adjusted R-squared | RMSE | AIC | BIC |
|---|---:|---:|---:|---:|---:|
| Baseline | 0.0840 | 0.0116 | 0.1023 | -64.29 | -57.34 |
| Original-indicator | 0.3112 | 0.1443 | 0.0887 | -66.27 | -50.63 |
| PCA-reduced | 0.2639 | 0.1617 | 0.0917 | -69.48 | -59.05 |

For 2011-2021, original/PCA R-squared is 0.5015/0.4714 and RMSE 0.0782/0.0805; PCA retains lower AIC/BIC. Overall KMO is 0.493. All results are in-sample.

## Verification

`analysis/verify_results.py` checks all 75 recorded numerical targets at manuscript precision, Bartlett's reported p-value bound, and the stated shorter-period AIC/BIC ordering. Independent NumPy least-squares fits and SVD reconstruct both periods' PCA scores/component coefficients and all six models' predictions/R-squared/adjusted R-squared/RMSE/AIC/BIC. An independent SciPy exact permutation calculation checks RQ1 in both periods. The verifier reconciles workbook result tabs with their CSVs and checks all eight PNG source hashes. Display rounding is allowed; analytical values retain full precision.

Reproduce calculations, workbook, and figures before running verification. A manuscript subsequently edited beyond the recorded SHA-256 needs a new audit; passing these checks does not verify an unseen later version.

Tested environment: Python 3.12.14; NumPy 2.5.3, pandas 3.0.6, SciPy 1.18.1, scikit-learn 1.9.1, statsmodels 0.15.0, matplotlib 3.11.2, XlsxWriter 3.2.9, openpyxl 3.1.5.
