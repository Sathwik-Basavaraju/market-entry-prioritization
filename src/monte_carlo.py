"""Monte Carlo sensitivity: perturb weights, recompute ranking each run.

Method: for each run, multiply each base weight by exp(N(0, 0.30))
(lognormal perturbation, sigma = 0.30), then renormalise to sum 1.0.
Seed fixed at 42, n_runs = 2,000. This tests sensitivity to the
author-set weights -- it does NOT simulate demand, costs, or market
outcomes, and it is not a forecast.

Outputs per metro: mean rank, rank min/max, share of runs in the top 3,
plus the share of runs where the base top-3 SET (order ignored) is
unchanged.
"""
import numpy as np
import pandas as pd

from scoring_model import BASE_WEIGHTS, INDICATORS, normalise

SEED = 42
N_RUNS = 2000
SIGMA = 0.30


def run_monte_carlo(df: pd.DataFrame, n_runs: int = N_RUNS, seed: int = SEED,
                    sigma: float = SIGMA) -> dict:
    rng = np.random.default_rng(seed)
    norm = normalise(df)
    metros = list(norm["metro"])
    norm_matrix = np.column_stack([norm[c + "_norm"].to_numpy() for c in INDICATORS])
    base_weights = np.array([BASE_WEIGHTS[c] for c in INDICATORS], dtype=float)

    base = norm.copy()
    base["composite_score"] = norm_matrix @ base_weights
    base_ranking = base.sort_values("composite_score", ascending=False)["metro"].tolist()
    base_top3_set = set(base_ranking[:3])

    ranks = np.zeros((n_runs, len(metros)), dtype=int)  # rows=runs, cols=metros in df order
    top3_hits = np.zeros(len(metros), dtype=int)
    top3_set_unchanged = 0
    # Map metro position in df order -> position in sorted results is handled
    # by ranking scores per run.
    for i in range(n_runs):
        perturbed = base_weights * np.exp(rng.normal(0.0, sigma, size=len(base_weights)))
        perturbed = perturbed / perturbed.sum()
        scores = norm_matrix @ perturbed
        order = np.argsort(-scores)  # indices into df order, best first
        rank_of = np.empty(len(metros), dtype=int)
        rank_of[order] = np.arange(1, len(metros) + 1)
        ranks[i] = rank_of
        top3_hits[order[:3]] += 1
        if set(np.array(metros)[order[:3]]) == base_top3_set:
            top3_set_unchanged += 1

    per_metro = pd.DataFrame({
        "metro": metros,
        "mean_rank": ranks.mean(axis=0).round(3),
        "rank_min": ranks.min(axis=0),
        "rank_max": ranks.max(axis=0),
        "pct_runs_in_top3": (top3_hits / n_runs * 100).round(2),
        "base_rank": [base_ranking.index(m) + 1 for m in metros],
    }).sort_values("base_rank").reset_index(drop=True)

    summary = {
        "n_runs": n_runs,
        "seed": seed,
        "sigma": sigma,
        "method": "lognormal weight perturbation exp(N(0, 0.30)), renormalised to sum 1.0",
        "base_top3": base_top3_set and base_ranking[:3],
        "pct_runs_base_top3_set_unchanged": round(top3_set_unchanged / n_runs * 100, 2),
        "per_metro": per_metro,
    }
    return summary


if __name__ == "__main__":
    from pathlib import Path
    df = pd.read_csv(Path(__file__).resolve().parents[1] / "data" / "metro_indicators.csv")
    s = run_monte_carlo(df)
    print(f"Base top 3: {s['base_top3']}")
    print(f"Top-3 set unchanged: {s['pct_runs_base_top3_set_unchanged']}% of {s['n_runs']} runs")
    print(s["per_metro"].to_string(index=False))
