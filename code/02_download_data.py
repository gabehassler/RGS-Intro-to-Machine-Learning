"""Download raw ACS 5-year estimates, for each vintage in
code/census_config.py, for the Census variables that feed the SoVI (Social
Vulnerability Index) at the tract, county, and PUMA level. See
code/sovi_variables.py for which codes are fetched and why.

Requires a Census API key in the CENSUS_API_KEY environment variable
(free key: https://api.census.gov/data/key_signup.html). Loaded from a
.env file in the repository root if present (see .env.example); if you
already export CENSUS_API_KEY another way (shell profile, direnv, etc.),
that takes precedence and no .env file is needed.

This script only downloads raw ACS variables, keyed by GEOID, for every
state and territory the "acs/acs5" dataset publishes; it does not filter
rows or compute any derived SoVI variables. Run
code/03_build_sovi_variables.py after this to filter to the desired
states/territories and produce the processed SoVI outputs, so changes to
the scope or formulas don't require re-downloading.

Output, per vintage year: data/raw/census_<year>/acs_tract.csv,
data/raw/census_<year>/acs_county.csv, data/raw/census_<year>/acs_puma.csv,
and data/raw/census_<year>/tract_by_state/acs_tract_<state_fips>.csv (one
file per state, combined into acs_tract.csv).
"""

import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))  # find sovi_variables.py when not run from code/

import pandas as pd
import requests
from dotenv import load_dotenv
from tqdm import tqdm

from census_config import DATASET, YEARS
from sovi_variables import HOUSING_COST_BURDEN_CODES, all_acs_codes

load_dotenv()  # does not override a CENSUS_API_KEY already set in the environment

API_KEY = os.environ["CENSUS_API_KEY"]
RAW_DIR = Path("data") / "raw"

# ACS sentinel codes for missing/suppressed estimates; see
# https://www.census.gov/data/developers/data-sets/acs-5year/notes-on-acs-estimate-and-annotation-values.html
ACS_SPECIAL_VALUES = {-666666666, -999999999, -888888888, -222222222, -333333333, -555555555}

GEO_COLUMN_RENAME = {
    "state": "STATE",
    "county": "COUNTY",
    "tract": "TRACT",
    "public use microdata area": "PUBLIC_USE_MICRODATA_AREA",
}

# The Census API rejects a `get` with more than 50 variables (including NAME),
# so requests for >49 codes must be split and merged on the geography columns.
MAX_CODES_PER_REQUEST = 49


def census_get(year, codes, for_geo, in_geo=None):
    """Query the Census API directly (replaces the `censusdis` package, which
    pulls in Fiona/GDAL/pyarrow/rasterio for shapefile features this script
    never uses, just to make this same HTTP call under the hood)."""
    chunks = [codes[i : i + MAX_CODES_PER_REQUEST] for i in range(0, len(codes), MAX_CODES_PER_REQUEST)] or [[]]
    df = None
    for chunk in chunks:
        params = {"get": ",".join(["NAME"] + chunk), "for": for_geo, "key": API_KEY}
        if in_geo:
            params["in"] = in_geo
        response = requests.get(f"https://api.census.gov/data/{year}/{DATASET}", params=params)
        response.raise_for_status()
        header, *rows = response.json()
        chunk_df = pd.DataFrame(rows, columns=header).rename(columns=GEO_COLUMN_RENAME)
        if df is None:
            df = chunk_df
        else:
            geo_columns = [c for c in chunk_df.columns if c in GEO_COLUMN_RENAME.values()]
            df = df.merge(chunk_df.drop(columns="NAME"), on=geo_columns).copy()
    value_columns = [c for c in df.columns if c not in GEO_COLUMN_RENAME.values() and c != "NAME"]
    df[value_columns] = df[value_columns].apply(pd.to_numeric)
    df[value_columns] = df[value_columns].mask(df[value_columns].isin(ACS_SPECIAL_VALUES))
    # Column-by-column dtype conversion above leaves the frame internally
    # fragmented (one block per column); consolidate before returning so
    # later column assignments (e.g. GEOID) don't trigger a PerformanceWarning.
    return df.copy()


def all_state_fips(year):
    """Every state/territory FIPS code this dataset vintage publishes."""
    df = census_get(year, [], for_geo="state:*")
    return sorted(df["STATE"])


def download_tract(year, tract_by_state_dir):
    codes = all_acs_codes(year, HOUSING_COST_BURDEN_CODES)
    tract_by_state_dir.mkdir(parents=True, exist_ok=True)
    frames = []
    for fips in tqdm(all_state_fips(year), desc=f"Downloading tract-level data ({year})"):
        df = census_get(year, codes, for_geo="tract:*", in_geo=f"state:{fips} county:*")
        df["GEOID"] = df["STATE"] + df["COUNTY"] + df["TRACT"]
        df = df[["GEOID", "NAME"] + codes]
        df.to_csv(tract_by_state_dir / f"acs_tract_{fips}.csv", index=False)
        frames.append(df)
        time.sleep(0.2)
    return pd.concat(frames, ignore_index=True)


def download_county(year):
    codes = all_acs_codes(year)
    df = census_get(year, codes, for_geo="county:*", in_geo="state:*")
    df["GEOID"] = df["STATE"] + df["COUNTY"]
    return df[["GEOID", "NAME"] + codes]


def download_puma(year):
    codes = all_acs_codes(year)
    df = census_get(year, codes, for_geo="public use microdata area:*", in_geo="state:*")
    df["GEOID"] = df["STATE"] + df["PUBLIC_USE_MICRODATA_AREA"]
    return df[["GEOID", "NAME"] + codes]


def save(df, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)


for year in YEARS:
    output_dir = RAW_DIR / f"census_{year}"

    print(f"Downloading tract-level data ({year})...")
    save(download_tract(year, output_dir / "tract_by_state"), output_dir / "acs_tract.csv")

    print(f"Downloading county-level data ({year})...")
    save(download_county(year), output_dir / "acs_county.csv")

    print(f"Downloading PUMA-level data ({year})...")
    save(download_puma(year), output_dir / "acs_puma.csv")
