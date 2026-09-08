"""Reproducible analysis for the Kazakhstan regional health PCA project.

Research Question 1 (RQ1)
-------------------------
Compare project-classified exposed and comparison regions using annual regional
health and socioeconomic indicators from 2011-2024. Primary group summaries are
based on regional means so repeated years are not treated as independent regions.

Research Question 2 (RQ2)
-------------------------
Restrict analysis to the three exposed-classified regions and compare:
A) OLS mortality model with five original indicators.
B) OLS mortality model with PC1 and PC2 after PCA dimensionality reduction.

Mortality is the observed crude all-cause mortality percentage calculated from
registered deaths / population * 100. It is NOT included in PCA.

HC3 changes covariance estimates, standard errors, and p-values; it does not
change fitted values from OLS.
"""

from __future__ import annotations

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
    "Cancer_pct",
    "Infant_mortality_pct",
    "Circulatory_pct",
    "Disability_pct",
    "Unemployment_pct",
]
RQ1_INDICATORS = PREDICTORS + ["Mortality_pct"]


def kmo_and_bartlett(X: np.ndarray):
    """Return overall KMO, variable KMO values, Bartlett chi-square, df, p-value."""
    n, p = X.shape
    corr = np.corrcoef(X, rowvar=False)
    inv_corr = np.linalg.inv(corr)
    partial = np.eye(p)
    for i in range(p):
        for j in range(p):
            if i != j:
                partial[i, j] = -inv_corr[i, j] / math.sqrt(inv_corr[i, i] * inv_corr[j, j])

    r2 = corr ** 2
    p2 = partial ** 2
    mask = ~np.eye(p, dtype=bool)
    overall = r2[mask].sum() / (r2[mask].sum() + p2[mask].sum())

    variable = []
    for i in range(p):
        keep = np.arange(p) != i
        numerator = r2[i, keep].sum()
        variable.append(numerator / (numerator + p2[i, keep].sum()))

    det_r = np.linalg.det(corr)
    chi2 = -(n - 1 - (2 * p + 5) / 6) * np.log(det_r)
    df = p * (p - 1) // 2
    p_value = stats.chi2.sf(chi2, df)
    return corr, overall, np.array(variable), chi2, df, p_value


def rq1(df: pd.DataFrame) -> None:
    # Annual group means for trend figures.
    yearly = (
        df.groupby(["Project_Group", "Year"], as_index=False)[RQ1_INDICATORS]
        .mean(numeric_only=True)
    )
    yearly.to_csv(OUT / "rq1_yearly_group_means.csv", index=False)

    # Each region is reduced to one 2011-2024 mean for primary group comparison.
    region_means = (
        df.groupby(["Project_Group", "Region"], as_index=False)[RQ1_INDICATORS]
        .mean(numeric_only=True)
    )
    region_means.to_csv(OUT / "rq1_region_means.csv", index=False)

    rows = []
    for indicator in RQ1_INDICATORS:
        exposed = region_means.loc[
            region_means["Project_Group"] == "Exposed-classified", indicator
        ].to_numpy(float)
        comparison = region_means.loc[
            region_means["Project_Group"] == "Comparison-classified", indicator
        ].to_numpy(float)
        t, p = stats.ttest_ind(exposed, comparison, equal_var=False)
        rows.append(
            {
                "Indicator": indicator,
                "Exposed_mean_of_region_means": exposed.mean(),
                "Comparison_mean_of_region_means": comparison.mean(),
                "Difference_exposed_minus_comparison": exposed.mean() - comparison.mean(),
                "Exposed_SD_across_regions": exposed.std(ddof=1),
                "Comparison_SD_across_regions": comparison.std(ddof=1),
                "Welch_t_region_means": t,
                "Welch_p_region_means": p,
                "N_regions_exposed": len(exposed),
                "N_regions_comparison": len(comparison),
            }
        )
    pd.DataFrame(rows).to_csv(OUT / "rq1_group_comparison.csv", index=False)


