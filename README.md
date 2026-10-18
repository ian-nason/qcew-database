# QCEW 2025 Annual Employment and Wages

A version-pinned DuckDB edition of the U.S. Bureau of Labor Statistics [Quarterly Census of Employment and Wages](https://www.bls.gov/cew/downloadable-data-files.htm), 2025 annual averages: **3,096,467 rows across 6 tables (48 columns)**, all 3,089,813 annual source rows plus five version-matched reference tables and a disclosure-aware view.

Use it for descriptive questions about covered employment, establishments and nominal pay by place, industry and ownership. It is establishment-based industry data, not occupational wages, unique people, an employer panel or a causal analysis.

Download/query the [Hugging Face dataset](https://huggingface.co/datasets/Nason/qcew-database). Published to Hugging Face on 2026-10-18. The datapond registry entry is a draft pull request, so `datapond.connect('qcew')` does not resolve this database until it is merged; the direct URL below works now.

[Quick start](#quick-start) · [Tables](#tables) · [Views](#pre-built-views) · [Examples](#example-queries) · [Caveats](#researcher-caveats) · [Source](#data-source-and-version) · [License](#license-and-attribution) · [Build](#build-from-source) · [Changelog](#changelog)

## Quick Start

### DuckDB CLI

```sql
SET memory_limit = '128MiB';
SET threads = 1;
SET max_temp_directory_size = '0B';
INSTALL httpfs;
LOAD httpfs;
ATTACH 'https://huggingface.co/datasets/Nason/qcew-database/resolve/334c467dba413928233fb1d8cd1c0ff8de5c0105/qcew.duckdb' AS qcew (READ_ONLY);

-- The one published national all-industry, all-ownership total. Never sum the whole table.
SELECT area_title, annual_avg_estabs, annual_avg_emplvl, total_annual_wages, avg_annual_pay
FROM qcew.annual
WHERE area_fips = 'US000' AND own_code = '0' AND industry_code = '10'
  AND agglvl_code = '10' AND size_code = '0' AND year = '2025' AND qtr = 'A';
```

The database is 196 MB. Filtered queries fetch only the byte ranges they touch; an unfiltered scan of `annual_raw` reads most of the file, so download it locally if you plan to scan repeatedly. The examples use this immutable artifact URL:

```
https://huggingface.co/datasets/Nason/qcew-database/resolve/334c467dba413928233fb1d8cd1c0ff8de5c0105/qcew.duckdb
```

### Python (duckdb)

```python
import duckdb
con = duckdb.connect(config={"memory_limit": "128MiB", "threads": "1", "max_temp_directory_size": "0B"})
con.sql("INSTALL httpfs; LOAD httpfs;")
con.sql("ATTACH 'https://huggingface.co/datasets/Nason/qcew-database/resolve/334c467dba413928233fb1d8cd1c0ff8de5c0105/qcew.duckdb' AS qcew (READ_ONLY)")
con.sql("SELECT * FROM qcew._metadata").show()
con.sql("""
    SELECT area_fips, area_title, annual_avg_emplvl, avg_annual_pay, disclosure_code
    FROM qcew.annual
    WHERE agglvl_code = '74' AND own_code = '5' AND industry_code = '62'
      AND right(area_fips, 3) <> '999' AND annual_avg_emplvl > 0
    ORDER BY annual_avg_emplvl DESC, area_fips LIMIT 20
""").show()
con.close()
```

### R (DBI + duckdb)

```r
library(DBI)
con <- dbConnect(duckdb::duckdb(config = list(memory_limit = "128MiB", threads = "1", max_temp_directory_size = "0B")))
dbExecute(con, "INSTALL httpfs")
dbExecute(con, "LOAD httpfs")
dbExecute(con, "ATTACH 'https://huggingface.co/datasets/Nason/qcew-database/resolve/334c467dba413928233fb1d8cd1c0ff8de5c0105/qcew.duckdb' AS qcew (READ_ONLY)")
dbGetQuery(con, "SELECT area_fips, area_title, annual_avg_emplvl, avg_annual_pay
                 FROM qcew.annual
                 WHERE agglvl_code = '55' AND own_code = '5' AND industry_code = '621'
                 ORDER BY annual_avg_emplvl DESC NULLS LAST, area_fips")
dbDisconnect(con, shutdown = TRUE)
```

In the tested R DuckDB 1.5.5 configuration, BIGINT and DECIMAL results are exposed as doubles. Employment and wage integers here are below 2^53 and exact; location quotients and percentage changes may be approximate in R although the stored DECIMAL values are exact.

### datapond package (after catalog integration)

The public default catalog does not yet include `qcew`. After its registry entry is merged, these examples use the package's normal discovery and connection API:

```python
import datapond
print(datapond.list())
datapond.describe('qcew', table='annual_raw')
con = datapond.connect('qcew')
con.sql("SELECT annual_avg_emplvl, total_annual_wages FROM annual WHERE area_fips = 'US000' AND own_code = '0' AND industry_code = '10' AND agglvl_code = '10'").show()
con.close()
```

```r
library(datapond)
dp_list()
con <- dp_connect('qcew')
dp_describe(con, table = 'annual_raw')
DBI::dbGetQuery(con, "SELECT annual_avg_emplvl, total_annual_wages FROM annual WHERE area_fips = 'US000' AND own_code = '0' AND industry_code = '10' AND agglvl_code = '10'")
dp_disconnect(con)
```

For repeated scans, after catalog integration, download once and connect locally:

```python
import datapond
datapond.download('qcew')
con = datapond.connect('qcew', local=True)
con.sql("SELECT annual_avg_emplvl, total_annual_wages FROM annual WHERE area_fips = 'US000' AND own_code = '0' AND industry_code = '10' AND agglvl_code = '10'").show()
con.close()
```

```r
library(datapond)
dp_download('qcew')
con <- dp_connect('qcew', local = TRUE)
DBI::dbGetQuery(con, "SELECT annual_avg_emplvl, total_annual_wages FROM annual WHERE area_fips = 'US000' AND own_code = '0' AND industry_code = '10' AND agglvl_code = '10'")
dp_disconnect(con)
```

Verify the recorded artifact SHA-256 after downloading. In tested Python 0.1.1, the optional Hugging Face download path follows the default branch rather than the pinned URL; see [consumer verification](https://github.com/ian-nason/qcew-database/blob/main/docs/CONSUMERS.md) for the tested configuration.

Package checks use an isolated candidate registry; default-catalog discovery remains pending. See [consumer verification](https://github.com/ian-nason/qcew-database/blob/main/docs/CONSUMERS.md) for exact client versions, paths, resource limits and download behavior. The direct URL examples above work independently of the catalog. The SQL examples below use the `qcew` catalog alias from the direct-URL quick start.


## Tables

| Table | Description | Rows | Columns |
|---|---|---:|---:|
| `annual_raw` | 2025 annual QCEW rows preserving all 38 source fields, numeric placeholders and disclosure flags. Mixed nested geographies, industries and ownership totals; do not sum unfiltered | 3,089,813 | 38 |
| `areas` | Distinct exact area code/title pairs from the pinned 2025 BLS by-area archive | 4,451 | 2 |
| `industries` | Distinct exact industry code/title pairs from the pinned archive | 2,159 | 2 |
| `aggregation_levels` | Distinct exact aggregation-level code/title pairs | 36 | 2 |
| `ownerships` | Distinct exact ownership code/title pairs | 7 | 2 |
| `size_classes` | Code 0, all establishment sizes | 1 | 2 |

The raw key is `(area_fips, own_code, industry_code, agglvl_code, size_code, year, qtr)`. All key fields are text, including leading-zero FIPS codes; `year='2025'`, `qtr='A'` (annual, not a fifth quarter), `size_code='0'`. Reference tables cover codes used in this snapshot, not a historical code list; every code had one exact title. `_metadata` has one row per data table; `_columns` carries column definitions.

## Pre-built Views

| View | What it does |
|---|---|
| `annual` | `annual_raw` with the full key, five labels joined through the unique dictionaries, and the three disclosure flags applied independently |

In `annual`, `disclosure_code='N'` sets employment, wages, contributions, weekly wage and annual pay to NULL; `lq_disclosure_code='N'` nulls the six location quotients; `oty_disclosure_code='N'` nulls the over-the-year changes. The four establishment measures (`annual_avg_estabs`, `lq_annual_avg_estabs`, `oty_annual_avg_estabs_chg`, `oty_annual_avg_estabs_pct_chg`) are always retained as published. `annual_raw` keeps every source value, including placeholder zeroes on suppressed rows. The view is not counted in the row and table totals above.

## Example Queries

County disclosure coverage for private health care and social assistance, including valid establishment counts on suppressed rows:

```sql
SELECT disclosure_code, count(*) AS source_cells,
       count(annual_avg_emplvl) AS published_employment_cells,
       sum(annual_avg_estabs) AS published_establishments_rounded
FROM qcew.annual
WHERE agglvl_code = '74' AND own_code = '5' AND industry_code = '62'
  AND right(area_fips, 3) <> '999'
GROUP BY disclosure_code ORDER BY disclosure_code;
```

State private ambulatory health care (NAICS 621) with published year-over-year change and its own flag:

```sql
SELECT area_fips, area_title, annual_avg_emplvl, avg_annual_pay,
       oty_annual_avg_emplvl_pct_chg, oty_disclosure_code
FROM qcew.annual
WHERE agglvl_code = '55' AND own_code = '5' AND industry_code = '621'
ORDER BY annual_avg_emplvl DESC NULLS LAST, area_fips;
```

Compare two disjoint subsectors after fixing the grain to one row per county and industry:

```sql
WITH selected AS (
  SELECT area_fips, area_title, industry_code, annual_avg_emplvl, avg_annual_pay
  FROM qcew.annual
  WHERE agglvl_code = '75' AND own_code = '5'
    AND industry_code IN ('621', '622') AND right(area_fips, 3) <> '999'
)
SELECT a.area_fips, a.area_title,
       a.annual_avg_emplvl AS ambulatory_jobs, h.annual_avg_emplvl AS hospital_jobs,
       a.avg_annual_pay AS ambulatory_pay, h.avg_annual_pay AS hospital_pay
FROM selected a JOIN selected h ON a.area_fips = h.area_fips
WHERE a.industry_code = '621' AND h.industry_code = '622'
ORDER BY a.area_fips LIMIT 20;
```

The full set is in [examples.sql](https://github.com/ian-nason/qcew-database/blob/main/examples.sql); saved results are bound to the artifact hash.

## Researcher Caveats

1. **Suppression flags are independent and partial.** Three flags (`disclosure_code`, `lq_disclosure_code`, `oty_disclosure_code`) each govern their own measures. There are 1,860,359 suppressed level rows, 1,872,172 suppressed quotient rows and 1,937,791 suppressed change rows. Suppressed rows still carry valid establishment counts. Never read a suppressed zero as zero employment or pay.
2. **Suppressed cells are inside published totals.** Summing disclosed detail gives an incomplete total; the view does not estimate or back out suppressed values. Report how many eligible cells have published values ([BLS disclosure note](https://www.bls.gov/cew/publications/employment-and-wages-annual-averages/2025/home.htm#disclosure-restrictions)).
3. **Rows nest; pick one grain.** National, state, county, metro and combined-area rows overlap, industry totals nest, and ownership 0 (total), 8 (total government) and 9 (UI covered excluding federal) overlap sectors 1, 2, 3 and 5. Filter on `agglvl_code` (for example 74 county/sector/ownership, 75 county/3-digit, 55 state/3-digit), not on code length.
4. **Geography moves.** Connecticut uses planning-region codes from 2024 data; codes ending `999` are unallocated. Check `areas` before fixing a study universe.
5. **Industry is 2022 NAICS.** `62` is health care and social assistance; `621` ambulatory care; `622` hospitals. Do not splice historical series without checking classification changes.
6. **Employment counts covered jobs, not people.** A worker with two covered employers counts twice; the self-employed and other uncovered groups are absent. Annual employment averages 12 monthly levels; establishments average four quarters; rounding can break exact additivity.
7. **Pay is a nominal ratio.** Average annual and weekly pay are not hourly wages and not additive; do not average county pay to estimate national pay or build weighted aggregates where components are suppressed.
8. **Changes are published, not computed.** Over-the-year fields come from BLS and reflect revisions, reclassification and coverage changes; they are not causal effects. There is no separate 2024 table.
9. **Published zeros can be structural.** Some taxable-wage and contribution fields do not apply to particular ownerships, so a zero is not necessarily economic absence.

10. **Source anomalies remain visible.** DC codes 11000 and 11001 both carry “District of Columbia, not unknown”. Los Angeles County’s private health care/social assistance row has 287,445 establishments and 859,824 jobs; this snapshot does not establish why the establishment count is unusually large.

## Data Source and Version

Bureau of Labor Statistics, Quarterly Census of Employment and Wages, 2025 annual singlefile, acquired 2026-10-18. Pinned source ZIP: 62,799,396 bytes, SHA-256 `94ebbc589b1b500671c1fd507e2589a9eeb24dcd30eb07f1ce37b0018643f865`; labels derived from the official 2025 annual-by-area ZIP (114,997,862 bytes). Both archives were last modified by BLS on August 21, 2026. The national row reports 155,732,363 jobs and $12,259,226,899,972 in wages. BLS may revise annual files; this is the exact acquired snapshot, with no automatic refresh promised.

Artifact: `qcew.duckdb`, 195,571,712 bytes, SHA-256 `89bf1cef54f42f821965df6e9079b24fc7c4c0c86046fadc98e6cedf9ebd8a1d`, dataset commit `334c467dba413928233fb1d8cd1c0ff8de5c0105`.

## License and Attribution

BLS data are public domain; BLS requests source attribution ([BLS copyright information](https://www.bls.gov/opub/copyright-information.htm)). Cite: U.S. Bureau of Labor Statistics, Quarterly Census of Employment and Wages, 2025 annual, acquisition date and artifact hash. This derivative changes representation, adds dictionaries, metadata and the `annual` view, and preserves all source values in `annual_raw`. No BLS endorsement is implied.

## Build from Source

The audited build uses Python 3.12 and DuckDB 1.5.5; dependency and helper revisions are pinned in `pyproject.toml` and `helper-lock.json`.

```sh
python -m unittest -v test_qcew test_guard
python run_guarded.py evidence/new-build python qcew.py --download --output releases/new-candidate
python run_guarded.py evidence/new-audit python audit_release.py releases/new-candidate/qcew.duckdb
```

Use a fresh isolated checkout and output directory. The supervisor bounds memory, disk and runtime; source hashes fail closed. Every typed source cell is compared before checkpoint and after read-only reopen, and 35 regression fixtures cover failure cases. See [build, validation and update details](docs/REPRODUCE.md) for prerequisites, exact limits, source provenance, retained partials, measured resource use and the update procedure. See [the detailed researcher guide](docs/RESEARCHER-GUIDE.md) for the complete original interpretation and code notes.

## GitHub, Dictionary and Website

[Detailed researcher guide](https://github.com/ian-nason/qcew-database/blob/main/docs/RESEARCHER-GUIDE.md) · [Build and update instructions](https://github.com/ian-nason/qcew-database/blob/main/docs/REPRODUCE.md) · [Verified publication](https://github.com/ian-nason/qcew-database/blob/main/PUBLICATION.md)

- Source, build scripts, tests and evidence: [github.com/ian-nason/qcew-database](https://github.com/ian-nason/qcew-database)
- Column dictionary (all 48 columns, source headers, types, NULL shares, join hints): [DICTIONARY.md](https://github.com/ian-nason/qcew-database/blob/main/DICTIONARY.md); BLS [annual layout](https://www.bls.gov/cew/about-data/downloadable-file-layouts/annual/naics-based-annual-layout.htm)
- Catalog: [datapond registry](https://github.com/datapond-db/registry); the entry for `qcew` is a draft pull request and the database will appear on the [datapond website](https://datapond-db.github.io/website/) once it is merged.

## Changelog

### 2026-10-18 — Documentation refresh

- Added Python/R quick starts, table descriptions and column counts, view guidance, navigation, and clearer researcher caveats.
- Database bytes, schema, source locks and validated query results are unchanged. Catalog integration remains pending.

### 2026-10-18 — Initial release

- QCEW 2025 annual: 3,096,467 rows across 6 tables (48 columns) and the `annual` view. Artifact 195,571,712 bytes, SHA-256 `89bf1cef…edbf8a1d`, commit `334c467d`.
- Every typed cell verified against an independent read of the pinned source ZIP; disclosure NULLs checked against their own flags; public immutable URL, HTTP range requests and the installed Python and R clients tested after upload.
- Registry entry opened as a draft pull request; catalog integration pending.
