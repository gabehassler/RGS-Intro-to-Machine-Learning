"""Compute the SoVI (Social Vulnerability Index) input variables from the raw
ACS data downloaded by code/02_download_data.py. See code/sovi_variables.py
for the formulas.

Run code/02_download_data.py first to produce the raw inputs this script
reads. This script only transforms already-downloaded data, so changing a
SoVI formula does not require re-downloading. It also filters the raw data
(which covers every state/territory "acs/acs5" publishes) down to the
desired scope.

Output, per vintage year in code/census_config.py: data/processed/sovi_tract_<year>.csv,
data/processed/sovi_county_<year>.csv, data/processed/sovi_puma_<year>.csv.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))  # find sovi_variables.py when not run from code/

import numpy as np
import pandas as pd

from census_config import YEARS
from sovi_variables import OUTPUT_COLUMNS, SOVI_VARIABLES, limited_english_codes

RAW_DIR = Path("data") / "raw"
OUTPUT_DIR = Path("data") / "processed"

# 50 states + DC. The raw ACS data also includes Puerto Rico and could
# include other territories in the future; these are excluded here since
# they weren't part of the requested scope. Adjust this list to change scope.
STATE_FIPS = [
    "01", "02", "04", "05", "06", "08", "09", "10", "11", "12", "13", "15",
    "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27",
    "28", "29", "30", "31", "32", "33", "34", "35", "36", "37", "38", "39",
    "40", "41", "42", "44", "45", "46", "47", "48", "49", "50", "51", "53",
    "54", "55", "56",
]


def add_sovi_variables(df):
    for name, (num_cols, den_cols, mult) in SOVI_VARIABLES.items():
        numer = df[num_cols].sum(axis=1)
        if den_cols is None:
            df[name] = numer
        else:
            denom = df[den_cols].sum(axis=1)
            df[name] = np.where(denom == 0, np.nan, numer / denom * mult)
    return df


def add_limited_english(df, year):
    numer_cols, denom_cols = limited_english_codes(year)
    numer = df[numer_cols].sum(axis=1)
    denom = df[denom_cols].sum(axis=1)
    df["pct_limited_english_household"] = np.where(denom == 0, np.nan, numer / denom * 100)
    return df


def add_housing_burden(df):
    burdened = df[
        ["B25070_009E", "B25070_010E", "B25091_010E", "B25091_011E",
         "B25091_021E", "B25091_022E"]
    ].sum(axis=1)
    renter_specified = df["B25070_001E"] - df["B25070_011E"]
    owner_specified = df["B25091_001E"] - df["B25091_012E"] - df["B25091_023E"]
    denom = renter_specified + owner_specified
    df["pct_housing_cost_burdened"] = np.where(denom == 0, np.nan, burdened / denom * 100)
    return df


def read_raw(raw_dir, name):
    df = pd.read_csv(raw_dir / name, dtype={"GEOID": str})
    return df[df["GEOID"].str[:2].isin(STATE_FIPS)].copy()


def build_tract(raw_dir, year):
    df = read_raw(raw_dir, "acs_tract.csv")
    df = add_sovi_variables(df)
    df = add_limited_english(df, year)
    df = add_housing_burden(df)
    return df[["GEOID", "NAME"] + OUTPUT_COLUMNS + ["pct_housing_cost_burdened"]]


def build_county(raw_dir, year):
    df = read_raw(raw_dir, "acs_county.csv")
    df = add_sovi_variables(df)
    df = add_limited_english(df, year)
    return df[["GEOID", "NAME"] + OUTPUT_COLUMNS]


def build_puma(raw_dir, year):
    df = read_raw(raw_dir, "acs_puma.csv")
    df = add_sovi_variables(df)
    df = add_limited_english(df, year)
    return df[["GEOID", "NAME"] + OUTPUT_COLUMNS]


def save(df, name):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_DIR / name, index=False)


for year in YEARS:
    raw_dir = RAW_DIR / f"census_{year}"
    save(build_tract(raw_dir, year), f"sovi_tract_{year}.csv")
    save(build_county(raw_dir, year), f"sovi_county_{year}.csv")
    save(build_puma(raw_dir, year), f"sovi_puma_{year}.csv")