def rq2(df: pd.DataFrame) -> None:
    exp = df[df["Project_Group"] == "Exposed-classified"].copy()
    exp = exp.sort_values(["Region", "Year"]).reset_index(drop=True)

    X = exp[PREDICTORS].to_numpy(float)
    y = exp["Mortality_pct"].to_numpy(float)
    n, p = X.shape

    corr, kmo, kmo_var, bart_chi2, bart_df, bart_p = kmo_and_bartlett(X)
    pd.DataFrame(corr, index=PREDICTORS, columns=PREDICTORS).to_csv(
        OUT / "rq2_predictor_correlation_matrix.csv"
    )

    scaler = StandardScaler()
    Z = scaler.fit_transform(X)
    pca = PCA(n_components=p)
    all_scores = pca.fit_transform(Z)
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
        diag.append({"Statistic": f"PC{i} eigenvalue", "Value": ev})
        diag.append({"Statistic": f"PC{i} explained variance ratio", "Value": ratio})
    diag.append(
        {"Statistic": "PC1+PC2 cumulative explained variance", "Value": pca.explained_variance_ratio_[:2].sum()}
    )
    pd.DataFrame(diag).to_csv(OUT / "rq2_pca_diagnostics.csv", index=False)

    coeff = pd.DataFrame(
        {
            "Indicator": PREDICTORS,
            "PC1_component_coefficient": pca.components_[0],
            "PC2_component_coefficient": pca.components_[1],
        }
    )
    coeff.to_csv(OUT / "rq2_pca_component_coefficients.csv", index=False)

    scores = exp[["Region", "Year", "Mortality_pct"]].copy()
    for j, name in enumerate(PREDICTORS):
        scores[f"Z_{name}"] = Z[:, j]
    scores["PC1"] = pc1
    scores["PC2"] = pc2
    scores.to_csv(OUT / "rq2_pca_scores.csv", index=False)

    year_centered = exp["Year"].to_numpy(float) - exp["Year"].mean()
    region_karaganda = (exp["Region"] == "Karaganda").astype(float).to_numpy()
    region_pavlodar = (exp["Region"] == "Pavlodar").astype(float).to_numpy()

    XA = np.column_stack(
        [np.ones(n), X, year_centered, region_karaganda, region_pavlodar]
    )
    names_a = [
        "Intercept",
        *PREDICTORS,
        "Year_centered",
        "Region_Karaganda",
        "Region_Pavlodar",
    ]
    model_a = sm.OLS(y, XA).fit(cov_type="HC3")
    pred_a = model_a.predict(XA)
    rmse_a = np.sqrt(np.mean((y - pred_a) ** 2))

    XB = np.column_stack(
        [np.ones(n), pc1, pc2, year_centered, region_karaganda, region_pavlodar]
    )
    names_b = [
        "Intercept",
        "PC1",
        "PC2",
        "Year_centered",
        "Region_Karaganda",
        "Region_Pavlodar",
    ]
    model_b = sm.OLS(y, XB).fit(cov_type="HC3")
    pred_b = model_b.predict(XB)
    rmse_b = np.sqrt(np.mean((y - pred_b) ** 2))

    comparison = pd.DataFrame(
        [
            {
                "Model": "Before PCA - 5 original indicators",
                "N": n,
                "Parameters": XA.shape[1],
                "R2": model_a.rsquared,
                "Adjusted_R2": model_a.rsquared_adj,
                "RMSE": rmse_a,
                "AIC": model_a.aic,
                "BIC": model_a.bic,
            },
            {
                "Model": "After PCA - PC1 + PC2",
                "N": n,
                "Parameters": XB.shape[1],
                "R2": model_b.rsquared,
                "Adjusted_R2": model_b.rsquared_adj,
                "RMSE": rmse_b,
                "AIC": model_b.aic,
                "BIC": model_b.bic,
            },
        ]
    )
    comparison.to_csv(OUT / "rq2_model_comparison.csv", index=False)

    coefficient_rows = []
    for model_name, model, names in [
        ("Before PCA", model_a, names_a),
        ("After PCA", model_b, names_b),
    ]:
        ci = model.conf_int(alpha=0.05)
        for j, term in enumerate(names):
            coefficient_rows.append(
                {
                    "Model": model_name,
                    "Term": term,
                    "Coefficient": model.params[j],
                    "HC3_SE": model.bse[j],
                    "t": model.tvalues[j],
                    "p_value": model.pvalues[j],
                    "CI95_low": ci[j, 0],
                    "CI95_high": ci[j, 1],
                }
            )
    pd.DataFrame(coefficient_rows).to_csv(OUT / "rq2_ols_coefficients.csv", index=False)

    predictions = exp[["Region", "Year", "Mortality_pct"]].rename(
        columns={"Mortality_pct": "Observed_Mortality"}
    )
    predictions["Fitted_Before_PCA"] = pred_a
    predictions["Residual_Before_PCA"] = y - pred_a
    predictions["Fitted_After_PCA"] = pred_b
    predictions["Residual_After_PCA"] = y - pred_b
    predictions.to_csv(OUT / "rq2_fitted_mortality.csv", index=False)

    print("RQ2 exposed-only PCA + OLS complete")
    print(f"Overall KMO: {kmo:.4f}")
    print(f"PC1+PC2 variance: {pca.explained_variance_ratio_[:2].sum():.4%}")
    print(comparison.to_string(index=False))


def main() -> None:
    df = pd.read_csv(DATA)
    rq1(df)
    rq2(df)


if __name__ == "__main__":
    main()
