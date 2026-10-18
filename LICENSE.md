# Data license and attribution

The underlying QCEW data and BLS data documentation are public domain U.S. federal government material. The [BLS copyright statement](https://www.bls.gov/opub/copyright-information.htm) permits reuse without specific permission and requests source credit. The [2025 annual bulletin](https://www.bls.gov/cew/publications/employment-and-wages-annual-averages/2025/home.htm) also states that its material may be reproduced with appropriate credit.

Suggested credit: U.S. Bureau of Labor Statistics, Quarterly Census of Employment and Wages, 2025 annual, source snapshot acquired October 18, 2026; datapond derivative identified by its artifact SHA-256.

Changes: exact CSV values are typed into DuckDB; code/title pairs are deduplicated from the same year's official by-area archive; metadata, field dictionary, SQL examples, validation and a disclosure-aware view are added. Raw disclosure flags and original placeholder values remain accessible. The analytical view replaces non-establishment measures with SQL NULL under their respective nondisclosure flags. It does not estimate suppressed values.

No BLS photographs, illustrations or emblem are included. The public-domain data statement does not grant trademark rights or imply BLS endorsement of this derivative.
