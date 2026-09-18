"""Generate repository figures from processed/results CSV files."""

from pathlib import Path
import hashlib
import json
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "results" / "tables"
FIGURES = ROOT / "figures"
FIGURES.mkdir(parents=True, exist_ok=True)


def save_figure(fig, filename, *source_names):
    """Hash CSV text with LF newlines for portable figure provenance checks."""
    provenance = {"source_sha256": {
        name: hashlib.sha256((TABLES / name).read_text(encoding="utf-8").encode("utf-8")).hexdigest()
        for name in source_names
    }}
    fig.savefig(FIGURES / filename, dpi=220,
                metadata={"Description": json.dumps(provenance, sort_keys=True)})
    plt.close(fig)

# Figure 1: RQ1 mortality trend by project group
yearly = pd.read_csv(TABLES / "rq1_yearly_group_means.csv")
fig, ax = plt.subplots(figsize=(8.5, 5.2))
for group, part in yearly.groupby("Project_Group"):
    ax.plot(part["Year"], part["Mortality_pct"], marker="o", label=group)
ax.set_title("RQ1: Mean crude mortality by project classification")
ax.set_xlabel("Year")
ax.set_ylabel("Crude all-cause mortality (%)")
ax.legend()
ax.grid(True, alpha=0.25)
fig.tight_layout()
save_figure(fig, "rq1_mortality_group_trend.png", "rq1_yearly_group_means.csv")

# Figure 2: PCA explained variance
pca_diag = pd.read_csv(TABLES / "rq2_pca_diagnostics.csv")
ratios = []
for i in range(1, 6):
    label = f"PC{i} explained variance ratio"
    ratios.append(float(pca_diag.loc[pca_diag["Statistic"] == label, "Value"].iloc[0]) * 100)
fig, ax = plt.subplots(figsize=(7.6, 4.8))
ax.bar([f"PC{i}" for i in range(1, 6)], ratios)
ax.set_title("RQ2: PCA explained variance in exposed-classified regions")
ax.set_ylabel("Explained variance (%)")
ax.set_xlabel("Principal component")
for i, v in enumerate(ratios):
    ax.text(i, v + 0.8, f"{v:.1f}%", ha="center", va="bottom", fontsize=9)
fig.tight_layout()
save_figure(fig, "rq2_pca_explained_variance.png", "rq2_pca_diagnostics.csv")

# Figure 3: PC1 coefficients
coef = pd.read_csv(TABLES / "rq2_pca_component_coefficients.csv")
fig, ax = plt.subplots(figsize=(8.3, 4.8))
y = np.arange(len(coef))
ax.barh(y, coef["PC1_component_coefficient"])
ax.set_yticks(y, coef["Indicator"])
ax.axvline(0, linewidth=1)
ax.set_title("RQ2: PC1 component coefficients")
ax.set_xlabel("Component coefficient")
fig.tight_layout()
save_figure(fig, "rq2_pc1_component_coefficients.png", "rq2_pca_component_coefficients.csv")

# Figure 4: PC2 coefficients
fig, ax = plt.subplots(figsize=(8.3, 4.8))
ax.barh(y, coef["PC2_component_coefficient"])
ax.set_yticks(y, coef["Indicator"])
ax.axvline(0, linewidth=1)
ax.set_title("RQ2: PC2 component coefficients")
ax.set_xlabel("Component coefficient")
fig.tight_layout()
save_figure(fig, "rq2_pc2_component_coefficients.png", "rq2_pca_component_coefficients.csv")

# Figure 5: observed vs fitted mortality
pred = pd.read_csv(TABLES / "rq2_fitted_mortality.csv")
fig, ax = plt.subplots(figsize=(6.5, 6.0))
fits = [("Fitted_Baseline", "Baseline: Region + Year", "^"),
        ("Fitted_Before_PCA", "Original: 5 indicators + controls", "o"),
        ("Fitted_After_PCA", "PCA: PC1 + PC2 + controls", "s")]
for column, label, marker in fits:
    ax.scatter(pred["Observed_Mortality"], pred[column], label=label, marker=marker, alpha=0.75)
