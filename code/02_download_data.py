"""Download ACS 2020-2024 5-year estimates for the SoVI (Social Vulnerability
Index) input variables at the tract, county, and PUMA level.

Requires a Census API key in the CENSUS_API_KEY environment variable
(free key: https://api.census.gov/data/key_signup.html).

Two of the 29 Table 1 variables are not available from the ACS and are
skipped here:
  - HOSPTPC (hospitals per capita, county-level only): not a Census variable;
    needs a facility-location source such as CMS or HIFLD.
  - QNRRES (nursing home residents per capita): ACS only publishes the
    nursing-facility group-quarters count (table B26103) at the state level,
    not at tract, county, or PUMA.

Output: data/sovi_tract.csv, data/sovi_county.csv, data/sovi_puma.csv.
"""

import os
import time
from pathlib import Path

import censusdis.data as ced
import numpy as np
import pandas as pd

DATASET = "acs/acs5"
VINTAGE = 2024
API_KEY = os.environ["CENSUS_API_KEY"]
OUTPUT_DIR = Path("data")

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

# Each SoVI variable: (numerator ACS codes to sum, denominator ACS codes to
# sum or None for a value used as-is, multiplier). Codes were verified against
# the live ACS 2024 5-year variable metadata (api.census.gov/data/2024/acs/acs5/
# groups/<table>.json) before being hardcoded here.
SOVI_VARIABLES = {
    "QASIAN": (["B02001_005E"], ["B02001_001E"], 100),
    "QBLACK": (["B02001_003E"], ["B02001_001E"], 100),
    "QHISP": (["B03003_003E"], ["B03003_001E"], 100),
    "QNATAM": (["B02001_004E"], ["B02001_001E"], 100),
    "QAGEDEP": (
        [
            "B01001_003E", "B01001_027E",  # under 5 (male, female)
            "B01001_020E", "B01001_021E", "B01001_022E",  # 65+ male
            "B01001_023E", "B01001_024E", "B01001_025E",
            "B01001_044E", "B01001_045E", "B01001_046E",  # 65+ female
            "B01001_047E", "B01001_048E", "B01001_049E",
        ],
        ["B01001_001E"], 100,
    ),
    "QFAM": (["B09002_002E"], ["B09002_001E"], 100),
    "MEDAGE": (["B01002_001E"], None, 1),
    "QSSBEN": (["B19055_002E"], ["B19055_001E"], 100),
    "QPOVTY": (["B17001_002E"], ["B17001_001E"], 100),
    "QRICH": (["B19001_017E"], ["B19001_001E"], 100),
    "PERCAP": (["B19301_001E"], None, 1),
    "QESL": (
        ["C16002_004E", "C16002_007E", "C16002_010E", "C16002_013E"],
        ["C16002_001E"], 100,
    ),
    "QFEMALE": (["B01001_026E"], ["B01001_001E"], 100),
    "QFHH": (["B11001_006E"], ["B11001_001E"], 100),
    "QNOHLTH": (
        [f"B27001_{n:03d}E" for n in
         (5, 8, 11, 14, 17, 20, 23, 26, 29, 33, 36, 39, 42, 45, 48, 51, 54, 57)],
        ["B27001_001E"], 100,
    ),
    "QED12LES": (
        [f"B15003_{n:03d}E" for n in range(2, 17)],
        ["B15003_001E"], 100,
    ),
    "QCVLUN": (["B23025_005E"], ["B23025_003E"], 100),
    "PPUNIT": (["B01001_001E"], ["B25001_001E"], 1),
    "QRENTER": (["B25003_003E"], ["B25003_001E"], 100),
    "MDHSEVAL": (["B25077_001E"], None, 1),
    "MDGRENT": (["B25064_001E"], None, 1),
    "QMOHO": (["B25024_010E"], ["B25024_001E"], 100),
    "QEXTRCT": (
        ["C24030_004E", "C24030_005E", "C24030_031E", "C24030_032E"],
        ["C24030_001E"], 100,
    ),
    "QSERV": (["C24010_019E", "C24010_055E"], ["C24010_001E"], 100),
    "QFEMLBR": (
        [f"B23001_{n:03d}E" for n in
         (90, 97, 104, 111, 118, 125, 132, 139, 146, 153, 160, 165, 170)],
        ["B23001_088E"], 100,
    ),
    "QNOAUTO": (["B25044_003E", "B25044_010E"], ["B25044_001E"], 100),
    "QUNOCCHU": (["B25002_003E"], ["B25002_001E"], 100),
}

