"""Weighted scoring model: min-max normalisation, weights, ranking.

Direction (documented, not assumed):
  higher = better: pop_growth_pct, median_hh_income_usd, bachelor_plus_pct
  lower  = better: median_hourly_wage_usd, office_rent_usd_sqft_yr,
                   competitors_per_100k, incumbent_share_pct
Min-max normalisation maps each indicator to [0, 1] on the observed
10-metro range. A constant column would map to 0.5 (guard against /0).
"""
import pandas as pd

# Base weights: a documented EXERCISE set by the author, NOT a stakeholder
# vote. Dimension rationale is in README.md and the Weights sheet.
BASE_WEIGHTS = {
    # Demand 0.45 -- entry is demand-led; split equally across 3 indicators.
    "pop_growth_pct": 0.15,
    "median_hh_income_usd": 0.15,
    "bachelor_plus_pct": 0.15,
    # Labor cost 0.30 -- operating cost is the second constraint.
    "median_hourly_wage_usd": 0.15,
    "office_rent_usd_sqft_yr": 0.15,
    # Competition 0.25 -- a crowded market slows share gains.
    "competitors_per_100k": 0.125,
    "incumbent_share_pct": 0.125,
}

HIGHER_BETTER = ["pop_growth_pct", "median_hh_income_usd", "bachelor_plus_pct"]
LOWER_BETTER = ["median_hourly_wage_usd", "office_rent_usd_sqft_yr",
                "competitors_per_100k", "incumbent_share_pct"]
INDICATORS = HIGHER_BETTER + LOWER_BETTER

DIMENSIONS = {
    "Demand": ["pop_growth_pct", "median_hh_income_usd", "bachelor_plus_pct"],
    "Labor cost": ["median_hourly_wage_usd", "office_rent_usd_sqft_yr"],
    "Competition": ["competitors_per_100k", "incumbent_share_pct"],
}


def normalise(df: pd.DataFrame) -> pd.DataFrame:
    out = df.copy()
    for col in INDICATORS:
        lo, hi = df[col].min(), df[col].max()
        if hi == lo:
            out[col + "_norm"] = 0.5
        elif col in HIGHER_BETTER:
            out[col + "_norm"] = (df[col] - lo) / (hi - lo)
        else:
            out[col + "_norm"] = (hi - df[col]) / (hi - lo)
    return out


def score(df: pd.DataFrame, weights: dict | None = None) -> pd.DataFrame:
    """Return metros with normalised columns, composite score, and rank."""
    weights = weights or BASE_WEIGHTS
    assert abs(sum(weights.values()) - 1.0) < 1e-9, f"weights sum to {sum(weights.values())}"
    norm = normalise(df)
    norm["composite_score"] = sum(norm[c + "_norm"] * w for c, w in weights.items())
    result = norm.sort_values("composite_score", ascending=False).reset_index(drop=True)
    result["rank"] = range(1, len(result) + 1)
    return result


if __name__ == "__main__":
    from pathlib import Path
    df = pd.read_csv(Path(__file__).resolve().parents[1] / "data" / "metro_indicators.csv")
    print(score(df)[["rank", "metro", "composite_score"]].to_string(index=False))
