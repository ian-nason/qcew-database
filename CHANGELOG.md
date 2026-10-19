# Changelog


## 2026-10-18 — Documentation refresh

- Added Python/R quick starts, table descriptions and column counts, view guidance, navigation, and clearer researcher caveats.
- Database bytes, schema, source locks and validated query results are unchanged. Catalog integration was pending at that checkpoint and was completed later on October 18.

## 2026-10-18 — Initial release

- QCEW 2025 annual: 3,096,467 rows across 6 tables (48 columns) and the `annual` view. Artifact 195,571,712 bytes, SHA-256 `89bf1cef…edbf8a1d`, commit `334c467d`.
- Every typed cell verified against an independent read of the pinned source ZIP; disclosure NULLs checked against their own flags; public immutable URL, HTTP range requests and the installed Python and R clients tested after upload.
- Registry entry opened as a draft pull request, then merged after integration review on October 18.