limits = pred[["Observed_Mortality", *(column for column, _, _ in fits)]]
lo, hi = limits.min().min(), limits.max().max()
ax.plot([lo, hi], [lo, hi], linestyle="--", linewidth=1, label="Perfect fit")
ax.set_title("RQ2: Observed vs fitted crude mortality")
ax.set_xlabel("Observed mortality (%)")
ax.set_ylabel("Fitted mortality (%)")
ax.legend(fontsize=8)
ax.grid(True, alpha=0.25)
fig.tight_layout()
save_figure(fig, "rq2_observed_vs_fitted_mortality.png", "rq2_fitted_mortality.csv")

# Figure 6: PC1 vs PC2 by region
scores = pd.read_csv(TABLES / "rq2_pca_scores.csv")
fig, ax = plt.subplots(figsize=(7.2, 5.8))
for region, part in scores.groupby("Region"):
    ax.scatter(part["PC1"], part["PC2"], label=region, alpha=0.85)
ax.axhline(0, linewidth=0.8)
ax.axvline(0, linewidth=0.8)
ax.set_title("RQ2: PC1-PC2 scores in exposed-classified regions")
ax.set_xlabel("PC1 score")
ax.set_ylabel("PC2 score")
ax.legend(fontsize=8)
ax.grid(True, alpha=0.2)
fig.tight_layout()
save_figure(fig, "rq2_pc1_pc2_scores.png", "rq2_pca_scores.csv")

# Figure 7: boundary sensitivity of the five manuscript RQ1 indicators.
boundary = pd.read_csv(TABLES / "rq1_boundary_sensitivity.csv")
indicator_labels = {
    "Cancer_pct": "Cancer",
    "Infant_mortality_pct": "Infant mortality",
    "Circulatory_pct": "Circulatory disease",
    "Disability_pct": "Disability",
    "Unemployment_pct": "Unemployment",
}
fig, ax = plt.subplots(figsize=(8.5, 5.1))
positions = np.arange(len(indicator_labels))
for offset, (period, color) in zip([-0.14, 0.14], [("2011-2024", "#3465a4"), ("2011-2021", "#d97924")]):
    part = boundary[boundary["Period"] == period].set_index("Indicator").loc[list(indicator_labels)]
    ax.barh(positions + offset, part["Difference_exposed_minus_comparison"],
            height=0.26, label=period, color=color)
ax.set_yticks(positions, list(indicator_labels.values()))
ax.invert_yaxis()
ax.axvline(0, color="#444444", linewidth=0.9)
ax.set_title("RQ1: Pre-2022 boundary sensitivity")
ax.set_xlabel("Exposed minus comparison mean (percentage points)")
ax.legend(title="Analysis period")
ax.grid(axis="x", alpha=0.2)
fig.tight_layout()
save_figure(fig, "rq1_boundary_sensitivity.png", "rq1_boundary_sensitivity.csv")

# Figure 8: models fitted separately in each period; RMSE is an in-sample measure.
boundary_models = pd.read_csv(TABLES / "rq2_boundary_model_comparison.csv")
fig, axes = plt.subplots(1, 2, figsize=(10.4, 4.6))
for offset, (period, color) in zip([-0.18, 0.18], [("2011-2024", "#3465a4"), ("2011-2021", "#d97924")]):
    part = boundary_models[boundary_models["Period"] == period]
    for ax, measure in zip(axes, ["R2", "RMSE"]):
        ax.bar(np.arange(3) + offset, part[measure], width=0.34, label=period, color=color)
for ax, ylabel in zip(axes, ["In-sample R²", "In-sample RMSE (percentage points)"]):
    ax.set_xticks(np.arange(3), ["Baseline", "Original", "PCA"])
    ax.set_ylabel(ylabel)
    ax.grid(axis="y", alpha=0.2)
axes[0].legend(title="Analysis period", fontsize=8)
fig.suptitle("RQ2: Pre-2022 boundary sensitivity (PCA refitted in each period)")
fig.tight_layout()
save_figure(fig, "rq2_boundary_sensitivity.png", "rq2_boundary_model_comparison.csv")

print(f"Saved figures to {FIGURES}")
