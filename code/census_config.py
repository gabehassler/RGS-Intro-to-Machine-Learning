"""Census API vintage configuration shared by code/01_build_data_dictionaries.py,
code/02_download_data.py, and code/03_build_sovi_variables.py, so changing which
ACS 5-year vintages the pipeline covers only requires editing this file.
"""

DATASET = "acs/acs5"
YEARS = [2024, 2015]
