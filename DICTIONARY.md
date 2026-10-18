# QCEW 2025 annual data dictionary

Source: U.S. Bureau of Labor Statistics QCEW, public domain.
annual_raw preserves all source values; annual applies separate disclosure flags except for published establishment measures. See README for limitations and exact grain.

## annual_raw

2025 annual QCEW rows preserving all 38 source fields, numeric placeholders and disclosure flags. Mixed nested geographies, industries and ownership totals; do not sum unfiltered.

Source file: `2025.annual.singlefile.csv`
Rows: 3,089,813

| Column | Type | Nulls | Example | Join |
|--------|------|-------|---------|------|
| area_fips | VARCHAR | 0.0% | 01000 | Join areas using the entire string code. Filter one aggregation/ownership/industry level before aggregating. |
| own_code | VARCHAR | 0.0% | 0 | Join ownerships using the entire string code. Filter one aggregation/ownership/industry level before aggregating. |
| industry_code | VARCHAR | 0.0% | 10 | Join industries using the entire string code. Filter one aggregation/ownership/industry level before aggregating. |
| agglvl_code | VARCHAR | 0.0% | 10 | Join aggregation_levels using the entire string code. Filter one aggregation/ownership/industry level before aggregating. |
| size_code | VARCHAR | 0.0% | 0 | Join size_classes using the entire string code. Filter one aggregation/ownership/industry level before aggregating. |
| year | VARCHAR | 0.0% | 2025 |  |
| qtr | VARCHAR | 0.0% | A |  |
| disclosure_code | VARCHAR | 0.0% |  | Blank is published; N is not disclosed. Raw numeric zeros are retained; use the annual view for disclosure-aware values. |
| annual_avg_estabs | BIGINT | 0.0% | 0 |  |
| annual_avg_emplvl | BIGINT | 0.0% | 0 |  |
| total_annual_wages | BIGINT | 0.0% | 0 |  |
| taxable_annual_wages | BIGINT | 0.0% | 0 |  |
| annual_contributions | BIGINT | 0.0% | 0 |  |
| annual_avg_wkly_wage | BIGINT | 0.0% | 0 |  |
| avg_annual_pay | BIGINT | 0.0% | 0 |  |
| lq_disclosure_code | VARCHAR | 0.0% |  | Blank is published; N is not disclosed. Raw numeric zeros are retained; use the annual view for disclosure-aware values. |
| lq_annual_avg_estabs | DECIMAL(18,2) | 0.0% | 0.00 |  |
| lq_annual_avg_emplvl | DECIMAL(18,2) | 0.0% | 0.00 |  |
| lq_total_annual_wages | DECIMAL(18,2) | 0.0% | 0.00 |  |
| lq_taxable_annual_wages | DECIMAL(18,2) | 0.0% | 0.00 |  |
| lq_annual_contributions | DECIMAL(18,2) | 0.0% | 0.00 |  |
| lq_annual_avg_wkly_wage | DECIMAL(18,2) | 0.0% | 0.00 |  |
| lq_avg_annual_pay | DECIMAL(18,2) | 0.0% | 0.00 |  |
| oty_disclosure_code | VARCHAR | 0.0% |  | Blank is published; N is not disclosed. Raw numeric zeros are retained; use the annual view for disclosure-aware values. |
| oty_annual_avg_estabs_chg | BIGINT | 0.0% | -1 |  |
| oty_annual_avg_estabs_pct_chg | DECIMAL(18,1) | 0.0% | -0.1 |  |
| oty_annual_avg_emplvl_chg | BIGINT | 0.0% | -1 |  |
| oty_annual_avg_emplvl_pct_chg | DECIMAL(18,1) | 0.0% | -0.1 |  |
| oty_total_annual_wages_chg | BIGINT | 0.0% | -1 |  |
| oty_total_annual_wages_pct_chg | DECIMAL(18,1) | 0.0% | -0.1 |  |
| oty_taxable_annual_wages_chg | BIGINT | 0.0% | -1 |  |
| oty_taxable_annual_wages_pct_chg | DECIMAL(18,1) | 0.0% | -0.1 |  |
| oty_annual_contributions_chg | BIGINT | 0.0% | -1 |  |
| oty_annual_contributions_pct_chg | DECIMAL(18,1) | 0.0% | -0.1 |  |
| oty_annual_avg_wkly_wage_chg | BIGINT | 0.0% | -1 |  |
| oty_annual_avg_wkly_wage_pct_chg | DECIMAL(18,1) | 0.0% | -0.1 |  |
| oty_avg_annual_pay_chg | BIGINT | 0.0% | -1 |  |
| oty_avg_annual_pay_pct_chg | DECIMAL(18,1) | 0.0% | -0.1 |  |

