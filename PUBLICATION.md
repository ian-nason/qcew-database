# Verified public release

> Historical checkpoint, recorded before catalog integration. The dataset is now in the public catalog: [registry PR #6](https://github.com/datapond-db/registry/pull/6) merged on October 18, 2026. The dated checks and version labels below are preserved; see [current consumer guidance](docs/CONSUMERS.md).

Published October 18, 2026. [Dataset](https://huggingface.co/datasets/Nason/qcew-database) and [immutable dataset commit](https://huggingface.co/datasets/Nason/qcew-database/commit/334c467dba413928233fb1d8cd1c0ff8de5c0105). The corresponding registry submission is a draft PR; global datapond discovery is not claimed until that PR is merged.

Artifact: `qcew.duckdb`, 195,571,712 bytes, SHA-256 `89bf1cef54f42f821965df6e9079b24fc7c4c0c86046fadc98e6cedf9ebd8a1d`. All four uploaded files were streamed anonymously from the immutable public commit and matched their frozen sizes/checksums. A 4096-byte range request returned HTTP 206 with the exact Content-Range and original bytes. See publication/public-byte-verification.json.

```sql
LOAD httpfs;
ATTACH 'https://huggingface.co/datasets/Nason/qcew-database/resolve/334c467dba413928233fb1d8cd1c0ff8de5c0105/qcew.duckdb' AS qcew (READ_ONLY);
SELECT table_name,row_count,column_count FROM qcew._metadata ORDER BY table_name;
```

Installed datapond Python (0.1.1, DuckDB 1.5.4) and R datapond 0.1.0/0.1.1 (DuckDB 1.5.5) passed actual public-HTTPS metadata, row-count and meaningful semantic queries. Python also executed all 5 audited example queries. Before registry merge, tests use a local registry override whose attach_url is the immutable public URL above. Existing httpfs was loaded; no software was installed. Test constructors were bounded to 128 MiB, one thread and no spill, under the 768 MiB group guard. Exact installed package identities and outputs are retained in publication/.

The audited local source snapshot is `75499207f3c0b20087587435a8774056aeaf4dd5`; the public source export starts at `2ab9fe0dd73f8a48f0d3be12a7b1c6b45d3058a9`. PUBLICATION-EXPORT.json maps byte-identical audited source files and any private exclusions. A fresh public history prevents accidental publication of private historical material. This commit adds hosting evidence and a publication-status notice to README; it changes no ingestion code, audited database, dictionaries or source data. Original audit/source manifests and historical pre-publication status text remain intact as evidence.

Independent Claude reviews covered supplied code/documentation/evidence, not independent execution or hash recomputation. Public-host checks were subsequently executed by Codex. All audit findings were resolved before upload. No registry PR merge or CRAN submission is included.
