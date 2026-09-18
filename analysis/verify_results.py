"""Check manuscript precision and independent numerical/artifact consistency."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from PIL import Image
from scipy import stats

ROOT = Path(__file__).resolve().parents[1]
TABLES = ROOT / 'results/tables'
PREDICTORS = ['Cancer_pct', 'Infant_mortality_pct', 'Circulatory_pct', 'Disability_pct', 'Unemployment_pct']
MODELS = ['Baseline - Region + Year', 'Before PCA - 5 original indicators', 'After PCA - PC1 + PC2']
WORKBOOK_TABLES = {
    'RQ1_All_Data': 'data/processed/rq1_all_regions_audited.csv',
    'RQ1_Group_Comparison': 'results/tables/rq1_group_comparison.csv',
    'RQ1_Region_Means': 'results/tables/rq1_region_means.csv',
    'RQ1_Yearly_Means': 'results/tables/rq1_yearly_group_means.csv',
    'RQ2_Exposed_Data': 'data/processed/rq2_exposed_regions_audited.csv',
    'RQ2_PCA_Diagnostics': 'results/tables/rq2_pca_diagnostics.csv',
    'RQ2_PCA_Coefficients': 'results/tables/rq2_pca_component_coefficients.csv',
    'RQ2_PCA_Scores': 'results/tables/rq2_pca_scores.csv',
    'RQ2_Model_Comparison': 'results/tables/rq2_model_comparison.csv',
    'RQ2_OLS_Coefficients': 'results/tables/rq2_ols_coefficients.csv',
    'RQ2_Fitted_Mortality': 'results/tables/rq2_fitted_mortality.csv',
    'RQ1_Boundary_Sensitivity': 'results/tables/rq1_boundary_sensitivity.csv',
    'RQ1_Pre2022_Group_Comparison': 'results/tables/rq1_pre2022_group_comparison.csv',
    'RQ1_Pre2022_Region_Means': 'results/tables/rq1_pre2022_region_means.csv',
    'RQ2_Boundary_Comparison': 'results/tables/rq2_boundary_model_comparison.csv',
    'RQ2_Pre2022_Model_Comparison': 'results/tables/rq2_pre2022_model_comparison.csv',
    'RQ2_Pre2022_Diagnostics': 'results/tables/rq2_pre2022_pca_diagnostics.csv',
    'RQ2_Pre2022_PCA_Coefficients': 'results/tables/rq2_pre2022_pca_component_coefficients.csv',
    'RQ2_Pre2022_PCA_Scores': 'results/tables/rq2_pre2022_pca_scores.csv',
    'RQ2_Pre2022_OLS_Coefficients': 'results/tables/rq2_pre2022_ols_coefficients.csv',
    'RQ2_Pre2022_Fitted_Mortality': 'results/tables/rq2_pre2022_fitted_mortality.csv',
}


def select_row(table, where):
    frame = pd.read_csv(TABLES / table)
    mask = pd.Series(True, index=frame.index)
    for column, value in where.items():
        mask &= frame[column].astype(str).eq(str(value))
    rows = frame.loc[mask]
    assert len(rows) == 1, f'{table}: expected one row for {where}, found {len(rows)}'
    return rows.iloc[0]


def verify_paper(paper=None):
    reference = json.loads((ROOT / 'manuscript/paper_numbers.json').read_text(encoding='utf-8'))
    if paper is not None:
        assert hashlib.sha256(paper.read_bytes()).hexdigest() == reference['manuscript']['sha256'], 'Provided manuscript differs from the recorded final version'
    for check in reference['checks']:
        actual = float(select_row(check['table'], check['where'])[check['column']]) * check['multiplier']
        tolerance = .5 * 10 ** -check['decimals'] if check['decimals'] else 0
        assert abs(actual - check['expected']) <= tolerance + 1e-12, f'Manuscript mismatch: {check}, computed {actual}'
    for check in reference['inequalities']:
        assert float(select_row(check['table'], check['where'])[check['column']]) < check['expected'], str(check)
    for check in reference['ordering']:
        low = select_row(check['table'], {'Model': check['lower_model']})
        high = select_row(check['table'], {'Model': check['higher_model']})
        for column in check['columns']:
            assert low[column] < high[column], f'{check["table"]}: {column} ordering differs from manuscript'
    return len(reference['checks'])


def verify_independent_fits():
    data = pd.read_csv(ROOT / 'data/processed/rq1_all_regions_audited.csv')
    exposed_file = pd.read_csv(ROOT / 'data/processed/rq2_exposed_regions_audited.csv')
    expected = data.loc[data.Project_Group.eq('Exposed-classified')].sort_values(['Region', 'Year']).reset_index(drop=True)
    pd.testing.assert_frame_equal(expected, exposed_file.sort_values(['Region', 'Year']).reset_index(drop=True), check_dtype=False)
    np.testing.assert_allclose(data.Mortality_pct, data.Registered_deaths / data.Population * 100, rtol=0, atol=1e-12)
    for end, prefix in [(2024, 'rq2'), (2021, 'rq2_pre2022')]:
        sample = expected.loc[expected.Year.le(end)].reset_index(drop=True)
        x = sample[PREDICTORS].to_numpy(float)
        z = (x - x.mean(axis=0)) / x.std(axis=0, ddof=0)
        _, singular, vt = np.linalg.svd(z, full_matrices=False)
        if vt[0, 1] < 0:
            vt[0] *= -1
        if vt[1, 3] < 0:
            vt[1] *= -1
        pc = z @ vt[:2].T
        scores = pd.read_csv(TABLES / f'{prefix}_pca_scores.csv')
        np.testing.assert_array_equal(scores[['Region', 'Year']], sample[['Region', 'Year']])
        np.testing.assert_allclose(scores[['PC1', 'PC2']], pc, rtol=1e-10, atol=1e-10)
        coefficients = pd.read_csv(TABLES / f'{prefix}_pca_component_coefficients.csv')
        np.testing.assert_allclose(coefficients[['PC1_component_coefficient', 'PC2_component_coefficient']], vt[:2].T, rtol=1e-10, atol=1e-10)
        ratios = singular ** 2 / (singular ** 2).sum()
        for component in (1, 2):
            value = select_row(f'{prefix}_pca_diagnostics.csv', {'Statistic': f'PC{component} explained variance ratio'})['Value']
            np.testing.assert_allclose(value, ratios[component - 1], rtol=1e-10, atol=1e-12)
        controls = np.column_stack([sample.Year - sample.Year.mean(), sample.Region.eq('Karaganda'), sample.Region.eq('Pavlodar')]).astype(float)
        y = sample.Mortality_pct.to_numpy(float)
        predictions = pd.read_csv(TABLES / f'{prefix}_fitted_mortality.csv')
        for model, extras, fit_column in zip(MODELS, [np.empty((len(sample), 0)), x, pc], ['Fitted_Baseline', 'Fitted_Before_PCA', 'Fitted_After_PCA']):
            design = np.column_stack([np.ones(len(sample)), extras, controls])
            coefficients = np.linalg.lstsq(design, y, rcond=None)[0]
            fitted = design @ coefficients
            np.testing.assert_allclose(predictions[fit_column], fitted, rtol=0, atol=1e-10)
            n, k = design.shape
            sse = float(((y - fitted) ** 2).sum())
            r2 = 1 - sse / ((y - y.mean()) ** 2).sum()
            llf = -n / 2 * (np.log(2 * np.pi) + 1 + np.log(sse / n))
            calculated = [n, k, r2, 1 - (1 - r2) * (n - 1) / (n - k), np.sqrt(sse / n), -2 * llf + 2 * k, -2 * llf + np.log(n) * k]
            row = select_row(f'{prefix}_model_comparison.csv', {'Model': model})
            np.testing.assert_allclose(row[['N', 'Parameters', 'R2', 'Adjusted_R2', 'RMSE', 'AIC', 'BIC']].to_numpy(float), calculated, rtol=1e-10, atol=1e-10)
        region_means = data.loc[data.Year.le(end)].groupby(['Project_Group', 'Region'])[PREDICTORS + ['Mortality_pct']].mean()
        for indicator in PREDICTORS + ['Mortality_pct']:
            exposed = region_means.loc['Exposed-classified', indicator].to_numpy()
            comparison = region_means.loc['Comparison-classified', indicator].to_numpy()
            result = stats.permutation_test((exposed, comparison), lambda a, b: np.mean(a) - np.mean(b), permutation_type='independent', alternative='two-sided', n_resamples=np.inf)
            row = select_row('rq1_boundary_sensitivity.csv', {'Period': f'2011-{end}', 'Indicator': indicator})
            np.testing.assert_allclose(row['Exact_permutation_p_region_means'], result.pvalue, rtol=0, atol=1e-12)
            np.testing.assert_allclose(row['Difference_exposed_minus_comparison'], exposed.mean() - comparison.mean(), rtol=0, atol=1e-12)


def verify_workbook():
    workbook = pd.ExcelFile(ROOT / 'results/research_results.xlsx')
    assert workbook.sheet_names == ['README', *WORKBOOK_TABLES], 'Workbook sheet order/names differ from the required structure'
    for sheet, source in WORKBOOK_TABLES.items():
        csv = pd.read_csv(ROOT / source)
        excel = pd.read_excel(workbook, sheet_name=sheet)
        pd.testing.assert_frame_equal(csv, excel, check_dtype=False, check_exact=False, rtol=1e-12, atol=1e-12, obj=sheet)
    readme = pd.read_excel(workbook, sheet_name='README', header=2).set_index('Item')
    for label, model in zip(['Baseline', 'Original-indicator', 'PCA-reduced'], MODELS):
        row = select_row('rq2_model_comparison.csv', {'Model': model})
        for metric in ['R2', 'RMSE', 'AIC']:
            key = f'{label} {"R²" if metric == "R2" else metric}'
            np.testing.assert_allclose(float(readme.loc[key, 'Value']), float(row[metric]), rtol=1e-12, atol=1e-12)
    return len(WORKBOOK_TABLES)


def verify_figures():
    figures = sorted((ROOT / 'figures').glob('*.png'))
    assert len(figures) == 8, 'Expected six existing and two boundary-sensitivity figures'
    for figure in figures:
        with Image.open(figure) as image:
            image.verify()
            metadata = json.loads(image.info['Description'])
        sources = metadata['source_sha256']
        assert sources, f'{figure.name}: no recorded figure sources'
        for filename, recorded in sources.items():
            canonical = (TABLES / filename).read_text(encoding='utf-8').encode('utf-8')
            assert recorded == hashlib.sha256(canonical).hexdigest(), f'{figure.name} is stale relative to {filename}'
    return len(figures)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--paper', type=Path, help='Optionally verify the source manuscript SHA-256')
    args = parser.parse_args()
    count = verify_paper(args.paper)
    verify_independent_fits()
    sheets = verify_workbook()
    figures = verify_figures()
    print(f'PASS: {count} manuscript numerical targets, six independent OLS fits, independently computed PCA/permutation checks, {sheets} CSV/Excel result sheets, and {figures} figure source hashes.')


if __name__ == '__main__':
    main()
