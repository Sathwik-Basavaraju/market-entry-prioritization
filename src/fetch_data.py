"""Attempt public no-key data sources, then fall back to illustrative data.

Attempts (run 2026-11-04, documented in DATA_SOURCES.md):
  1. Census API, no key:
     https://api.census.gov/data/2023/acs/acs5?get=NAME,B19013_001E
     &for=metropolitan%20statistical%20area:*
     -> HTTP 302 to https://api.census.gov/data/missing_key.html
        with header X-DataWebAPI-KeyError: 1. A key is required in
        this environment, so no metro data could be retrieved.
  2. FRED graph CSV, no key:
     https://fred.stlouisfed.org/graph/fredgraph.csv?id=UNRATE
     -> Succeeds, but UNRATE is a single NATIONAL unemployment series,
        not metro-level demand / labor-cost / competition indicators,
        so it cannot populate this model.

Result: `fetch_data()` returns the illustrative dataset with
`data_source` flagged, and writes data/metro_indicators.csv.
Nothing in the output is presented as an official statistic.
"""
import json
import subprocess
from pathlib import Path

from generate_illustrative_data import build_illustrative_data

PROJECT_ROOT = Path(__file__).resolve().parents[1]

CENSUS_URL = (
    "https://api.census.gov/data/2023/acs/acs5"
    "?get=NAME,B19013_001E&for=metropolitan%20statistical%20area:*"
)
FRED_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=UNRATE"


def _probe(url: str, timeout: int = 15) -> dict:
    """Probe with curl (no redirect following) so a key redirect is visible.

    urllib hung in this sandbox; curl via the sandbox proxy returns
    promptly, so the probe uses curl and never blocks the pipeline.
    """
    try:
        out = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code} %{redirect_url}",
             "--max-time", str(timeout), url],
            capture_output=True, text=True, timeout=timeout + 5)
        code, _, redirect = out.stdout.strip().partition(" ")
        return {"url": url, "status": code, "redirect_url": redirect or None,
                "key_error": "yes (redirect to missing_key.html)" if "missing_key" in redirect else None}
    except Exception as exc:
        return {"url": url, "status": None, "error": str(exc)}


def fetch_data(output_csv: Path | None = None) -> tuple:
    """Probe public sources, then write the illustrative fallback CSV."""
    attempts = [_probe(CENSUS_URL), _probe(FRED_URL)]
    # FRED national UNRATE alone cannot supply metro indicators, and
    # Census requires a key here, so the fallback is used in all cases
    # where metro-level data was not actually retrieved.
    df = build_illustrative_data()
    out = output_csv or PROJECT_ROOT / "data" / "metro_indicators.csv"
    out.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out, index=False)
    log = {
        "attempts": attempts,
        "used": "illustrative",
        "reason": ("Census no-key request redirected to missing_key page; "
                   "FRED no-key CSV is national-level only (UNRATE)"),
        "output_csv": str(out),
        "n_metros": int(len(df)),
    }
    return df, log


if __name__ == "__main__":
    df, log = fetch_data()
    print(json.dumps(log, indent=2, default=str))
    print(df.to_string(index=False))
