"""Merge the 2015 tract-level SoVI data with life expectancy and tract
centroid coordinates, and build a small set of geography predictors from
those coordinates: standardized latitude/longitude and their degree-2
polynomial expansion (lat, lon, lat^2, lat*lon, lon^2).

Only the 2015 SoVI vintage is used (not 2024): USALEEP's life expectancy
estimates are based on 2010-2015 mortality and population data, using 2010
Census tract boundaries -- the same vintage as the 2015 ACS data. The 2024
ACS data uses the 2020 Census's redrawn tract boundaries instead, which
don't line up with USALEEP's tract GEOIDs.

Life expectancy is left-joined onto every 2015 SoVI tract, rather than
inner-joined, so tracts with no USALEEP estimate stay in the output with a
missing life_expectancy value instead of silently disappearing.

The standardization and polynomial expansion are fit once here, on every
tract, before any train/test split happens in a notebook -- so the feature
values a model sees for a given tract are always the same regardless of
which cross-validation scheme or fold is being run.

Run after code/03_build_sovi_variables.py and code/04_download_life_expectancy.py
(this script reads both of their outputs).

Output: data/processed/sovi_tract_2015_merged.csv -- every SoVI variable,
life_expectancy, and geo_lat, geo_lon, geo_lat2, geo_lat_lon, geo_lon2.
"""

from pathlib import Path

import pandas as pd
from sklearn.preprocessing import PolynomialFeatures

PROCESSED_DIR = Path("data") / "processed"
RAW_DIR = Path("data") / "raw"

sovi = pd.read_csv(PROCESSED_DIR / "sovi_tract_2015.csv", dtype={"GEOID": str})

life_expectancy = pd.read_csv(RAW_DIR / "usaleep_tract.csv", dtype={"Tract ID": str})
life_expectancy = life_expectancy.rename(columns={"e(0)": "life_expectancy"})
# USALEEP drops the leading zero from "Tract ID" for states with FIPS < 10
# (e.g. Alabama's "01" becomes "1"), so it has to be re-padded to match GEOID.
life_expectancy["GEOID"] = life_expectancy["Tract ID"].str.zfill(11)
life_expectancy = life_expectancy[["GEOID", "life_expectancy"]]

gazetteer = pd.read_csv(RAW_DIR / "gazetteer_tract_2015.txt", sep="\t", dtype={"GEOID": str})
gazetteer.columns = [c.strip() for c in gazetteer.columns]  # trailing whitespace in the header
gazetteer = gazetteer[["GEOID", "INTPTLAT", "INTPTLONG"]]

df = sovi.merge(life_expectancy, on="GEOID", how="left").merge(gazetteer, on="GEOID", how="inner")

# An Aleutian-island AK tract crosses the International Date Line and is
# recorded with positive longitude (~+178), discontinuous with the rest of
# AK (~-150 to -170); unwrap so AK's longitude is continuous.
df.loc[df["INTPTLONG"] > 0, "INTPTLONG"] -= 360

lat_z = (df["INTPTLAT"] - df["INTPTLAT"].mean()) / df["INTPTLAT"].std()
lon_z = (df["INTPTLONG"] - df["INTPTLONG"].mean()) / df["INTPTLONG"].std()

geo_cols = ["geo_lat", "geo_lon", "geo_lat2", "geo_lat_lon", "geo_lon2"]
poly = PolynomialFeatures(degree=2, include_bias=False)
df[geo_cols] = poly.fit_transform(pd.concat([lat_z, lon_z], axis=1))

df = df.drop(columns=["INTPTLAT", "INTPTLONG"])

output_path = PROCESSED_DIR / "sovi_tract_2015_merged.csv"
df.to_csv(output_path, index=False)
n_missing = df["life_expectancy"].isna().sum()
print(f"Saved {output_path} ({len(df):,} tracts, {n_missing:,} missing life_expectancy, {len(geo_cols)} geography columns)")
