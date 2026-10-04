"""Download raw ACS 2020-2024 5-year estimates for the Census variables that
feed the SoVI (Social Vulnerability Index) at the tract, county, and PUMA
level. See code/sovi_variables.py for which codes are fetched and why.

Requires a Census API key in the CENSUS_API_KEY environment variable
(free key: https://api.census.gov/data/key_signup.html). Loaded from a
.env file in the repository root if present (see .env.example); if you
already export CENSUS_API_KEY another way (shell profile, direnv, etc.),
that takes precedence and no .env file is needed.

This script only downloads raw ACS variables, keyed by GEOID; it does not
compute any derived SoVI variables. Run code/03_build_sovi_variables.py
after this to produce the processed SoVI outputs, so changes to the SoVI
formulas don't require re-downloading.

Output: data/raw/acs_tract.csv, data/raw/acs_county.csv, data/raw/acs_puma.csv.
"""

import os
import time
from pathlib import Path

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

# 50 states + DC. ACS "acs/acs5" also publishes Puerto Rico and other
# territories; these are excluded since they weren't part of the requested
# scope.
STATE_FIPS = [
    "01", "02", "04", "05", "06", "08", "09", "10", "11", "12", "13", "15",
    "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27",
    "28", "29", "30", "31", "32", "33", "34", "35", "36", "37", "38", "39",
    "40", "41", "42", "44", "45", "46", "47", "48", "49", "50", "51", "53",
    "54", "55", "56",
]


def download_tract():
    codes = all_acs_codes(HOUSING_COST_BURDEN_CODES)
    frames = []
    for fips in tqdm(STATE_FIPS, desc="Downloading tract-level data"):
        frames.append(ced.download(
            dataset=DATASET, vintage=VINTAGE,
            download_variables=["NAME"] + codes,
            state=fips, county="*", tract="*",
            api_key=API_KEY,
        ))
        time.sleep(0.2)
    df = pd.concat(frames, ignore_index=True)
    df["GEOID"] = df["STATE"] + df["COUNTY"] + df["TRACT"]
    return df[["GEOID", "NAME"] + codes]


def download_county():
    codes = all_acs_codes()
    df = ced.download(
        dataset=DATASET, vintage=VINTAGE,
        download_variables=["NAME"] + codes,
        state="*", county="*",
        api_key=API_KEY,
    )
    df = df[df["STATE"].isin(STATE_FIPS)]
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
    df = df[df["STATE"].isin(STATE_FIPS)]
    df["GEOID"] = df["STATE"] + df["PUBLIC_USE_MICRODATA_AREA"]
    return df[["GEOID", "NAME"] + codes]


def save(df, name):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_DIR / name, index=False)


def main():
    save(download_tract(), "acs_tract.csv")

    print("Downloading county-level data...")
    save(download_county(), "acs_county.csv")

    print("Downloading PUMA-level data...")
    save(download_puma(), "acs_puma.csv")


if __name__ == "__main__":
    main()