## areas

Distinct exact code/title pairs from the pinned 2025 BLS by-area archive. Covers codes used in this release, not all historical classifications.

Source file: `data/area_fips_labels.csv`
Rows: 4,451

| Column | Type | Nulls | Example | Join |
|--------|------|-------|---------|------|
| area_fips | VARCHAR | 0.0% | 01000 | Join areas using the entire string code. Filter one aggregation/ownership/industry level before aggregating. |
| area_title | VARCHAR | 0.0% | Abbeville County, South Carolina |  |

## ownerships

Distinct exact code/title pairs from the pinned 2025 BLS by-area archive. Covers codes used in this release, not all historical classifications.

Source file: `data/own_code_labels.csv`
Rows: 7

| Column | Type | Nulls | Example | Join |
|--------|------|-------|---------|------|
| own_code | VARCHAR | 0.0% | 0 | Join ownerships using the entire string code. Filter one aggregation/ownership/industry level before aggregating. |
| own_title | VARCHAR | 0.0% | Federal Government |  |

## industries

Distinct exact code/title pairs from the pinned 2025 BLS by-area archive. Covers codes used in this release, not all historical classifications.

Source file: `data/industry_code_labels.csv`
Rows: 2,159

| Column | Type | Nulls | Example | Join |
|--------|------|-------|---------|------|
| industry_code | VARCHAR | 0.0% | 10 | Join industries using the entire string code. Filter one aggregation/ownership/industry level before aggregating. |
| industry_title | VARCHAR | 0.0% | 10 Total, all industries |  |

## aggregation_levels

Distinct exact code/title pairs from the pinned 2025 BLS by-area archive. Covers codes used in this release, not all historical classifications.

Source file: `data/agglvl_code_labels.csv`
Rows: 36

| Column | Type | Nulls | Example | Join |
|--------|------|-------|---------|------|
| agglvl_code | VARCHAR | 0.0% | 10 | Join aggregation_levels using the entire string code. Filter one aggregation/ownership/industry level before aggregating. |
| agglvl_title | VARCHAR | 0.0% | CMSA or CSA, Total Covered |  |

## size_classes

Distinct exact code/title pairs from the pinned 2025 BLS by-area archive. Covers codes used in this release, not all historical classifications.

Source file: `data/size_code_labels.csv`
Rows: 1

| Column | Type | Nulls | Example | Join |
|--------|------|-------|---------|------|
| size_code | VARCHAR | 0.0% | 0 | Join size_classes using the entire string code. Filter one aggregation/ownership/industry level before aggregating. |
| size_title | VARCHAR | 0.0% | All establishment sizes |  |

## Exact field definitions

### annual_raw

