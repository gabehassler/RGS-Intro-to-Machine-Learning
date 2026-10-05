# Data dictionaries: where the social-vulnerability variable definitions came from

`code/sovi_variables.py` defines 27 social-vulnerability variables inspired
by Table 1 of the assignment (based on Cutter's SoVI), plus
`pct_housing_cost_burdened` (QHSEBRDN, tract-level only) — 28 in total —
plus `population` (total population), which is not one of Table 1's SoVI
variables but is included as useful context. We
use our own human-readable names rather than reproducing SoVI's original
cryptic codes (`QASIAN`, `QBLACK`, ...); those variables aren't Census
variables themselves — each one is a ratio (or, for a few, a direct value)
built from one or more raw ACS estimates. This directory records exactly
which ACS table(s) and variable code(s) back each variable, so the mapping
isn't just sitting undocumented inside the code.

`code/02_download_data.py` downloads the raw ACS codes to `data/raw/`.
`code/03_build_sovi_variables.py` reads those raw files and computes the
derived variables below into `data/processed/`. Splitting the two means
changing a formula doesn't require re-downloading.

## Provenance

Two separate sources went into the crosswalk below:

1. **The original SoVI variable codes** (`QASIAN`, `QBLACK`, ...) came from
   Table 1 of the assignment prompt — not from Census. Census has no concept
   of "SoVI variables"; it only has the raw tables. They're included here
   only for traceability back to Table 1; the names actually used in code
   and output files are the human-readable ones in the "Variable name"
   column.
2. **The ACS table/variable codes** were verified against the **live**
   Census Data API metadata endpoint for each table —
   `https://api.census.gov/data/2024/acs/acs5/groups/<TABLE>.json` — rather
   than recalled from memory or copied from an older vintage. ACS cell
   numbering can and does shift between vintages, so every code used in
   `code/sovi_variables.py` was checked against that endpoint's variable
   labels before being hardcoded.

`code/01_build_data_dictionaries.py` re-runs that same lookup for
every table and merges the results into one CSV,
`data_dictionaries/acs_variable_dictionary.csv`, with a `table` column added
so rows stay traceable to their source table. It's the Census Bureau's own
variable list (`table`, `variable`, `label`, `concept`) for the **2024
5-year ACS** (vintage used throughout `code/02_download_data.py`). Re-run it
(`python code/01_build_data_dictionaries.py` from the repository root) if
the vintage in `code/02_download_data.py` ever changes, to regenerate a
dictionary that matches.

## Variable crosswalk

All ratios are `sum(numerator codes) / sum(denominator codes) * 100`, unless
noted otherwise. "Direct" means the ACS estimate is used as-is.

| Variable name | SoVI code | Description | ACS Table(s) | Numerator | Denominator | Levels |
|---|---|---|---|---|---|---|
| population | — | Total population (not a Table 1 variable) | B01001 | `B01001_001E` (direct) | — | tract, county, PUMA |
| pct_asian | QASIAN | % Asian | B02001 | `B02001_005E` | `B02001_001E` | tract, county, PUMA |
| pct_black | QBLACK | % Black | B02001 | `B02001_003E` | `B02001_001E` | tract, county, PUMA |
| pct_hispanic | QHISP | % Hispanic | B03003 | `B03003_003E` | `B03003_001E` | tract, county, PUMA |
| pct_native_american | QNATAM | % Native American | B02001 | `B02001_004E` | `B02001_001E` | tract, county, PUMA |
| pct_age_dependent | QAGEDEP | % under 5 or 65+ | B01001 | under-5 + 65+ age-bin cells (male and female) | `B01001_001E` | tract, county, PUMA |
| pct_children_married_couple_family | QFAM | % children in 2-parent (married-couple) families | B09002 | `B09002_002E` | `B09002_001E` | tract, county, PUMA |
| median_age | MEDAGE | Median age | B01002 | `B01002_001E` (direct) | — | tract, county, PUMA |
| pct_household_social_security_income | QSSBEN | % households w/ Social Security income | B19055 | `B19055_002E` | `B19055_001E` | tract, county, PUMA |
| pct_below_poverty | QPOVTY | % below poverty | B17001 | `B17001_002E` | `B17001_001E` | tract, county, PUMA |
| pct_high_income_200k | QRICH | % households earning $200k+ | B19001 | `B19001_017E` | `B19001_001E` | tract, county, PUMA |
| per_capita_income | PERCAP | Per capita income | B19301 | `B19301_001E` (direct) | — | tract, county, PUMA |
| pct_limited_english_household | QESL | % limited-English-speaking households | C16002 | sum of "Limited English speaking household" cells across language groups | `C16002_001E` | tract, county, PUMA |
| pct_female | QFEMALE | % female | B01001 | `B01001_026E` | `B01001_001E` | tract, county, PUMA |
| pct_female_headed_household | QFHH | % female-headed households | B11001 | `B11001_006E` | `B11001_001E` | tract, county, PUMA |
| pct_no_health_insurance | QNOHLTH | % without health insurance | B27001 | sum of "No health insurance coverage" cells across all sex/age bins | `B27001_001E` | tract, county, PUMA |
| pct_less_than_12th_grade | QED12LES | % with less than 12th-grade education | B15003 | `B15003_002E`...`B15003_016E` (no schooling through 12th grade, no diploma) | `B15003_001E` | tract, county, PUMA |
| pct_unemployed | QCVLUN | % civilian unemployment | B23025 | `B23025_005E` | `B23025_003E` | tract, county, PUMA |
| people_per_housing_unit | PPUNIT | People per housing unit | B01001, B25001 | `B01001_001E` | `B25001_001E` | tract, county, PUMA |
| pct_renter | QRENTER | % renters | B25003 | `B25003_003E` | `B25003_001E` | tract, county, PUMA |
| median_home_value | MDHSEVAL | Median housing value | B25077 | `B25077_001E` (direct) | — | tract, county, PUMA |
| median_gross_rent | MDGRENT | Median gross rent | B25064 | `B25064_001E` (direct) | — | tract, county, PUMA |
| pct_mobile_homes | QMOHO | % mobile homes | B25024 | `B25024_010E` | `B25024_001E` | tract, county, PUMA |
| pct_extractive_industry | QEXTRCT | % employed in extractive industries | C24030 | agriculture/forestry/fishing/mining cells, male + female | `C24030_001E` | tract, county, PUMA |
| pct_service_occupation | QSERV | % employed in service occupations | C24010 | "Service occupations" subtotal, male + female | `C24010_001E` | tract, county, PUMA |
| pct_female_labor_force | QFEMLBR | % female labor force participation | B23001 | "In labor force" cells for each female age bin (13 bins) | `B23001_088E` (female total) | tract, county, PUMA |
| pct_no_vehicle | QNOAUTO | % housing units with no vehicle | B25044 | owner + renter "No vehicle available" cells | `B25044_001E` | tract, county, PUMA |
| pct_vacant_housing | QUNOCCHU | % unoccupied housing units | B25002 | `B25002_003E` (vacant) | `B25002_001E` | tract, county, PUMA |
| pct_housing_cost_burdened | QHSEBRDN | % households spending >40% of income on housing (**tract-level only**, per Table 1) | B25070 (renters), B25091 (owners) | renter 40%+ cells + owner (with/without mortgage) 40%+ cells | renter- and owner-occupied units with a computable ratio (excludes "not computed" cells) | tract only |

Exact code lists for the multi-cell rows (pct_age_dependent,
pct_limited_english_household, pct_no_health_insurance,
pct_female_labor_force, pct_extractive_industry, pct_service_occupation,
pct_no_vehicle, pct_housing_cost_burdened) are in `SOVI_VARIABLES` /
`HOUSING_COST_BURDEN_CODES` in `code/sovi_variables.py`, and every code
listed there can be looked up by number in the matching CSV in
`data_dictionaries/`.

## Excluded variables

Two of the 29 Table 1 variables are not produced by this pipeline
because the ACS does not publish the data needed, at any geography requested:

- **HOSPTPC** (hospitals per capita, county-level only in Table 1): hospital
  counts are not a Census variable at all. This needs a facility-location
  source such as CMS's Provider of Services file or HIFLD.
- **QNRRES** (nursing home residents per capita): ACS does publish a
  nursing-facility group-quarters count (table `B26103`, cell `_005E`), but
  it is only released at the **state** level — querying it at tract, county,
  or PUMA returns no data (confirmed by direct API query, not assumed from
  table documentation).

## Files in `data_dictionaries/`

A single merged file, `acs_variable_dictionary.csv`, with columns `table`,
`variable`, `label`, `concept` — the Census Bureau's own metadata for every
estimate cell in every ACS table referenced above, for the 2024 5-year ACS.
Generated by `code/01_build_data_dictionaries.py`.
