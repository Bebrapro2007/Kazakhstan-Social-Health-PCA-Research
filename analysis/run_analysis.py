"""Reproduce full-period and pre-2022 regional comparisons and mortality models.

RQ1 compares three exposed-classified with three comparison-classified REGION
means. Its primary two-sided permutation test enumerates all 20 allocations.
Welch results are retained as explicitly named secondary summaries.

RQ2 compares baseline, original-indicator, and PCA-reduced OLS models, all with
region indicators and a centered linear year term. HC3 affects inference, not
OLS fitted values. Mortality (registered deaths / population * 100) is the
outcome and is excluded from PCA. The 2011-2021 analysis refits its scaler/PCA.
"""

from __future__ import annotations

import argparse
from itertools import combinations
import math
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
import statsmodels.api as sm

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "processed" / "rq1_all_regions_audited.csv"
OUT = ROOT / "results" / "tables"
OUT.mkdir(parents=True, exist_ok=True)

PREDICTORS = [
    "Cancer_pct", "Infant_mortality_pct", "Circulatory_pct",
    "Disability_pct", "Unemployment_pct",
]
RQ1_INDICATORS = PREDICTORS + ["Mortality_pct"]
PERIODS = [("2011-2024", 2011, 2024), ("2011-2021", 2011, 2021)]
MODEL_LABELS = [
    "Baseline - Region + Year",
    "Before PCA - 5 original indicators",
    "After PCA - PC1 + PC2",
]


def validate_input(df: pd.DataFrame) -> None:
    """Fail before exporting results if the audited balanced panel is invalid."""
    required = ["Region", "Year", "Project_Group", "Population", "Registered_deaths", *RQ1_INDICATORS]
    if df[required].isna().any().any():
        raise ValueError("Audited input contains missing required values")
    if df.duplicated(["Region", "Year"]).any():
        raise ValueError("Audited input contains duplicate region-year keys")
    if len(df) != 84 or df["Region"].nunique() != 6:
        raise ValueError("Expected 84 rows across six regions")
    if any(set(part["Year"]) != set(range(2011, 2025)) for _, part in df.groupby("Region")):
        raise ValueError("Expected complete 2011-2024 observations for each region")
    if df["Project_Group"].value_counts().to_dict() != {"Exposed-classified": 42, "Comparison-classified": 42}:
        raise ValueError("Expected 42 observations in each classification")
    if (df.groupby("Region")["Project_Group"].nunique() != 1).any():
        raise ValueError("A region changes project classification")
    if (df["Population"] <= 0).any():
        raise ValueError("Population must be positive")
    if not np.isfinite(df[["Year", "Population", "Registered_deaths", *RQ1_INDICATORS]].to_numpy(float)).all():
        raise ValueError("Audited input contains non-finite numeric values")
    calculated = df["Registered_deaths"] / df["Population"] * 100
    if not np.allclose(df["Mortality_pct"], calculated, rtol=0, atol=1e-12):
        raise ValueError("Mortality does not equal registered deaths / population * 100")


def kmo_and_bartlett(X: np.ndarray):
    """Return correlation, KMO, variable KMO, and Bartlett statistics."""
    n, p = X.shape
    corr = np.corrcoef(X, rowvar=False)
    inv_corr = np.linalg.inv(corr)
    partial = np.eye(p)
    for i in range(p):
        for j in range(p):
            if i != j:
                partial[i, j] = -inv_corr[i, j] / math.sqrt(inv_corr[i, i] * inv_corr[j, j])
    r2, p2 = corr ** 2, partial ** 2
    mask = ~np.eye(p, dtype=bool)
    overall = r2[mask].sum() / (r2[mask].sum() + p2[mask].sum())
    variable = []
    for i in range(p):
        keep = np.arange(p) != i
        numerator = r2[i, keep].sum()
        variable.append(numerator / (numerator + p2[i, keep].sum()))
    chi2 = -(n - 1 - (2 * p + 5) / 6) * np.log(np.linalg.det(corr))
    degrees = p * (p - 1) // 2
    return corr, overall, np.array(variable), chi2, degrees, stats.chi2.sf(chi2, degrees)


def exact_permutation_p(exposed: np.ndarray, comparison: np.ndarray) -> tuple[float, int]:
    """Enumerate every equal-sized allocation, including the observed allocation."""
    values = np.concatenate([exposed, comparison])
    observed = abs(exposed.mean() - comparison.mean())
    differences = []
    indices = np.arange(len(values))
    for allocation in combinations(indices, len(exposed)):
        mask = np.isin(indices, allocation)
        differences.append(abs(values[mask].mean() - values[~mask].mean()))
    # Include ties: decimal inputs and summation order differ at machine precision.
    tolerance = np.finfo(float).eps * max(1.0, np.abs(values).max()) * 32
    return float(np.mean(np.asarray(differences) >= observed - tolerance)), len(differences)


