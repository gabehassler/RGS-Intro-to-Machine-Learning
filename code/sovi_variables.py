"""Shared definition of the social-vulnerability input variables inspired by
Table 1 of the assignment (based on Cutter's SoVI): which ACS codes each one
is built from, and how to combine them. Variable names here are our own
human-readable names, not a reproduction of SoVI's original cryptic codes
(e.g. QASIAN) — see documentation/README.md for the crosswalk back to Table 1.
Also includes `population` (total population), which is not one of the
Table 1 SoVI variables but is useful context for interpreting the others.

Imported by both code/02_download_data.py (to know which raw ACS codes to
fetch) and code/03_build_sovi_variables.py (to compute the derived
variables from those raw codes). Keeping the definitions here means
changing a formula doesn't touch the download script, and changing which
raw codes are needed doesn't touch the processing script.

Two of the 29 Table 1 variables are not available from the ACS and are
skipped here:
  - HOSPTPC (hospitals per capita, county-level only): not a Census variable;
    needs a facility-location source such as CMS or HIFLD.
  - QNRRES (nursing home residents per capita): ACS only publishes the
    nursing-facility group-quarters count (table B26103) at the state level,
    not at tract, county, or PUMA.
"""

# Each variable: (numerator ACS codes to sum, denominator ACS codes to sum
# or None for a value used as-is, multiplier). Codes were verified against
# the live ACS 2024 5-year variable metadata (api.census.gov/data/2024/acs/acs5/
# groups/<table>.json) before being hardcoded here. The trailing comment on
# each line is the corresponding SoVI code from Table 1, for traceability.
SOVI_VARIABLES = {
    "population": (["B01001_001E"], None, 1),  # not a Table 1 SoVI variable; total population
    "pct_asian": (["B02001_005E"], ["B02001_001E"], 100),  # QASIAN
    "pct_black": (["B02001_003E"], ["B02001_001E"], 100),  # QBLACK
    "pct_hispanic": (["B03003_003E"], ["B03003_001E"], 100),  # QHISP
    "pct_native_american": (["B02001_004E"], ["B02001_001E"], 100),  # QNATAM
    "pct_age_dependent": (  # QAGEDEP
        [
            "B01001_003E", "B01001_027E",  # under 5 (male, female)
            "B01001_020E", "B01001_021E", "B01001_022E",  # 65+ male
            "B01001_023E", "B01001_024E", "B01001_025E",
            "B01001_044E", "B01001_045E", "B01001_046E",  # 65+ female
            "B01001_047E", "B01001_048E", "B01001_049E",
        ],
        ["B01001_001E"], 100,
    ),
    "pct_children_married_couple_family": (["B09002_002E"], ["B09002_001E"], 100),  # QFAM
    "median_age": (["B01002_001E"], None, 1),  # MEDAGE
    "pct_household_social_security_income": (["B19055_002E"], ["B19055_001E"], 100),  # QSSBEN
    "pct_below_poverty": (["B17001_002E"], ["B17001_001E"], 100),  # QPOVTY
    "pct_high_income_200k": (["B19001_017E"], ["B19001_001E"], 100),  # QRICH
    "per_capita_income": (["B19301_001E"], None, 1),  # PERCAP
    "pct_limited_english_household": (  # QESL
        ["C16002_004E", "C16002_007E", "C16002_010E", "C16002_013E"],
        ["C16002_001E"], 100,
    ),
    "pct_female": (["B01001_026E"], ["B01001_001E"], 100),  # QFEMALE
    "pct_female_headed_household": (["B11001_006E"], ["B11001_001E"], 100),  # QFHH
    "pct_no_health_insurance": (  # QNOHLTH
        [f"B27001_{n:03d}E" for n in
         (5, 8, 11, 14, 17, 20, 23, 26, 29, 33, 36, 39, 42, 45, 48, 51, 54, 57)],
        ["B27001_001E"], 100,
    ),
    "pct_less_than_12th_grade": (  # QED12LES
        [f"B15003_{n:03d}E" for n in range(2, 17)],
        ["B15003_001E"], 100,
    ),
    "pct_unemployed": (["B23025_005E"], ["B23025_003E"], 100),  # QCVLUN
    "people_per_housing_unit": (["B01001_001E"], ["B25001_001E"], 1),  # PPUNIT
    "pct_renter": (["B25003_003E"], ["B25003_001E"], 100),  # QRENTER
    "median_home_value": (["B25077_001E"], None, 1),  # MDHSEVAL
    "median_gross_rent": (["B25064_001E"], None, 1),  # MDGRENT
    "pct_mobile_homes": (["B25024_010E"], ["B25024_001E"], 100),  # QMOHO
    "pct_extractive_industry": (  # QEXTRCT
        ["C24030_004E", "C24030_005E", "C24030_031E", "C24030_032E"],
        ["C24030_001E"], 100,
    ),
    "pct_service_occupation": (["C24010_019E", "C24010_055E"], ["C24010_001E"], 100),  # QSERV
    "pct_female_labor_force": (  # QFEMLBR
        [f"B23001_{n:03d}E" for n in
         (90, 97, 104, 111, 118, 125, 132, 139, 146, 153, 160, 165, 170)],
        ["B23001_088E"], 100,
    ),
    "pct_no_vehicle": (["B25044_003E", "B25044_010E"], ["B25044_001E"], 100),  # QNOAUTO
    "pct_vacant_housing": (["B25002_003E"], ["B25002_001E"], 100),  # QUNOCCHU
}

# pct_housing_cost_burdened ("percent of households spending >40% of income
# on housing", QHSEBRDN in Table 1, which marks it tract-level ONLY) needs a
# denominator that excludes "not computed" cells, so it doesn't fit the
# simple sum/sum pattern above and is computed separately in
# build_sovi_variables.add_housing_burden().
HOUSING_COST_BURDEN_CODES = [
    "B25070_001E", "B25070_009E", "B25070_010E", "B25070_011E",
    "B25091_001E", "B25091_010E", "B25091_011E", "B25091_012E",
    "B25091_021E", "B25091_022E", "B25091_023E",
]

OUTPUT_COLUMNS = [
    "population",
    "pct_asian", "pct_black", "pct_hispanic", "pct_native_american",
    "pct_age_dependent", "pct_children_married_couple_family", "median_age",
    "pct_household_social_security_income", "pct_below_poverty",
    "pct_high_income_200k", "per_capita_income",
    "pct_limited_english_household", "pct_female",
    "pct_female_headed_household", "pct_no_health_insurance",
    "pct_less_than_12th_grade", "pct_unemployed", "people_per_housing_unit",
    "pct_renter", "median_home_value", "median_gross_rent",
    "pct_mobile_homes", "pct_extractive_industry", "pct_service_occupation",
    "pct_female_labor_force", "pct_no_vehicle", "pct_vacant_housing",
]


def all_acs_codes(extra_codes=()):
    codes = set(extra_codes)
    for num_cols, den_cols, _ in SOVI_VARIABLES.values():
        codes.update(num_cols)
        if den_cols:
            codes.update(den_cols)
    return sorted(codes)
