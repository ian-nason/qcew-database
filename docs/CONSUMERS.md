# Python and R consumer verification

[Overview](../README.md) · [Publication](../PUBLICATION.md) · [Machine-readable results](../evidence/documentation/report.json)

## Current starting point — October 19, 2026

Use Python datapond 0.1.5 or later (`python -m pip install --upgrade datapond`) or released CRAN R datapond 0.1.0 (`install.packages("datapond")`). The R 0.1.1 startup resource controls are development features. Python 0.1.5 includes the identifier-quoting fix documented in the 0.1.2 release notes; the older 0.1.1 installation described below lacks it. Check the version and loaded path in your own environment; the paths in the historical reports identify the audited machine.

For a reproducible local copy, use the README's immutable URL and verify its SHA-256. Inspection of Python 0.1.5 confirms that its optional `huggingface_hub` path still omits `revision`; the older download caveat below therefore remains relevant. The earlier full-download checks are not being relabeled as 0.1.5 tests.

## Original documentation verification — October 18, 2026

The final reader examples were executed on October 18, 2026, against the immutable public artifact and against full, hash-verified local downloads. Discovery, schema descriptions, representative queries, download and local connection passed in each deliberately selected environment below. No packages or extensions were installed.

| Client | Exact tested version | Runtime and actual loaded path |
|---|---|---|
| Python datapond | 0.1.1 | Python 3.12, DuckDB 1.5.4; `/home/inason/datapond-maintenance/.venv-datapond/lib/python3.12/site-packages/datapond/__init__.py` |
| Released CRAN datapond | 0.1.0 | R 4.5.3, DuckDB 1.5.5; `/mnt/c/Users/ignna/Documents/Codex/2026-10-17/task-2/libraries/cran/datapond` |
| Isolated patched datapond | 0.1.1 | R 4.5.3, DuckDB 1.5.5; `/mnt/c/Users/ignna/Documents/Codex/2026-10-17/task-2/libraries/patched/datapond` |

Package version labels alone do not identify editable or patched installations. The result file records the executable/module/library paths and SHA-256 for installed package files. These results do not claim that the default shell import, another R library also labeled 0.1.1, or the latest Python source checkout was tested. The patched R build is separate from the released CRAN 0.1.0 package; no CRAN submission was made.

## Historical post-merge check before the Python upgrade

After the registry merge, fresh caches using the unchanged public default registry
URL discovered all 19 IDs in installed Python datapond 0.1.1, released CRAN
datapond 0.1.0, and an isolated R 0.1.1 installation built from the merged PR.
Representative package connections and queries passed for O*NET, QCEW, FARS,
FEC and CourtListener in all three clients, and for FJC judges in both R clients.
Installed Python 0.1.1 fails to quote the hyphenated `fjc-judges` ID when attaching;
its FJC package connection failed. A separate direct DuckDB connection using the
quoted alias `"fjc-judges"` passed the FJC artifact queries. This fallback is not
counted as a successful Python package connection. No registry fixture or URL
override was used for these post-merge checks. The machine-readable [live integration report](../evidence/integration/live-consumers.json)
records exact source commits, package paths, runtime versions and query results.
The resource controls and preinstalled-extension substitution described below
also apply to this check. The earlier full-download results remain unchanged.

## Earlier candidate-catalog and resource scope

The default public registry was fetched into a fresh cache and returned **16 existing IDs**, without `onet`, `qcew` or `fars`. The package examples then used a **local 19-entry candidate fixture**, preserving PR #4's refreshed metadata and the three proposed additions. That tests the clients against the proposed entries; it does **not** establish live default-catalog discovery. The direct DuckDB examples use immutable public URLs independently of the catalog.

Query connections were limited to 128 MiB, one thread and no spill. Direct examples specify their limits. The harness bounds the installed Python constructor and released R 0.1.0 constructor; the isolated patched R 0.1.1 uses its real `datapond.duckdb_config` option. The patched download validator ran unmodified with its default connection and a minimal `SELECT 1`; the outer process-group guard still applied. The outer supervisor measures the full process group with a 768 MiB RSS stop and bounded disk/runtime. Package cache/data paths are redirected to test-owned directories, and `INSTALL httpfs` is replaced with `LOAD httpfs` of the already installed extension. All actual remote database reads use public HTTPS.

The October 18 Markdown blocks are saved verbatim in [doc-blocks.json](../evidence/documentation/doc-blocks.json). Python and R blocks were executed in order, including the documented download/local examples. The standalone SQL blocks were executed with Python DuckDB. Schema totals and meaningful source-derived aggregates were asserted separately. Each of the three downloaded copies matched SHA-256 `89bf1cef54f42f821965df6e9079b24fc7c4c0c86046fadc98e6cedf9ebd8a1d`. Query outputs and package identities are retained alongside the harness in [evidence/documentation](../evidence/documentation/).

## Known download limitation in tested Python 0.1.1

This environment has no optional `huggingface_hub` dependency, so `datapond.download()` used its requests fallback and the registry's immutable `attach_url`. Inspection of the installed Python 0.1.1 implementation shows that, **when `huggingface_hub` is present**, its preferred download call omits `revision` and follows the Hugging Face repository's current default branch. It therefore does not preserve an immutable `attach_url` pin. No package code was changed for these documentation updates. Use the pinned direct URL and verify the recorded artifact SHA-256 for a reproducible local copy; do not assume the optional download path is version-pinned.

## Test corrections

The shared harness, first run on O*NET, initially redirected the downloader but missed the connection's independently constructed home path. A second attempt unnecessarily wrapped the patched R constructor, interfering with its download validation. Both were corrected in the harness: test-owned Python home paths are consistent, and patched R uses its native constructor. The unmocked patched validator also passed independently on an already verified artifact. Those failed attempts are retained in the local QA workspace; they were not attributed to a package defect.
