"""Build outputs/market_entry_model.xlsx with openpyxl."""
from pathlib import Path

import pandas as pd
from openpyxl import Workbook
from openpyxl.styles import Font
from openpyxl.utils import get_column_letter

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def _write_sheet(wb: Workbook, title: str, df: pd.DataFrame, note: str | None = None):
    ws = wb.create_sheet(title)
    if note:
        ws.append([note])
        ws["A1"].font = Font(italic=True)
    ws.append(list(df.columns))
    for cell in ws[ws.max_row]:
        cell.font = Font(bold=True)
    for row in df.itertuples(index=False):
        ws.append(list(row))
    for col in range(1, ws.max_column + 1):
        width = max(len(str(ws.cell(row=r, column=col).value or "")) for r in range(1, ws.max_row + 1))
        ws.column_dimensions[get_column_letter(col)].width = min(max(width + 2, 14), 52)
    ws.freeze_panes = ws.cell(row=3 if note else 2, column=1)
    return ws


def build_workbook(scored: pd.DataFrame, mc: dict, out_path: Path | None = None) -> Path:
    from scoring_model import BASE_WEIGHTS, DIMENSIONS
    out = out_path or PROJECT_ROOT / "outputs" / "market_entry_model.xlsx"
    out.parent.mkdir(parents=True, exist_ok=True)
    wb = Workbook()
    wb.remove(wb.active)

    scores_cols = ["rank", "metro", "composite_score"] + \
        [c for c in scored.columns if c.endswith("_norm")] + \
        ["pop_growth_pct", "median_hh_income_usd", "bachelor_plus_pct",
         "median_hourly_wage_usd", "office_rent_usd_sqft_yr",
         "competitors_per_100k", "incumbent_share_pct"]
    _write_sheet(wb, "Scores", scored[scores_cols].round(4),
                 note="ILLUSTRATIVE data only -- not official FRED/BLS/Census values. Scores are 0-1 composites.")
    weights_df = pd.DataFrame([
        {"dimension": dim, "indicator": ind, "weight": BASE_WEIGHTS[ind],
         "direction": "higher=better" if ind in
                      ["pop_growth_pct", "median_hh_income_usd", "bachelor_plus_pct"]
                      else "lower=better"}
        for dim, inds in DIMENSIONS.items() for ind in inds
    ])
    _write_sheet(wb, "Weights", weights_df,
                 note="Weights are a documented author exercise, NOT a stakeholder vote. Sum = 1.0.")
    mc_df = mc["per_metro"].copy()
    mc_df.insert(0, "note",
                 f"Monte Carlo: {mc['n_runs']} runs, seed {mc['seed']}; "
                 f"base top-3 set unchanged in {mc['pct_runs_base_top3_set_unchanged']}% of runs")
    _write_sheet(wb, "Monte Carlo", mc_df,
                 note="Weight-perturbation sensitivity only -- not a demand or revenue forecast.")
    raw = scored.drop(columns=[c for c in scored.columns if c.endswith("_norm") or c in ("composite_score", "rank")])
    _write_sheet(wb, "Indicators", raw,
                 note="ILLUSTRATIVE indicator values (author-set). See DATA_SOURCES.md.")
    notes = pd.DataFrame([{"item": "Data", "detail": "Illustrative dataset; Census no-key attempt redirected to missing_key page; FRED no-key CSV is national-only."},
                          {"item": "Method", "detail": "Min-max normalisation; composite = sum(weight x normalised indicator)."},
                          {"item": "Monte Carlo", "detail": mc["method"]},
                          {"item": "Limitation", "detail": "Do not use for a real entry decision without replacing illustrative data with cited official data."}])
    _write_sheet(wb, "README_Notes", notes)
    wb.save(out)
    return out


if __name__ == "__main__":
    import sys
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from monte_carlo import run_monte_carlo
    from scoring_model import score
    df = pd.read_csv(PROJECT_ROOT / "data" / "metro_indicators.csv")
    scored = score(df)
    mc = run_monte_carlo(df)
    print(build_workbook(scored, mc))
