"""End-to-end pipeline: fetch -> score -> Monte Carlo -> charts -> workbook -> metrics.json.

Run from the project folder:  python3 src/run_all.py
All numbers in metrics.json, README.md, and the memo come from this run.
"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))

from build_workbook import build_workbook
from fetch_data import fetch_data
from monte_carlo import N_RUNS, SEED, run_monte_carlo
from scoring_model import BASE_WEIGHTS, INDICATORS, score

PROJECT_ROOT = Path(__file__).resolve().parents[1]


def chart_ranking(scored: pd.DataFrame, path: Path):
    data = scored.sort_values("composite_score")
    plt.figure(figsize=(10, 6))
    plt.barh(data["metro"], data["composite_score"])
    plt.xlabel("Composite score (0-1)")
    plt.title("Market-entry composite score by metro (illustrative data)")
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def chart_stability(mc: dict, path: Path):
    data = mc["per_metro"].sort_values("pct_runs_in_top3", ascending=True)
    plt.figure(figsize=(10, 6))
    plt.barh(data["metro"], data["pct_runs_in_top3"])
    plt.xlabel("% of Monte Carlo runs in top 3 (2,000 runs, seed 42)")
    plt.title("Rank stability: % of runs in top 3")
    plt.tight_layout()
    plt.savefig(path, dpi=150)
    plt.close()


def main():
    df, fetch_log = fetch_data()
    scored = score(df)
    mc = run_monte_carlo(df)

    charts_dir = PROJECT_ROOT / "outputs" / "charts"
    charts_dir.mkdir(parents=True, exist_ok=True)
    chart_ranking(scored, charts_dir / "composite_ranking.png")
    chart_stability(mc, charts_dir / "monte_carlo_stability.png")

    workbook = build_workbook(scored, mc)

    per_metro = mc["per_metro"]
    metrics = {
        "project": "Market-Entry Prioritization Model with Monte Carlo Sensitivity Analysis",
        "data_source": "illustrative (author-set, NOT official FRED/BLS/Census values)",
        "fetch_attempts": fetch_log["attempts"],
        "n_metros": int(len(df)),
        "metros": list(df["metro"]),
        "indicators": INDICATORS,
        "base_weights": BASE_WEIGHTS,
        "weights_note": "Documented author exercise, NOT a stakeholder vote; weights sum to 1.0",
        "base_ranking": [
            {"rank": int(r.rank), "metro": r.metro, "composite_score": round(float(r.composite_score), 4)}
            for r in scored.itertuples()
        ],
        "monte_carlo": {
            "n_runs": mc["n_runs"],
            "seed": mc["seed"],
            "sigma": mc["sigma"],
            "method": mc["method"],
            "base_top3": mc["base_top3"],
            "pct_runs_base_top3_set_unchanged": mc["pct_runs_base_top3_set_unchanged"],
            "per_metro_top3_pct": {
                row.metro: float(row.pct_runs_in_top3) for row in per_metro.itertuples()
            },
            "per_metro": [
                {"metro": row.metro, "base_rank": int(row.base_rank),
                 "mean_rank": float(row.mean_rank), "rank_min": int(row.rank_min),
                 "rank_max": int(row.rank_max),
                 "pct_runs_in_top3": float(row.pct_runs_in_top3)}
                for row in per_metro.itertuples()
            ],
        },
        "outputs": {
            "workbook": str(workbook.relative_to(PROJECT_ROOT)),
            "charts": ["outputs/charts/composite_ranking.png", "outputs/charts/monte_carlo_stability.png"],
            "indicator_csv": "data/metro_indicators.csv",
        },
    }
    metrics_path = PROJECT_ROOT / "outputs" / "metrics.json"
    metrics_path.write_text(json.dumps(metrics, indent=2))
    print(f"Metros: {metrics['n_metros']}")
    print("Base ranking:")
    for item in metrics["base_ranking"]:
        print(f"  {item['rank']}. {item['metro']} — {item['composite_score']}")
    print(f"Monte Carlo: {mc['n_runs']} runs, seed {mc['seed']}")
    print(f"Base top-3 set unchanged: {mc['pct_runs_base_top3_set_unchanged']}% of runs")
    print("Per-metro % runs in top 3:")
    for row in per_metro.itertuples():
        print(f"  {row.metro}: {row.pct_runs_in_top3}% (mean rank {row.mean_rank}, range {row.rank_min}-{row.rank_max})")
    print(f"Wrote {metrics_path} and {workbook}")
    return metrics


if __name__ == "__main__":
    main()
