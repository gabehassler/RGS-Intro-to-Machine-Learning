"""Compute the SoVI (Social Vulnerability Index) input variables from the raw
ACS data downloaded by code/02_download_data.py. See code/sovi_variables.py
for the formulas.

Run code/02_download_data.py first to produce the raw inputs this script
reads. This script only transforms already-downloaded data, so changing a
SoVI formula does not require re-downloading.

Output: data/processed/sovi_tract.csv, data/processed/sovi_county.csv,
data/processed/sovi_puma.csv.
"""

from pathlib import Path

import numpy as np
import pandas as pd

from sovi_variables import OUTPUT_COLUMNS, SOVI_VARIABLES

RAW_DIR = Path("data") / "raw"
OUTPUT_DIR = Path("data") / "processed"


def add_sovi_variables(df):
    for name, (num_cols, den_cols, mult) in SOVI_VARIABLES.items():
        numer = df[num_cols].sum(axis=1)
        if den_cols is None:
            df[name] = numer
        else:
            denom = df[den_cols].sum(axis=1)
            df[name] = np.where(denom == 0, np.nan, numer / denom * mult)
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


def read_raw(name):
    return pd.read_csv(RAW_DIR / name, dtype={"GEOID": str})


def build_tract():
    df = read_raw("acs_tract.csv")
    df = add_sovi_variables(df)
    df = add_housing_burden(df)
    return df[["GEOID", "NAME"] + OUTPUT_COLUMNS + ["pct_housing_cost_burdened"]]


def build_county():
    df = read_raw("acs_county.csv")
    df = add_sovi_variables(df)
    return df[["GEOID", "NAME"] + OUTPUT_COLUMNS]


def build_puma():
    df = read_raw("acs_puma.csv")
    df = add_sovi_variables(df)
    return df[["GEOID", "NAME"] + OUTPUT_COLUMNS]


def save(df, name):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_DIR / name, index=False)


def main():
    save(build_tract(), "sovi_tract.csv")
    save(build_county(), "sovi_county.csv")
    save(build_puma(), "sovi_puma.csv")


if __name__ == "__main__":
    main()
