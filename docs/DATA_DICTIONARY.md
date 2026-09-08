# Data dictionary

## Processed datasets

### `rq1_all_regions_audited.csv`

One row represents one region-year observation. There are 84 rows (6 regions x 14 years).

| Column | Meaning |
|---|---|
| `Region` | Geographic unit used by the project |
| `Year` | Calendar year, 2011-2024 |
| `Population` | Project population denominator |
| `Project_Group` | `Exposed-classified` or `Comparison-classified` |
| `Cancer_pct` | Cancer morbidity cases per 100,000 divided by 1,000; numerical percent scale |
| `Infant_mortality_pct` | Deaths under age 1 per 1,000 live births divided by 10; percent of live births |
| `Circulatory_pct` | Circulatory-disease morbidity cases per 100,000 divided by 1,000; numerical percent scale |
| `Disability_pct` | Registered persons with disability / population x 100 |
| `Unemployment_pct` | Reported unemployment percentage of labor force |
| `Registered_deaths` | Registered all-cause deaths used for mortality calculation |
| `Mortality_pct` | Observed crude all-cause mortality = registered deaths / population x 100 |
| `Imputed` | Whether at least one analytical input for the row was imputed in the legacy processing workflow |
| `Imputation_note` | Explanation of the imputation where present |
| `Data_note` | Source/provenance note inherited from the processed project table |

### `rq2_exposed_regions_audited.csv`

The subset used for RQ2. It contains only East Kazakhstan+Abay, Karaganda, and Pavlodar (42 region-year rows).

## Important denominator note

The five predictors do **not** share a common epidemiological denominator. PCA is performed after z-score standardization, but standardization does not make the original denominators epidemiologically equivalent.

## Mortality

`Mortality_pct` is the **observed outcome**, not an OLS prediction. OLS fitted values are stored separately in `results/tables/rq2_fitted_mortality.csv`.
