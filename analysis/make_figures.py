"""Generate repository figures from processed/results CSV files."""

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / "results" / "tables"
FIGURES = ROOT / "figures"
FIGURES.mkdir(parents=True, exist_ok=True)

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
fig.savefig(FIGURES / "rq1_mortality_group_trend.png", dpi=220)
plt.close(fig)

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
fig.savefig(FIGURES / "rq2_pca_explained_variance.png", dpi=220)
plt.close(fig)

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
fig.savefig(FIGURES / "rq2_pc1_component_coefficients.png", dpi=220)
plt.close(fig)

# Figure 4: PC2 coefficients
fig, ax = plt.subplots(figsize=(8.3, 4.8))
ax.barh(y, coef["PC2_component_coefficient"])
ax.set_yticks(y, coef["Indicator"])
ax.axvline(0, linewidth=1)
ax.set_title("RQ2: PC2 component coefficients")
ax.set_xlabel("Component coefficient")
fig.tight_layout()
fig.savefig(FIGURES / "rq2_pc2_component_coefficients.png", dpi=220)
plt.close(fig)

# Figure 5: observed vs fitted mortality
pred = pd.read_csv(TABLES / "rq2_fitted_mortality.csv")
fig, ax = plt.subplots(figsize=(6.5, 6.0))
ax.scatter(pred["Observed_Mortality"], pred["Fitted_Before_PCA"], label="Before PCA", alpha=0.8)
ax.scatter(pred["Observed_Mortality"], pred["Fitted_After_PCA"], label="After PCA", alpha=0.8)
lo = min(pred["Observed_Mortality"].min(), pred["Fitted_Before_PCA"].min(), pred["Fitted_After_PCA"].min())
hi = max(pred["Observed_Mortality"].max(), pred["Fitted_Before_PCA"].max(), pred["Fitted_After_PCA"].max())
ax.plot([lo, hi], [lo, hi], linestyle="--", linewidth=1, label="Perfect fit")
ax.set_title("RQ2: Observed vs fitted crude mortality")
ax.set_xlabel("Observed mortality (%)")
ax.set_ylabel("Fitted mortality (%)")
ax.legend()
ax.grid(True, alpha=0.25)
fig.tight_layout()
fig.savefig(FIGURES / "rq2_observed_vs_fitted_mortality.png", dpi=220)
plt.close(fig)

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
fig.savefig(FIGURES / "rq2_pc1_pc2_scores.png", dpi=220)
plt.close(fig)

print(f"Saved figures to {FIGURES}")
