"""Export the audited CSV datasets and analysis tables to the research workbook."""

from __future__ import annotations

import argparse
import csv
import json
import math
import re
from pathlib import Path

import xlsxwriter


ROOT = Path(__file__).resolve().parents[1]
NUMERIC = re.compile(r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?$")
SHEETS = [
    ("RQ1_All_Data", "data/processed/rq1_all_regions_audited.csv"),
    ("RQ1_Group_Comparison", "results/tables/rq1_group_comparison.csv"),
    ("RQ1_Region_Means", "results/tables/rq1_region_means.csv"),
    ("RQ1_Yearly_Means", "results/tables/rq1_yearly_group_means.csv"),
    ("RQ2_Exposed_Data", "data/processed/rq2_exposed_regions_audited.csv"),
    ("RQ2_PCA_Diagnostics", "results/tables/rq2_pca_diagnostics.csv"),
    ("RQ2_PCA_Coefficients", "results/tables/rq2_pca_component_coefficients.csv"),
    ("RQ2_PCA_Scores", "results/tables/rq2_pca_scores.csv"),
    ("RQ2_Model_Comparison", "results/tables/rq2_model_comparison.csv"),
    ("RQ2_OLS_Coefficients", "results/tables/rq2_ols_coefficients.csv"),
    ("RQ2_Fitted_Mortality", "results/tables/rq2_fitted_mortality.csv"),
    ("RQ1_Boundary_Sensitivity", "results/tables/rq1_boundary_sensitivity.csv"),
    ("RQ1_Pre2022_Group_Comparison", "results/tables/rq1_pre2022_group_comparison.csv"),
    ("RQ1_Pre2022_Region_Means", "results/tables/rq1_pre2022_region_means.csv"),
    ("RQ2_Boundary_Comparison", "results/tables/rq2_boundary_model_comparison.csv"),
    ("RQ2_Pre2022_Model_Comparison", "results/tables/rq2_pre2022_model_comparison.csv"),
    ("RQ2_Pre2022_Diagnostics", "results/tables/rq2_pre2022_pca_diagnostics.csv"),
    ("RQ2_Pre2022_PCA_Coefficients", "results/tables/rq2_pre2022_pca_component_coefficients.csv"),
    ("RQ2_Pre2022_PCA_Scores", "results/tables/rq2_pre2022_pca_scores.csv"),
    ("RQ2_Pre2022_OLS_Coefficients", "results/tables/rq2_pre2022_ols_coefficients.csv"),
    ("RQ2_Pre2022_Fitted_Mortality", "results/tables/rq2_pre2022_fitted_mortality.csv"),
]


def read_csv(path: Path) -> list[list[object]]:
    """Read CSV records with numeric data stored as numeric Excel cells."""
    with path.open(newline="", encoding="utf-8-sig") as stream:
        rows = list(csv.reader(stream))
    for row in rows[1:]:
        for column, value in enumerate(row):
            if value == "":
                row[column] = None
            elif NUMERIC.fullmatch(value):
                number = float(value)
                if not math.isfinite(number):
                    raise ValueError(f"Non-finite number in {path}: {value}")
                row[column] = number
    if not rows or any(len(row) != len(rows[0]) for row in rows):
        raise ValueError(f"CSV rows are missing or inconsistent: {path}")
    return rows


def workbook_data(root: Path = ROOT) -> dict[str, object]:
    """Return the shared workbook values/layout for export and reconciliation."""
    sheets = []
    for name, relative_path in SHEETS:
        rows = read_csv(root / relative_path)
        widths = [28.0] + [18.0] * (len(rows[0]) - 1)
        if name in {"RQ1_All_Data", "RQ2_Exposed_Data"}:
            widths[:4] = [28.0, 10.0, 18.0, 22.0]
        elif "Model" in name or name == "RQ2_Boundary_Comparison":
            widths[0] = 46.0
        elif "OLS" in name:
            widths[:2] = [32.0, 30.0]
        elif "Diagnostics" in name:
            widths[0] = 45.0
        elif name == "RQ1_Pre2022_Region_Means":
            widths[1] = 28.0
        header_height = 58.0
        if "Model_Comparison" in name or "Diagnostics" in name or name == "RQ2_Boundary_Comparison":
            header_height = 24.0
        elif "Scores" in name or "OLS" in name or "Fitted" in name:
            header_height = 44.0
        elif name == "RQ1_Pre2022_Region_Means":
            header_height = 24.0
        sheets.append({"name": name, "csv": relative_path, "rows": rows, "widths": widths, "header_height": header_height})

    models = next(sheet["rows"] for sheet in sheets if sheet["name"] == "RQ2_Model_Comparison")
    if len(models) != 4:
        raise ValueError("The main RQ2 model comparison must contain exactly three models")
    model_columns = {column: i for i, column in enumerate(models[0])}
    diagnostics = dict(next(sheet["rows"] for sheet in sheets if sheet["name"] == "RQ2_PCA_Diagnostics")[1:])
    pre_diagnostics = dict(next(sheet["rows"] for sheet in sheets if sheet["name"] == "RQ2_Pre2022_Diagnostics")[1:])
    items = [
        ["RQ1", "6 regions, exposed-classified vs comparison-classified"],
        ["RQ2", "3 exposed-classified regions only"],
        ["Study years", "2011-2024"],
        ["RQ2 rows", diagnostics["N exposed region-year rows"]],
        ["RQ2 Overall KMO", diagnostics["Overall KMO"]],
        ["RQ2 PC1+PC2 variance", diagnostics["PC1+PC2 cumulative explained variance"]],
    ]
    for label, row in zip(["Baseline", "Original-indicator", "PCA-reduced"], models[1:]):
        for metric in ["R2", "RMSE", "AIC"]:
            items.append([f"{label} {'R²' if metric == 'R2' else metric}", row[model_columns[metric]]])
    items.extend([
        ["RQ1 primary test", "Exact permutation of six regional means (20 allocations)"],
        ["Boundary sensitivity", "2011-2021, RQ1 and RQ2"],
        ["Pre-2022 RQ2 rows", pre_diagnostics["N exposed region-year rows"]],
        ["Pre-2022 Overall KMO", pre_diagnostics["Overall KMO"]],
    ])
    notes = [
        "Important interpretation note",
        "Observed mortality is calculated from registered deaths / population × 100.",
        "Mortality is NOT included in PCA.",
        "HC3 changes SE/p-values, not fitted mortality values.",
        "All RQ2 model metrics are in-sample.",
        "Welch results are secondary. RQ1 uses exact region-label permutation tests.",
        "Pre-2022 analysis refits standardization, PCA and all three OLS models.",
    ]
    rows = [["Kazakhstan Regional Health PCA Research - Repository Results"], [], ["Item", "Value"], *items, [], *[[note] for note in notes]]
    note_row = len(items) + 5  # 1-based position, after the blank separator
    return {"author": "Akezhan Omashev", "readme": {"rows": rows, "note_row": note_row}, "sheets": sheets}


def export_workbook(root: Path = ROOT, output: Path | None = None) -> Path:
    """Regenerate the published workbook without requiring a private runtime."""
    data = workbook_data(root)
    output = Path(output) if output is not None else root / "results/research_results.xlsx"
    output.parent.mkdir(parents=True, exist_ok=True)
    with xlsxwriter.Workbook(output) as workbook:
        workbook.set_properties({"title": "Kazakhstan Regional Health PCA Research - Repository Results", "author": data["author"]})
        body = workbook.add_format({"font_name": "Carlito", "font_size": 11})
        header = workbook.add_format({"font_name": "Carlito", "font_size": 11, "bold": True, "font_color": "#FFFFFF", "bg_color": "#1F4E78", "align": "center", "valign": "vcenter", "text_wrap": True})
        numeric = workbook.add_format({"font_name": "Carlito", "font_size": 11, "num_format": "0.0000"})
        integer = workbook.add_format({"font_name": "Carlito", "font_size": 11, "num_format": "0"})
        summary_header = workbook.add_format({"font_name": "Carlito", "font_size": 11, "bold": True, "bg_color": "#D9EAF7", "align": "center"})
        title = workbook.add_format({"font_name": "Carlito", "font_size": 14, "bold": True, "font_color": "#FFFFFF", "bg_color": "#1F4E78", "align": "center"})
        note_title = workbook.add_format({"font_name": "Carlito", "font_size": 11, "bold": True, "bg_color": "#FFF2CC"})
        readme = workbook.add_worksheet("README")
        readme.set_column(0, 0, 30, body)
        readme.set_column(1, 1, 58, body)
        readme.set_column(2, 5, 13, body)
        readme.merge_range("A1:F1", data["readme"]["rows"][0][0], title)
        readme.write_row(2, 0, ["Item", "Value"], summary_header)
        for r, row in enumerate(data["readme"]["rows"][3:], start=3):
            if r + 1 >= data["readme"]["note_row"]:
                if row:
                    readme.merge_range(r, 0, r, 5, row[0], note_title if r + 1 == data["readme"]["note_row"] else body)
            else:
                for c, value in enumerate(row):
                    fmt = numeric if isinstance(value, (float, int)) else body
                    if row and row[0].endswith("rows"):
                        fmt = integer if isinstance(value, (float, int)) else body
                    if row and row[0] == "RQ2 PC1+PC2 variance" and c == 1:
                        fmt = workbook.add_format({"font_name": "Carlito", "font_size": 11, "num_format": "0.00%"})
                    readme.write(r, c, value, fmt)

        for table in data["sheets"]:
            sheet = workbook.add_worksheet(table["name"])
            if "Pre2022" in table["name"] or "Boundary" in table["name"]:
                sheet.hide_gridlines(2)
            for c, width in enumerate(table["widths"]):
                sheet.set_column(c, c, width, body)
            sheet.set_row(0, table["header_height"])
            sheet.write_row(0, 0, table["rows"][0], header)
            for r, row in enumerate(table["rows"][1:], start=1):
                sheet.write_row(r, 0, row, body)
    return output


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, help="Override the published workbook path")
    parser.add_argument("--data-json", type=Path, help="Write workbook values/layout as JSON without exporting Excel")
    args = parser.parse_args()
    if args.data_json is not None:
        args.data_json.parent.mkdir(parents=True, exist_ok=True)
        args.data_json.write_text(json.dumps(workbook_data(), ensure_ascii=False, allow_nan=False), encoding="utf-8")
        print(f"Workbook data written to {args.data_json}")
    else:
        print(f"Research workbook written to {export_workbook(output=args.output)}")


if __name__ == "__main__":
    main()
