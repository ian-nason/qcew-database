# Codex implementation and verification review

> Historical October 18, 2026 checkpoint: the text below is retained as the record of that stage, including its then-pending gates and earlier candidate hashes. It is not current availability or a new approval. Publication and catalog integration are now complete; see the [current README](README.md), [publication receipt](PUBLICATION.md) and [consumer guidance](docs/CONSUMERS.md).

Release artifact `89bf1cef54f42f821965df6e9079b24fc7c4c0c86046fadc98e6cedf9ebd8a1d`, 195,571,712 bytes. This is the primary Codex agent's review, not a claim of an independent second Codex agent.

Data: all 3,089,813 raw rows and typed cells were compared with independent Python CSV/Decimal parsing of the pinned official singlefile ZIP before checkpoint and after read-only reopen. All 6,654 reference rows match exact code/title pairs from the same-year official by-area ZIP. Regenerating the reference CSVs produced byte-identical files. Both official representations have identical ordered non-title string-record SHA-256s. Schemas, 48 dictionary columns, metadata, full keys, references, flags, numeric ranges and counts pass.

Code: unknown/missing fields and flags, bad source hashes, unexpected ZIP members, duplicate keys, precision loss and join inflation fail closed. Raw values stay intact; analytic NULLs are separately checked for level, quotient and change flags, preserving all four source establishment measures. The raw blank-flag CSV fixture prevents accidental conversion to SQL NULL. Source codes preserve leading zeros and wages use BIGINT.

Aggregates/examples: five example queries execute, including county health care and social assistance, state ambulatory care, disclosure coverage and a grain-constrained join. The exact national total is 155,732,363 jobs and $12,259,226,899,972 wages. Disjoint ownership employment/wages reconcile; establishments differ by one due to published rounding. No suppressed-cell reconstruction or unfiltered aggregation is offered.

Resources: the final build took 267.26 seconds and peaked at 411.7 MiB sampled process-group RSS. Engine limits are one thread, 256 MiB RAM and 512 MiB spill; the outer guard stops at 768 MiB RSS, 2 GiB isolated-workspace files, 1.5 GiB available-memory floor, 10 GiB free-disk floor or 15 minutes. Failure evidence is retained; one redundant CSV was removed only after exact hash comparison, with a receipt. O*NET/FEC are untouched.

Consumers: installed Python/DuckDB 1.5.4 and R datapond0.1.0/0.1.1 with DuckDB1.5.5 pass localhost HTTP queries, metadata and suppression checks. Existing httpfs is loaded without installation; each R run gets a fresh cache and installed package hashes. No clean dependency install or public-host result is claimed.

Result: all 35 regression fixtures pass. No remaining local ingestion, validation, documentation or query defect is identified by this Codex review. Independent Claude review is requested with the exact source/docs/evidence payload. Public repository naming approval, upload, immutable remote hash/range checks and public Python/R clients remain external gates.
