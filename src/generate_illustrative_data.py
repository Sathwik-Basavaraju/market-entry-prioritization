"""Generate the clearly-labelled illustrative indicator dataset.

This dataset is ILLUSTRATIVE ONLY. It is not FRED, BLS, or Census data,
and none of its values should be quoted as official statistics.
It exists so the scoring model and Monte Carlo code run end-to-end
after the public no-key attempts documented in DATA_SOURCES.md failed
to return usable metro-level indicators (Census returned a missing-key
redirect; FRED's no-key CSV is national-level only, e.g. UNRATE).

Values below are round, author-chosen magnitudes in plausible ranges
for a teaching model -- they encode relative differences between metros,
not measured facts. Replace this file's table with real, cited data
before using any ranking for a real market-entry decision.
"""
import pandas as pd

# Columns: metro, then 7 indicators.
# demand: pop_growth_pct (higher=better), median_hh_income_usd (higher=better),
#         bachelor_plus_pct (higher=better)
# labor_cost: median_hourly_wage_usd (lower=better), office_rent_usd_sqft_yr (lower=better)
# competition: competitors_per_100k (lower=better), incumbent_share_pct (lower=better)
ROWS = [
    # metro, pop_growth, income, bachelor, wage, rent, competitors, incumbent_share
    ("Seattle, WA", 1.8, 115000, 48, 32.0, 42, 6.2, 38),
    ("Austin, TX", 2.6, 98000, 46, 27.0, 34, 7.8, 30),
    ("Denver, CO", 1.5, 102000, 45, 28.5, 32, 6.5, 33),
    ("Atlanta, GA", 1.9, 88000, 38, 25.0, 28, 8.4, 35),
    ("Dallas, TX", 2.2, 92000, 36, 25.5, 30, 9.1, 40),
    ("Phoenix, AZ", 2.4, 84000, 32, 24.0, 26, 7.2, 28),
    ("Raleigh, NC", 2.1, 101000, 47, 26.5, 29, 5.4, 26),
    ("Nashville, TN", 2.0, 90000, 37, 24.5, 27, 6.8, 31),
    ("Boston, MA", 0.9, 118000, 50, 33.5, 48, 5.9, 42),
    ("Chicago, IL", 0.6, 94000, 39, 29.0, 31, 8.9, 44),
]

COLUMNS = [
    "metro", "pop_growth_pct", "median_hh_income_usd", "bachelor_plus_pct",
    "median_hourly_wage_usd", "office_rent_usd_sqft_yr",
    "competitors_per_100k", "incumbent_share_pct",
]


def build_illustrative_data() -> pd.DataFrame:
    df = pd.DataFrame(ROWS, columns=COLUMNS)
    df["data_source"] = "illustrative (author-set, NOT official FRED/BLS/Census)"
    return df


if __name__ == "__main__":
    print(build_illustrative_data().to_string(index=False))
