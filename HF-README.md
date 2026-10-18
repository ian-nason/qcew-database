---
license: other
license_name: public-domain-us-bls
license_link: https://www.bls.gov/opub/copyright-information.htm
pretty_name: QCEW 2025 Annual Employment and Wages
tags: [qcew, employment, wages, industry, counties, duckdb]
size_categories: [1M<n<10M]
---

# QCEW 2025 annual employment and wages

The U.S. Bureau of Labor Statistics [QCEW 2025 annual data](https://www.bls.gov/cew/downloadable-data-files.htm), pinned to the snapshot acquired October 18, 2026. The DuckDB file is **195,571,712 bytes** and includes **3,089,813 annual source rows**, five code/title tables with 6,654 rows, and one analytic view. Six data tables total **3,096,467 rows and 48 documented columns**.

`annual_raw` preserves all 38 source fields. `areas` (4,451), `ownerships` (7), `industries` (2,159), `aggregation_levels` (36) and `size_classes` (1) contain unique labels extracted from the official same-year by-area archive. They cover codes used in this snapshot, not every historical classification.

## Query

With DuckDB and an available httpfs extension:

```sql
LOAD httpfs;
ATTACH 'https://huggingface.co/datasets/Nason/qcew-database/resolve/main/qcew.duckdb'
  AS qcew (READ_ONLY);
SELECT area_fips,area_title,annual_avg_estabs,annual_avg_emplvl,avg_annual_pay
FROM qcew.annual
WHERE agglvl_code='74' AND own_code='5' AND industry_code='62'
  AND right(area_fips,3)<>'999' AND annual_avg_emplvl>0
ORDER BY annual_avg_emplvl DESC,area_fips LIMIT 20;
```

This compares private county health care **and social assistance**, not all occupations or all health care workers. Pin the Hugging Face commit instead of `main` for reproducibility. Registry-based client discovery requires the separate registry entry or a local override.

## Interpretation

The raw key is `(area_fips,own_code,industry_code,agglvl_code,size_code,year,qtr)`. Codes retain leading zeros; `qtr='A'` means annual and size 0 means all establishment sizes. Use exactly one geographic, industry and ownership grain. Totals, component industries, government groups, counties and metro areas overlap; unfiltered sums double-count. The 2025 snapshot uses 2022 NAICS. Connecticut county-equivalent geography changed to planning regions in 2024.

The `annual` view keeps source flags and replaces withheld employment, wage/contribution levels, quotients and changes with SQL NULL under their respective `disclosure_code`, `lq_disclosure_code` and `oty_disclosure_code`. Empty flag means published; N means not disclosed. The four establishment measures as published remain available even on flagged rows. Source numeric zeros and flags remain unchanged in `annual_raw`. Do not infer suppressed values or treat an incomplete sum of disclosed cells as a population total. Published zeros can also reflect inapplicable tax/contribution measures.

Annual average employment counts covered jobs, not unique people or the full labor force. Wages are nominal; average annual pay is a ratio affected by part-time/part-year work and bonuses, not hourly pay. Never average pay ratios across places without appropriate complete denominators. Published changes do not create a longitudinal employer panel. No causal claims or direct O*NET/ATUS crosswalk is supplied.

## Provenance and validation

Artifact SHA-256: `89bf1cef54f42f821965df6e9079b24fc7c4c0c86046fadc98e6cedf9ebd8a1d`.
Singlefile ZIP SHA-256: `94ebbc589b1b500671c1fd507e2589a9eeb24dcd30eb07f1ce37b0018643f865`.

[sources-2025.json](sources-2025.json) is an explicitly historical pre-publication evidence snapshot containing source identities, build proof and runtime identity. Every raw typed cell was checked against original CSV/Decimal reads before checkpoint and after readonly reopen. Reference CSV regeneration matched every byte; both official archives' non-title records agree. A repeated build reproduced typed fingerprints and dictionary bytes. All 35 fixtures pass, and independent release checks cover disclosure rules, keys, relationships, schema, metadata, dictionary fields, national totals and useful examples.

Installed Python and R consumers passed localhost HTTP range checks. Those checks do not establish actual public-host verification. See the [source repository](https://github.com/ian-nason/qcew-database) for code, audit records, exact review scope, update instructions and additional queries, and [DICTIONARY.md](DICTIONARY.md) for every field. Review of supplied code/evidence is distinct from an independent re-execution of computations.

## Attribution and changes

Source: **U.S. Bureau of Labor Statistics, Quarterly Census of Employment and Wages, 2025 annual**, acquired October 18, 2026. BLS data are [public domain](https://www.bls.gov/opub/copyright-information.htm); source credit is requested. Cite the year, acquisition date and derivative artifact hash. No BLS trademark rights or endorsement are implied.

This derivative types the CSVs, deduplicates exact code/title pairs, adds metadata/dictionary/examples, and exposes the disclosure-aware view. Original numeric values, flags and codes remain in `annual_raw`. No suppressed values are estimated. Annual source URLs may be revised; updates require new pins and review.

The source labels for DC codes 11000 and 11001 both say “District of Columbia, not unknown”; they are retained verbatim. Los Angeles County’s 2025 private health care/social assistance row reports 287,445 establishments and 859,824 jobs. This snapshot does not independently establish the administrative explanation for that unusually large establishment count. Use the exact source definitions when comparing establishments across states.
