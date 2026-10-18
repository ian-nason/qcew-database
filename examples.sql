-- One published national all-industry/all-ownership total: never sum the full table.
SELECT area_title,annual_avg_estabs,annual_avg_emplvl,total_annual_wages,avg_annual_pay
FROM annual WHERE area_fips='US000' AND own_code='0' AND industry_code='10'
  AND agglvl_code='10' AND size_code='0' AND year='2025' AND qtr='A';

-- Largest county private health care AND social assistance sectors (NAICS 62).
-- County-equivalent rows include Connecticut planning regions. Exclude unallocated county codes.
SELECT area_fips,area_title,industry_title,annual_avg_estabs,annual_avg_emplvl,
       avg_annual_pay,lq_annual_avg_emplvl,disclosure_code,lq_disclosure_code
FROM annual WHERE agglvl_code='74' AND own_code='5' AND industry_code='62'
  AND right(area_fips,3)<>'999' AND annual_avg_emplvl>0
ORDER BY annual_avg_emplvl DESC,area_fips LIMIT 20;

-- County-level disclosure coverage, including valid establishment counts on suppressed rows.
SELECT disclosure_code,count(*) AS source_cells,
       count(annual_avg_emplvl) AS published_employment_cells,
       sum(annual_avg_estabs) AS published_establishments_rounded
FROM annual WHERE agglvl_code='74' AND own_code='5' AND industry_code='62'
  AND right(area_fips,3)<>'999'
GROUP BY disclosure_code ORDER BY disclosure_code;

-- State private ambulatory health care services (NAICS 621), one industry/ownership grain.
SELECT area_fips,area_title,annual_avg_emplvl,avg_annual_pay,
       oty_annual_avg_emplvl_pct_chg,oty_disclosure_code
FROM annual WHERE agglvl_code='55' AND own_code='5' AND industry_code='621'
ORDER BY annual_avg_emplvl DESC NULLS LAST,area_fips;

-- Compare two disjoint subsectors only after selecting one rating per county/industry.
WITH selected AS (
 SELECT area_fips,area_title,industry_code,annual_avg_emplvl,avg_annual_pay
 FROM annual WHERE agglvl_code='75' AND own_code='5'
  AND industry_code IN ('621','622') AND right(area_fips,3)<>'999'
)
SELECT a.area_fips,a.area_title,a.annual_avg_emplvl AS ambulatory_jobs,
       h.annual_avg_emplvl AS hospital_jobs,a.avg_annual_pay AS ambulatory_pay,
       h.avg_annual_pay AS hospital_pay
FROM selected a JOIN selected h ON a.area_fips=h.area_fips
WHERE a.industry_code='621' AND h.industry_code='622'
ORDER BY a.area_fips LIMIT 20;