# QHSEBRDN ("percent of households spending >40% of income on housing",
# Table 1 marks it tract-level ONLY) needs a denominator that excludes
# "not computed" cells, so it doesn't fit the simple sum/sum pattern above
# and is computed separately in add_housing_burden().
QHSEBRDN_CODES = [
    "B25070_001E", "B25070_009E", "B25070_010E", "B25070_011E",
    "B25091_001E", "B25091_010E", "B25091_011E", "B25091_012E",
    "B25091_021E", "B25091_022E", "B25091_023E",
]

OUTPUT_COLUMNS = [
    "QASIAN", "QBLACK", "QHISP", "QNATAM", "QAGEDEP", "QFAM", "MEDAGE",
    "QSSBEN", "QPOVTY", "QRICH", "PERCAP", "QESL", "QFEMALE", "QFHH",
    "QNOHLTH", "QED12LES", "QCVLUN", "PPUNIT", "QRENTER", "MDHSEVAL",
    "MDGRENT", "QMOHO", "QEXTRCT", "QSERV", "QFEMLBR", "QNOAUTO", "QUNOCCHU",
]


def all_acs_codes(extra_codes=()):
    codes = set(extra_codes)
    for num_cols, den_cols, _ in SOVI_VARIABLES.values():
        codes.update(num_cols)
        if den_cols:
            codes.update(den_cols)
    return sorted(codes)


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
    df["QHSEBRDN"] = np.where(denom == 0, np.nan, burdened / denom * 100)
    return df


def download_tract():
    codes = all_acs_codes(QHSEBRDN_CODES)
    frames = []
    for fips in STATE_FIPS:
        frames.append(ced.download(
            dataset=DATASET, vintage=VINTAGE,
            download_variables=["NAME"] + codes,
            state=fips, county="*", tract="*",
            api_key=API_KEY,
        ))
        time.sleep(0.2)
    df = pd.concat(frames, ignore_index=True)
    df = add_sovi_variables(df)
    df = add_housing_burden(df)
    df["GEOID"] = df["STATE"] + df["COUNTY"] + df["TRACT"]
    return df[["GEOID", "NAME"] + OUTPUT_COLUMNS + ["QHSEBRDN"]]


def download_county():
    codes = all_acs_codes()
    df = ced.download(
        dataset=DATASET, vintage=VINTAGE,
        download_variables=["NAME"] + codes,
        state="*", county="*",
        api_key=API_KEY,
    )
    df = df[df["STATE"].isin(STATE_FIPS)]
    df = add_sovi_variables(df)
    df["GEOID"] = df["STATE"] + df["COUNTY"]
    return df[["GEOID", "NAME"] + OUTPUT_COLUMNS]


def download_puma():
    codes = all_acs_codes()
    df = ced.download(
        dataset=DATASET, vintage=VINTAGE,
        download_variables=["NAME"] + codes,
        state="*", public_use_microdata_area="*",
        api_key=API_KEY,
    )
    df = df[df["STATE"].isin(STATE_FIPS)]
    df = add_sovi_variables(df)
    df["GEOID"] = df["STATE"] + df["PUBLIC_USE_MICRODATA_AREA"]
    return df[["GEOID", "NAME"] + OUTPUT_COLUMNS]


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    print("Downloading tract-level data (looping over 51 states)...")
    download_tract().to_csv(OUTPUT_DIR / "sovi_tract.csv", index=False)

    print("Downloading county-level data...")
    download_county().to_csv(OUTPUT_DIR / "sovi_county.csv", index=False)

    print("Downloading PUMA-level data...")
    download_puma().to_csv(OUTPUT_DIR / "sovi_puma.csv", index=False)


if __name__ == "__main__":
    main()
