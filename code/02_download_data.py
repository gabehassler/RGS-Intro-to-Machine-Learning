"""Download raw ACS 2020-2024 5-year estimates for the Census variables that
feed the SoVI (Social Vulnerability Index) at the tract, county, and PUMA
level. See code/sovi_variables.py for which codes are fetched and why.

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

Output: data/raw/acs_tract.csv, data/raw/acs_county.csv, data/raw/acs_puma.csv,
and data/raw/tract_by_state/acs_tract_<state_fips>.csv (one file per state,
combined into acs_tract.csv).
"""

import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))  # find sovi_variables.py when not run from code/

import censusdis.data as ced
import pandas as pd
from dotenv import load_dotenv
from tqdm import tqdm

from sovi_variables import HOUSING_COST_BURDEN_CODES, all_acs_codes

load_dotenv()  # does not override a CENSUS_API_KEY already set in the environment

DATASET = "acs/acs5"
VINTAGE = 2024
API_KEY = os.environ["CENSUS_API_KEY"]
OUTPUT_DIR = Path("data") / "raw"
TRACT_BY_STATE_DIR = OUTPUT_DIR / "tract_by_state"


def all_state_fips():
    """Every state/territory FIPS code this dataset vintage publishes."""
    df = ced.download(
        dataset=DATASET, vintage=VINTAGE,
        download_variables=["NAME"],
        state="*",
        api_key=API_KEY,
    )
    return sorted(df["STATE"])


def download_tract():
    codes = all_acs_codes(HOUSING_COST_BURDEN_CODES)
    TRACT_BY_STATE_DIR.mkdir(parents=True, exist_ok=True)
    frames = []
    for fips in tqdm(all_state_fips(), desc="Downloading tract-level data"):
        df = ced.download(
            dataset=DATASET, vintage=VINTAGE,
            download_variables=["NAME"] + codes,
            state=fips, county="*", tract="*",
            api_key=API_KEY,
        )
        df["GEOID"] = df["STATE"] + df["COUNTY"] + df["TRACT"]
        df = df[["GEOID", "NAME"] + codes]
        df.to_csv(TRACT_BY_STATE_DIR / f"acs_tract_{fips}.csv", index=False)
        frames.append(df)
        time.sleep(0.2)
    return pd.concat(frames, ignore_index=True)


def download_county():
    codes = all_acs_codes()
    df = ced.download(
        dataset=DATASET, vintage=VINTAGE,
        download_variables=["NAME"] + codes,
        state="*", county="*",
        api_key=API_KEY,
    )
    df["GEOID"] = df["STATE"] + df["COUNTY"]
    return df[["GEOID", "NAME"] + codes]


def download_puma():
    codes = all_acs_codes()
    df = ced.download(
        dataset=DATASET, vintage=VINTAGE,
        download_variables=["NAME"] + codes,
        state="*", public_use_microdata_area="*",
        api_key=API_KEY,
    )
    df["GEOID"] = df["STATE"] + df["PUBLIC_USE_MICRODATA_AREA"]
    return df[["GEOID", "NAME"] + codes]


def save(df, name):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_DIR / name, index=False)


save(download_tract(), "acs_tract.csv")

print("Downloading county-level data...")
save(download_county(), "acs_county.csv")

print("Downloading PUMA-level data...")
save(download_puma(), "acs_puma.csv")