def rq1_comparison(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    region_means = df.groupby(["Project_Group", "Region"], as_index=False)[RQ1_INDICATORS].mean()
    rows = []
    for indicator in RQ1_INDICATORS:
        exposed = region_means.loc[region_means["Project_Group"] == "Exposed-classified", indicator].to_numpy(float)
        comparison = region_means.loc[region_means["Project_Group"] == "Comparison-classified", indicator].to_numpy(float)
        exact_p, allocations = exact_permutation_p(exposed, comparison)
        welch_t, welch_p = stats.ttest_ind(exposed, comparison, equal_var=False)
        rows.append({
            "Indicator": indicator,
            "Exposed_mean_of_region_means": exposed.mean(),
            "Comparison_mean_of_region_means": comparison.mean(),
            "Difference_exposed_minus_comparison": exposed.mean() - comparison.mean(),
            "Exposed_SD_across_regions": exposed.std(ddof=1),
            "Comparison_SD_across_regions": comparison.std(ddof=1),
            "Exact_permutation_p_region_means": exact_p,
            "Permutation_allocations": allocations,
            "Welch_t_region_means": welch_t,
            "Welch_p_region_means": welch_p,
            "N_regions_exposed": len(exposed),
            "N_regions_comparison": len(comparison),
        })
    return region_means, pd.DataFrame(rows)


def rq1(df: pd.DataFrame) -> None:
    yearly = df.groupby(["Project_Group", "Year"], as_index=False)[RQ1_INDICATORS].mean()
    yearly.to_csv(OUT / "rq1_yearly_group_means.csv", index=False)
    sensitivity = []
    for period, first_year, last_year in PERIODS:
        subset = df[df["Year"].between(first_year, last_year)]
        means, comparison = rq1_comparison(subset)
        prefix = "rq1" if last_year == 2024 else "rq1_pre2022"
        means.to_csv(OUT / f"{prefix}_region_means.csv", index=False)
        comparison.to_csv(OUT / f"{prefix}_group_comparison.csv", index=False)
        sensitivity.append(comparison.assign(Period=period, N_region_year_rows=len(subset)))
    pd.concat(sensitivity, ignore_index=True).to_csv(OUT / "rq1_boundary_sensitivity.csv", index=False)


def rq2(df: pd.DataFrame, prefix: str = "rq2") -> pd.DataFrame:
    exp = df[df["Project_Group"] == "Exposed-classified"].sort_values(["Region", "Year"]).reset_index(drop=True)
    X, y = exp[PREDICTORS].to_numpy(float), exp["Mortality_pct"].to_numpy(float)
    n, p = X.shape
    corr, kmo, kmo_var, bart_chi2, bart_df, bart_p = kmo_and_bartlett(X)
    pd.DataFrame(corr, index=PREDICTORS, columns=PREDICTORS).to_csv(OUT / f"{prefix}_predictor_correlation_matrix.csv")
    Z = StandardScaler().fit_transform(X)
    pca = PCA(n_components=p, svd_solver="full")
    all_scores = pca.fit_transform(Z)
    # Match the manuscript orientation. Scores and component vectors move together.
    for component, indicator in [(0, "Infant_mortality_pct"), (1, "Disability_pct")]:
        if pca.components_[component, PREDICTORS.index(indicator)] < 0:
            pca.components_[component] *= -1
            all_scores[:, component] *= -1
    pc1, pc2 = all_scores[:, 0], all_scores[:, 1]
    diag = [
        {"Statistic": "N exposed region-year rows", "Value": n},
        {"Statistic": "Overall KMO", "Value": kmo},
        {"Statistic": "Bartlett chi-square", "Value": bart_chi2},
        {"Statistic": "Bartlett df", "Value": bart_df},
        {"Statistic": "Bartlett p-value", "Value": bart_p},
    ]
    for name, value in zip(PREDICTORS, kmo_var):
        diag.append({"Statistic": f"KMO {name}", "Value": value})
    for i, (ev, ratio) in enumerate(zip(pca.explained_variance_, pca.explained_variance_ratio_), start=1):
        diag.extend([{"Statistic": f"PC{i} eigenvalue", "Value": ev}, {"Statistic": f"PC{i} explained variance ratio", "Value": ratio}])
    diag.append({"Statistic": "PC1+PC2 cumulative explained variance", "Value": pca.explained_variance_ratio_[:2].sum()})
    pd.DataFrame(diag).to_csv(OUT / f"{prefix}_pca_diagnostics.csv", index=False)
    pd.DataFrame({"Indicator": PREDICTORS, "PC1_component_coefficient": pca.components_[0], "PC2_component_coefficient": pca.components_[1]}).to_csv(OUT / f"{prefix}_pca_component_coefficients.csv", index=False)
    scores = exp[["Region", "Year", "Mortality_pct"]].copy()
    for j, name in enumerate(PREDICTORS):
        scores[f"Z_{name}"] = Z[:, j]
    scores["PC1"], scores["PC2"] = pc1, pc2
    scores.to_csv(OUT / f"{prefix}_pca_scores.csv", index=False)
    controls = np.column_stack([
        exp["Year"].to_numpy(float) - exp["Year"].mean(),
        (exp["Region"] == "Karaganda").astype(float).to_numpy(),
        (exp["Region"] == "Pavlodar").astype(float).to_numpy(),
    ])
    control_names = ["Year_centered", "Region_Karaganda", "Region_Pavlodar"]
    specifications = [
        (MODEL_LABELS[0], "Baseline", "Baseline", np.column_stack([np.ones(n), controls]), ["Intercept", *control_names]),
        (MODEL_LABELS[1], "Before PCA", "Before_PCA", np.column_stack([np.ones(n), X, controls]), ["Intercept", *PREDICTORS, *control_names]),
        (MODEL_LABELS[2], "After PCA", "After_PCA", np.column_stack([np.ones(n), pc1, pc2, controls]), ["Intercept", "PC1", "PC2", *control_names]),
    ]
    comparison_rows, coefficient_rows = [], []
    predictions = exp[["Region", "Year", "Mortality_pct"]].rename(columns={"Mortality_pct": "Observed_Mortality"})
    for label, coefficient_label, fit_suffix, design, names in specifications:
        if np.linalg.matrix_rank(design) != design.shape[1]:
            raise ValueError(f"{prefix} {label}: model design is not full rank")
        model = sm.OLS(y, design).fit(cov_type="HC3")
        fitted = model.predict(design)
        comparison_rows.append({"Model": label, "N": n, "Parameters": design.shape[1], "R2": model.rsquared, "Adjusted_R2": model.rsquared_adj, "RMSE": np.sqrt(np.mean((y - fitted) ** 2)), "AIC": model.aic, "BIC": model.bic})
        confidence = model.conf_int(alpha=0.05)
        for j, term in enumerate(names):
            coefficient_rows.append({"Model": coefficient_label, "Term": term, "Coefficient": model.params[j], "HC3_SE": model.bse[j], "t": model.tvalues[j], "p_value": model.pvalues[j], "CI95_low": confidence[j, 0], "CI95_high": confidence[j, 1]})
        predictions[f"Fitted_{fit_suffix}"] = fitted
        predictions[f"Residual_{fit_suffix}"] = y - fitted
    comparison = pd.DataFrame(comparison_rows)
    comparison.to_csv(OUT / f"{prefix}_model_comparison.csv", index=False)
    pd.DataFrame(coefficient_rows).to_csv(OUT / f"{prefix}_ols_coefficients.csv", index=False)
    predictions.to_csv(OUT / f"{prefix}_fitted_mortality.csv", index=False)
    print(f"{prefix}: {n} exposed observations; KMO {kmo:.4f}; PC1 {pca.explained_variance_ratio_[0]:.4%}, PC2 {pca.explained_variance_ratio_[1]:.4%}, cumulative {pca.explained_variance_ratio_[:2].sum():.4%}")
    print(comparison.to_string(index=False))
    return comparison


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--skip-workbook", action="store_true", help="Generate tables without rebuilding Excel")
    args = parser.parse_args()
    df = pd.read_csv(DATA)
    validate_input(df)
    rq1(df)
    full = rq2(df).assign(Period="2011-2024")
    pre2022 = rq2(df[df["Year"].between(2011, 2021)], prefix="rq2_pre2022").assign(Period="2011-2021")
    pd.concat([full, pre2022], ignore_index=True).to_csv(OUT / "rq2_boundary_model_comparison.csv", index=False)
    if not args.skip_workbook:
        from export_workbook import export_workbook
        print(f"Workbook saved to {export_workbook(ROOT)}")


if __name__ == "__main__":
    main()
