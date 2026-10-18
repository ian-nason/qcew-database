> **Published October 18, 2026:** see [verified public release and immutable query URL](PUBLICATION.md). Audit/status statements below record the frozen pre-publication snapshot. Registry discovery awaits draft PR review.

# QCEW 2025 annual employment and wages

A version-pinned DuckDB edition of the U.S. Bureau of Labor Statistics [Quarterly Census of Employment and Wages](https://www.bls.gov/cew/downloadable-data-files.htm), annual 2025 snapshot acquired October 18, 2026. It includes all **3,089,813 annual source rows**, five version-matched reference tables, and a disclosure-aware view. The six data tables contain **3,096,467 rows and 48 columns** in total; the view is excluded from those totals.

Use it for descriptive questions about covered employment, establishments and nominal pay in places and industries. The examples focus on county health care and social assistance and state ambulatory health care. This is establishment-based industry data, not occupational wages, unique people, a longitudinal employer panel or a causal analysis. It has no direct O*NET occupation or ATUS respondent crosswalk.

## Tables and grain

| Table | Rows | Meaning |
|---|---:|---|
| annual_raw | 3,089,813 | Exact 38 source fields, including all placeholder zeroes and three disclosure flags |
| areas | 4,451 | Unique area code/title pairs present in the 2025 source |
| ownerships | 7 | Ownership sectors and overlapping total groups |
| industries | 2,159 | Industry, supersector, domain and aggregate codes present in the source |
| aggregation_levels | 36 | Geographic/industry depth and special summary levels |
| size_classes | 1 | Code 0, all establishment sizes |

The complete raw key is `(area_fips, own_code, industry_code, agglvl_code, size_code, year, qtr)`. All key fields remain text, including leading-zero FIPS codes; `year='2025'`, `qtr='A'`, `size_code='0'`. `A` denotes annual, not a fifth quarter. The `annual` view retains this key, adds five labels through unique dictionaries, and applies disclosure rules.

The standalone BLS dictionary downloads returned HTTP 403 in this environment. Labels instead come from **every row of the official 2025 annual-by-area ZIP**, not a third-party list or a different vintage. Every code had one exact title. The derived reference CSVs are sorted distinct pairs, checksum-pinned and included in the source repository. They cover codes used in this snapshot; they are not a comprehensive historical code list. `profile_sources.py` can regenerate and compare them from the pinned archive without extracting it in full.

## Disclosure and missingness

The raw source has no missing numeric fields. An empty disclosure string means published; `N` means not disclosed. Empty flags remain empty strings rather than SQL NULL. All source numeric values remain exact in `annual_raw`.

The `annual` view treats the three flags independently:

| Flag | Measures set to NULL on N | Source establishment measures retained |
|---|---|---|
| disclosure_code | Employment, total/taxable wages, contributions, weekly wage and annual pay | annual_avg_estabs |
| lq_disclosure_code | Corresponding six location quotients | lq_annual_avg_estabs |
| oty_disclosure_code | Corresponding absolute and percentage changes | oty_annual_avg_estabs_chg and oty_annual_avg_estabs_pct_chg |

There are 1,860,359 `N` level rows, 1,872,172 `N` quotient rows and 1,937,791 `N` change rows. The four establishment measures are retained exactly as published; diagnostics report their nonzero values even when the corresponding flag is N. Never infer employment or pay from suppressed zeroes. Unsuppressed zeroes remain zero; some taxable-wage/contribution fields are not applicable to particular ownerships or programs, so a published zero is not automatically economic absence. Location quotients and percentage changes can also have source-defined zero-denominator limitations; this derivative preserves their published values without inventing replacements.

Suppressed detailed values are included in published higher-level totals. Summing disclosed cells produces an incomplete total. The view intentionally does not estimate suppressed values or reconstruct them by subtraction. Reports should state how many eligible cells have published values. [BLS disclosure discussion](https://www.bls.gov/cew/publications/employment-and-wages-annual-averages/2025/home.htm#disclosure-restrictions).

## Safe comparisons

* Filter one geographic level, industry depth and ownership group. National, state, county, metro and combined-area rows overlap. Industry totals, sectors and subsectors nest. Ownership 0 is total covered; 8 is total government; 9 is total UI covered excluding federal government. These overlap sectors 1, 2, 3 and 5.
* Use `agglvl_code`, not the length of an industry code, to select a consistent grain. For example, 74 is county/NAICS sector/by ownership; 75 is county/3-digit industry/by ownership; 55 is state/3-digit industry/by ownership.
* County-equivalent geography is not fixed through time. Connecticut uses planning-region codes starting with 2024 QCEW data. County examples exclude codes ending in `999` for unallocated geography; they include available states and territories. Review the geography dictionary before restricting a study universe.
* The 2025 data use **2022 NAICS**. Do not compare historical industry series without checking classification and geographic changes. `62` is health care **and social assistance**; `621` is ambulatory health care services and `622` is hospitals.
* Employment counts covered jobs. A person with multiple covered employers can be counted more than once. UI/UCFE coverage excludes the self-employed and other groups; it is not the entire labor force. Annual employment is the mean of 12 monthly levels, while establishment counts average four quarters. Published rounding can prevent exact equality between summed components and totals.
* Wage totals are nominal dollars. Annual/weekly average pay is a ratio, not an additive measure or an hourly wage. Full-time, part-time, part-year work and bonuses affect it. Do not take an unweighted average of county pay to estimate national pay. Use published aggregates, and do not calculate a weighted aggregate where suppressed components are missing.
* The snapshot includes BLS's published year-over-year changes, not a separate 2024 table. Administrative reclassification, revisions, imputations and coverage changes affect comparisons; reported changes are not causal effects.

## Examples

Open a locally built candidate read-only:

```python
import duckdb
con = duckdb.connect('releases/2025-release-final/qcew.duckdb', read_only=True)
con.sql("SELECT * FROM _metadata").show()
```

```sql
SELECT area_fips, area_title, annual_avg_estabs, annual_avg_emplvl,
       avg_annual_pay, lq_annual_avg_emplvl, lq_disclosure_code
FROM annual
WHERE agglvl_code='74' AND own_code='5' AND industry_code='62'
  AND right(area_fips,3)<>'999' AND annual_avg_emplvl>0
ORDER BY annual_avg_emplvl DESC, area_fips LIMIT 20;
```

[examples.sql](examples.sql) also selects one national total, reports disclosure coverage, compares state ambulatory-care employment/pay, and joins ambulatory and hospital rows after fixing their grain. Saved results bind to the artifact checksum. These queries establish useful behavior, not demand or adoption.

## Sources, reproducibility and validation

`source-lock.json` pins the original singlefile ZIP (62,799,396 bytes; SHA-256 `94ebbc589b1b500671c1fd507e2589a9eeb24dcd30eb07f1ce37b0018643f865`), its CSV member, the annual-by-area label ZIP (114,997,862 bytes), and each derived reference CSV. Both archives were last modified by BLS on August 21, 2026. The annual URL can be revised: this is the exact acquired snapshot, not a guarantee that a later download has identical content. A changed checksum fails closed. Source ZIP sizes are not memory or artifact-size estimates.

The builder uses Python 3.12, DuckDB 1.5.5 and the already provisioned FJC judges environment's datapond-build helper. `pyproject.toml` pins DuckDB and the helper source revision. `helper-lock.json` and `runtime.json` verify the actual imported helper code, interpreter and package inventory. The installed helper distribution reports 0.1.1 but its used metadata functions match the pinned source bytes. No new software installation or clean-environment dependency test is claimed.

```sh
python -m unittest -v test_qcew test_guard
python run_guarded.py evidence/new-build python qcew.py --download --output releases/new-candidate
python audit_release.py releases/new-candidate/qcew.duckdb
```

The five small derived dictionary CSVs are included in the source checkout. To regenerate their provenance, download the exact locked by-area ZIP into `data/` and run `profile_sources.py` under the guard; existing dictionary bytes must match. The builder hashes its cached extracted singlefile before every use. Output directories must stay within the guarded repository. Existing output directories and retained partial downloads/extractions are never overwritten. Extraction uses a `.partial` file, hashes it, and only then renames it into the cache; inspect and quarantine any interrupted partial before retrying. The first failed attempt logs and subsequent evidence remain available locally. A redundant extracted CSV from that failed attempt was removed only after matching its SHA-256 to the retained cache and pinned ZIP member; evidence/duplicate-source-cleanup.json records it.

DuckDB uses one thread, 256 MiB memory and at most 512 MiB temporary spill. The Linux supervisor stops its process group above 768 MiB sampled RSS, 2 GiB of files in this isolated repository, less than 1.5 GiB available RAM, less than 10 GiB free disk, or a 15-minute deadline. It handles disappearing temporary files and worker-exit races. Measurements are saved per run; retained attempts and `.git` count toward the disk cap. Only one ingestion worker runs at a time.

Every raw typed cell is compared against an independent streaming Python CSV/Decimal read of the original ZIP before checkpoint and again after read-only reopen. Types are explicit: text codes/flags, BIGINT counts and dollar values, DECIMAL(18,2) quotients, DECIMAL(18,1) percentage changes. No trimming, numeric coercion, rounding or hidden imputation is permitted. Code/title pairs, keys, relationships, counts, flag distributions, numeric ranges, dictionary statistics and metadata are checked. Raw order is only an audit mechanism; SQL users must specify `ORDER BY`.

Additional checks cover every analytic NULL against its own flag, preservation of all four establishment measures, view row counts, a locked original source-row regression value (not an external benchmark), and the disjoint ownership partition with rounding tolerance. The national source row reports 155,732,363 jobs and $12,259,226,899,972 in wages. Failure fixtures cover source corruption, duplicate members/keys, join inflation, missing codes, leading zeros, blank flags, invalid codes, overprecision, oversized wage values and suppression mistakes.

All 35 failure-fixture tests pass. The release build took 267.26 seconds, with 411.7 MiB sampled peak process-group RSS; its DuckDB artifact is 195,571,712 bytes. Rebuilds reproduce typed table fingerprints and dictionary bytes; metadata timestamps and physical serialization mean the database files are not byte-identical.

The consumer harness uses the existing Python client/DuckDB 1.5.4 and R clients 0.1.0/0.1.1 with DuckDB 1.5.5 through localhost HTTP ranges. It bounds each client, uses fresh R caches, hashes the installed R package, and loads preinstalled httpfs instead of installing anything. R returns BIGINT/DECIMAL results as doubles in the tested clients; the checked integer values are below 2^53, while decimal fractions are approximate in the client. The DuckDB DECIMAL storage remains exact. Actual public-host hash, range-request and Python/R/DuckDB verification remains necessary after an authorized upload. Local consumer success is not public availability.

## Dictionary, update and license

[DICTIONARY.md](DICTIONARY.md) describes all 48 data columns, exact source headers, types, examples, NULL proportions and join hints. `_metadata` gives table provenance and `_columns` stores column definitions. BLS's [annual layout](https://www.bls.gov/cew/about-data/downloadable-file-layouts/annual/naics-based-annual-layout.htm) and [CSV-slice layout](https://www.bls.gov/cew/additional-resources/open-data/csv-data-slices.htm) explain the measures. The source singlefile uses `annual_avg_estabs`, while one BLS layout calls it `annual_avg_estabs_count`; this derivative retains the actual CSV header.

To update, choose a reference year and acquisition snapshot; review release status, NAICS/geography changes and disclosure rules; independently pin both official archives and regenerate labels/schema; rebuild into a new directory; run all-cell, aggregate, fixture, example and installed-client checks; obtain Codex review and an independent Claude review and resolve findings. Then publish only to authorized destinations, verify the immutable remote artifact and consumers, and open the separate registry PR. Annual files may be revised; this repository does not promise automated refreshes.

BLS data are **public domain**, with source attribution requested. Cite the U.S. Bureau of Labor Statistics, Quarterly Census of Employment and Wages, 2025 annual, acquisition date and artifact hash. See [BLS copyright information](https://www.bls.gov/opub/copyright-information.htm) and [LICENSE.md](LICENSE.md). This derivative converts representation, adds dictionaries/metadata and the analytic view, and preserves original source values in `annual_raw`. No BLS endorsement or ownership of its emblem is implied.

The source labels for DC codes 11000 and 11001 both say “District of Columbia, not unknown”; they are retained verbatim. Los Angeles County’s 2025 private health care/social assistance row reports 287,445 establishments and 859,824 jobs. This snapshot does not independently establish the administrative explanation for that unusually large establishment count. Use the exact source definitions when comparing establishments across states.