| Column | Original header | Definition |
|---|---|---|
| area_fips | area_fips | Exact 5-character QCEW area code. Includes state, county-equivalent, metropolitan, national and special aggregates; not all are county FIPS. |
| own_code | own_code | Ownership code; 0 total covered, 1 federal, 2 state, 3 local government, 5 private, 8 total government, 9 total UI covered excluding federal government. Exact source labels are in ownerships; do not sum overlapping sectors. |
| industry_code | industry_code | Original NAICS/supersector/domain/total code. The 2025 release is based on 2022 NAICS; codes include aggregate groups and are not uniformly 6-digit NAICS. |
| agglvl_code | agglvl_code | Aggregation level identifies geographic and industry depth plus ownership grouping; use one level in a comparison. |
| size_code | size_code | Establishment-size code; all annual source records use 0, all sizes. |
| year | year | Source reference year as text; 2025. |
| qtr | qtr | Original quarter field; A means annual average, not a fifth quarter. |
| disclosure_code | disclosure_code | Empty string means published; N means not disclosed. annual_raw preserves zeros. annual nulls employment/wage/contribution levels on N, preserving establishment counts. |
| annual_avg_estabs | annual_avg_estabs | Annual mean of quarterly establishment counts, rounded by BLS; published even when employment/wages are suppressed. |
| annual_avg_emplvl | annual_avg_emplvl | Annual mean of 12 monthly employment levels, rounded; jobs at covered establishments, not unique employed persons. |
| total_annual_wages | total_annual_wages | Sum of quarterly covered wages, nominal dollars. Includes bonuses and other covered pay, not hourly earnings. |
| taxable_annual_wages | taxable_annual_wages | Sum of taxable wages under UI programs, nominal dollars; applicability varies by ownership/state. Preserve published zeros. |
| annual_contributions | annual_contributions | Annual UI contributions, nominal dollars; applicability varies. Preserve published zeros. |
| annual_avg_wkly_wage | annual_avg_wkly_wage | Published average weekly wage in nominal dollars, based on annual wages and average employment; not an unweighted mean of county or industry wages. |
| avg_annual_pay | avg_annual_pay | Published average annual pay in nominal dollars, based on covered wages and average employment; includes full-/part-time and partial-year jobs. |
| lq_disclosure_code | lq_disclosure_code | Separate location-quotient disclosure flag: empty published, N not disclosed. Establishment quotient remains published; annual nulls other quotient measures on N. |
| lq_annual_avg_estabs | lq_annual_avg_estabs | Published location quotient relative to the U.S. for annual_avg_estabs, rounded to hundredths. Use lq_disclosure_code; not a percentage or additive statistic. |
| lq_annual_avg_emplvl | lq_annual_avg_emplvl | Published location quotient relative to the U.S. for annual_avg_emplvl, rounded to hundredths. Use lq_disclosure_code; not a percentage or additive statistic. |
| lq_total_annual_wages | lq_total_annual_wages | Published location quotient relative to the U.S. for total_annual_wages, rounded to hundredths. Use lq_disclosure_code; not a percentage or additive statistic. |
| lq_taxable_annual_wages | lq_taxable_annual_wages | Published location quotient relative to the U.S. for taxable_annual_wages, rounded to hundredths. Use lq_disclosure_code; not a percentage or additive statistic. |
| lq_annual_contributions | lq_annual_contributions | Published location quotient relative to the U.S. for annual_contributions, rounded to hundredths. Use lq_disclosure_code; not a percentage or additive statistic. |
| lq_annual_avg_wkly_wage | lq_annual_avg_wkly_wage | Published location quotient relative to the U.S. for annual_avg_wkly_wage, rounded to hundredths. Use lq_disclosure_code; not a percentage or additive statistic. |
| lq_avg_annual_pay | lq_avg_annual_pay | Published location quotient relative to the U.S. for avg_annual_pay, rounded to hundredths. Use lq_disclosure_code; not a percentage or additive statistic. |
| oty_disclosure_code | oty_disclosure_code | Separate over-the-year disclosure flag: empty published, N not disclosed. Establishment changes remain published; annual nulls other change measures on N. |
| oty_annual_avg_estabs_chg | oty_annual_avg_estabs_chg | Published year-over-year absolute change for annual_avg_estabs. Use oty_disclosure_code; underlying prior-year universe is not supplied in this snapshot. |
| oty_annual_avg_estabs_pct_chg | oty_annual_avg_estabs_pct_chg | Published year-over-year percent change for annual_avg_estabs, rounded to tenths. Use oty_disclosure_code; do not recompute from suppressed/rounded values or interpret as a longitudinal employer panel. |
| oty_annual_avg_emplvl_chg | oty_annual_avg_emplvl_chg | Published year-over-year absolute change for annual_avg_emplvl. Use oty_disclosure_code; underlying prior-year universe is not supplied in this snapshot. |
| oty_annual_avg_emplvl_pct_chg | oty_annual_avg_emplvl_pct_chg | Published year-over-year percent change for annual_avg_emplvl, rounded to tenths. Use oty_disclosure_code; do not recompute from suppressed/rounded values or interpret as a longitudinal employer panel. |
| oty_total_annual_wages_chg | oty_total_annual_wages_chg | Published year-over-year absolute change for total_annual_wages. Use oty_disclosure_code; underlying prior-year universe is not supplied in this snapshot. |
| oty_total_annual_wages_pct_chg | oty_total_annual_wages_pct_chg | Published year-over-year percent change for total_annual_wages, rounded to tenths. Use oty_disclosure_code; do not recompute from suppressed/rounded values or interpret as a longitudinal employer panel. |
| oty_taxable_annual_wages_chg | oty_taxable_annual_wages_chg | Published year-over-year absolute change for taxable_annual_wages. Use oty_disclosure_code; underlying prior-year universe is not supplied in this snapshot. |
| oty_taxable_annual_wages_pct_chg | oty_taxable_annual_wages_pct_chg | Published year-over-year percent change for taxable_annual_wages, rounded to tenths. Use oty_disclosure_code; do not recompute from suppressed/rounded values or interpret as a longitudinal employer panel. |
| oty_annual_contributions_chg | oty_annual_contributions_chg | Published year-over-year absolute change for annual_contributions. Use oty_disclosure_code; underlying prior-year universe is not supplied in this snapshot. |
| oty_annual_contributions_pct_chg | oty_annual_contributions_pct_chg | Published year-over-year percent change for annual_contributions, rounded to tenths. Use oty_disclosure_code; do not recompute from suppressed/rounded values or interpret as a longitudinal employer panel. |
| oty_annual_avg_wkly_wage_chg | oty_annual_avg_wkly_wage_chg | Published year-over-year absolute change for annual_avg_wkly_wage. Use oty_disclosure_code; underlying prior-year universe is not supplied in this snapshot. |
| oty_annual_avg_wkly_wage_pct_chg | oty_annual_avg_wkly_wage_pct_chg | Published year-over-year percent change for annual_avg_wkly_wage, rounded to tenths. Use oty_disclosure_code; do not recompute from suppressed/rounded values or interpret as a longitudinal employer panel. |
| oty_avg_annual_pay_chg | oty_avg_annual_pay_chg | Published year-over-year absolute change for avg_annual_pay. Use oty_disclosure_code; underlying prior-year universe is not supplied in this snapshot. |
| oty_avg_annual_pay_pct_chg | oty_avg_annual_pay_pct_chg | Published year-over-year percent change for avg_annual_pay, rounded to tenths. Use oty_disclosure_code; do not recompute from suppressed/rounded values or interpret as a longitudinal employer panel. |

