"""Download tract-level files that aren't available through the Census API:
USALEEP life expectancy, and the Census Gazetteer tract centroids (latitude/
longitude) needed for any geographic/spatial modeling terms.

USALEEP: see https://www.cdc.gov/nchs/nvss/usaleep/usaleep.html#life-expectancy
for background, including which ACS vintage its estimates are based on. This
script only downloads the raw file; it does not reformat or merge it with any
other data (e.g. the tract identifier column, "Tract ID", is saved exactly as
published, without zero-padding to match the SoVI GEOID format).

Gazetteer: the Census data API (api.census.gov) only returns variable values,
never coordinates, so tract centroids have to come from this separate
product instead. Downloaded as the 2015 vintage to match the tract boundary
vintage used elsewhere in this assignment (see code/03_build_sovi_variables.py
and the HW_02 notebook's discussion of why USALEEP needs the 2015, not 2024,
ACS tracts). Published as a .zip containing a single tab-delimited .txt;
extracted in memory rather than left as a .zip on disk.

Output: data/raw/usaleep_tract.csv, data/raw/gazetteer_tract_2015.txt
"""

import io
import zipfile
from pathlib import Path

import requests
import truststore

# On a network with a TLS-inspecting proxy (e.g. RAND's), Python's default
# bundled CA list doesn't include the proxy's certificate, so a plain
# `requests.get` fails with SSLCertVerificationError even though the proxy's
# certificate is trusted at the OS level. truststore makes requests use the
# OS trust store (Keychain/Cert Store/ca-certificates) instead.
truststore.inject_into_ssl()

RAW_DIR = Path("data") / "raw"
RAW_DIR.mkdir(parents=True, exist_ok=True)

USALEEP_URL = "https://ftp.cdc.gov/pub/Health_Statistics/NCHS/Datasets/NVSS/USALEEP/CSV/US_A.CSV"
usaleep_path = RAW_DIR / "usaleep_tract.csv"

response = requests.get(USALEEP_URL)
response.raise_for_status()
usaleep_path.write_bytes(response.content)
print(f"Saved {usaleep_path} ({len(response.content):,} bytes)")

GAZETTEER_URL = "https://www2.census.gov/geo/docs/maps-data/data/gazetteer/2015_Gazetteer/2015_Gaz_tracts_national.zip"
gazetteer_path = RAW_DIR / "gazetteer_tract_2015.txt"

response = requests.get(GAZETTEER_URL)
response.raise_for_status()
with zipfile.ZipFile(io.BytesIO(response.content)) as archive:
    (name,) = archive.namelist()  # archive holds exactly one file
    gazetteer_path.write_bytes(archive.read(name))
print(f"Saved {gazetteer_path} (extracted from {name})")
