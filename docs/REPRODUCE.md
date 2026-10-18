# Build, validation and update details

[Overview](../README.md) · [Dictionary](../DICTIONARY.md) · [Publication verification](../PUBLICATION.md)

These detailed notes preserve the audited release documentation. Statements about local-only checks and later publication gates describe that earlier build stage; [PUBLICATION.md](../PUBLICATION.md) records the completed public-host verification. Catalog integration is complete; see the current [consumer verification](CONSUMERS.md).


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