### areas

| Column | Original header | Definition |
|---|---|---|
| area_fips | area_fips | Exact code present in the 2025 annual release; preserves leading zeros and special aggregate codes. |
| area_title | area_title | Exact BLS title embedded in the same 2025 by-area archive; one unambiguous title per code. |

### ownerships

| Column | Original header | Definition |
|---|---|---|
| own_code | own_code | Exact code present in the 2025 annual release; preserves leading zeros and special aggregate codes. |
| own_title | own_title | Exact BLS title embedded in the same 2025 by-area archive; one unambiguous title per code. |

### industries

| Column | Original header | Definition |
|---|---|---|
| industry_code | industry_code | Exact code present in the 2025 annual release; preserves leading zeros and special aggregate codes. |
| industry_title | industry_title | Exact BLS title embedded in the same 2025 by-area archive; one unambiguous title per code. |

### aggregation_levels

| Column | Original header | Definition |
|---|---|---|
| agglvl_code | agglvl_code | Exact code present in the 2025 annual release; preserves leading zeros and special aggregate codes. |
| agglvl_title | agglvl_title | Exact BLS title embedded in the same 2025 by-area archive; one unambiguous title per code. |

### size_classes

| Column | Original header | Definition |
|---|---|---|
| size_code | size_code | Exact code present in the 2025 annual release; preserves leading zeros and special aggregate codes. |
| size_title | size_title | Exact BLS title embedded in the same 2025 by-area archive; one unambiguous title per code. |

