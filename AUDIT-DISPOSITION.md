# Independent audit disposition

Session e54f89e5-c01a-468b-8418-436671219b59, initial review 01, 2026-10-18. No independent execution by Claude is claimed.

1. Medium establishment evidence: audit_release.py now reports flagged-row and nonzero counts for all four retained establishment fields. On N rows, LQ has 1,819,361 nonzero values, absolute change 588,950, and percentage change 588,949. README/HF wording says retained exactly as published. This is empirical source evidence, not a claim that every flagged zero is an independently estimated value.
2. UTF-8: reference CSV reads explicitly use UTF-8.
3. National benchmark: README and validation label it a locked original source-row regression value, not an external benchmark. The separate ownership partition and pay-arithmetic checks remain distinct.
4. Test binding: all 35 fixtures reran after the final ingestion edit; evidence/tests03-inputs.json binds ingestion/schema/test/guard/audit bytes. No ingestion/test changes followed that run. Final build, all-cell checks, read-only release audit and Python/R consumers were rerun.
5. Partial extraction: extract_cache writes a new .partial file, checks its hash, then renames it. Partial files are retained and retries explain inspection/quarantine. Failure fixtures demonstrate interrupted and corrupt extraction cannot become a valid cache.
6. Output disk: outputs must resolve inside the guarded repository, including through symlinks, so the same-filesystem free-space check and repository file cap apply. A fixture rejects external output paths. Existing output refusal remains first.
7. Local paths: retained intentionally as build-environment identity for the proposed auditable source payload. No credentials or secrets are included. Public destination approval is pending, and no source was published.
8. DC labels: all three 11-prefixed geography records were checked; 11000 and 11001 have the same unusual official title. Retained unchanged and explained.
9. California: source-faithful Los Angeles row verified. The review's proposed household-employer explanation was not independently verified, so it is not presented as fact. Documentation notes the unusual count and source-specific comparability.
10. R doubles: README distinguishes exact stored BIGINT/DECIMAL from tested client doubles; integer checks are below 2^53 and decimal fractions may be approximate in R.

The new artifact remains local. Exact public-host verification, new repository approval, upload and registry PR are pending. The current source, documentation, HF card, provenance snapshot and proposed registry entry are included in this follow-up.
