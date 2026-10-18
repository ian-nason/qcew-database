
args <- commandArgs(TRUE)
flavor <- args[[1]]
.libPaths(c(file.path(args[[2]],flavor),.libPaths()))
library(datapond)
cat('R',R.version.string,'duckdb',as.character(packageVersion('duckdb')),'datapond',as.character(packageVersion('datapond')),'path',find.package('datapond'),'\n')
cfg <- list(memory_limit='128MiB',threads='1',max_temp_directory_size='0B',autoinstall_known_extensions='false')
options(datapond.cache_dir=args[[4]],datapond.data_dir=args[[5]],datapond.duckdb_config=cfg)
dir.create(args[[4]],recursive=TRUE,showWarnings=FALSE);dir.create(args[[5]],recursive=TRUE,showWarnings=FALSE)
live <- dp_list();print(live);stopifnot(!any(c('onet','qcew','fars') %in% live))
options(datapond.registry_url=args[[3]])
dp_registry(refresh=TRUE)
stopifnot(all(c('onet','qcew','fars') %in% dp_list()))
originalDuckdb <- duckdb::duckdb
if(flavor=='cran') testthat::local_mocked_bindings(duckdb=function(...) {
  a <- list(...)
  if (is.null(a$config)) a$config <- cfg
  do.call(originalDuckdb,a)
},.package='duckdb')
originalExecute <- DBI::dbExecute
testthat::local_mocked_bindings(dbExecute=function(conn,statement,...) {
 if(grepl('INSTALL httpfs',statement,fixed=TRUE)) statement <- gsub('INSTALL httpfs','LOAD httpfs',statement,fixed=TRUE)
 originalExecute(conn,statement,...)
},.package='DBI')
cat("\nDOC BLOCK 2 R\n")
library(DBI)
con <- dbConnect(duckdb::duckdb(config = list(memory_limit = "128MiB", threads = "1", max_temp_directory_size = "0B")))
dbExecute(con, "INSTALL httpfs")
dbExecute(con, "LOAD httpfs")
dbExecute(con, "ATTACH 'https://huggingface.co/datasets/Nason/qcew-database/resolve/334c467dba413928233fb1d8cd1c0ff8de5c0105/qcew.duckdb' AS qcew (READ_ONLY)")
dbGetQuery(con, "SELECT area_fips, area_title, annual_avg_emplvl, avg_annual_pay
                 FROM qcew.annual
                 WHERE agglvl_code = '55' AND own_code = '5' AND industry_code = '621'
                 ORDER BY annual_avg_emplvl DESC NULLS LAST, area_fips")
dbDisconnect(con, shutdown = TRUE)
cat("\nDOC BLOCK 4 R\n")
library(datapond)
dp_list()
con <- dp_connect('qcew')
dp_describe(con, table = 'annual_raw')
DBI::dbGetQuery(con, "SELECT annual_avg_emplvl, total_annual_wages FROM annual WHERE area_fips = 'US000' AND own_code = '0' AND industry_code = '10' AND agglvl_code = '10'")
dp_disconnect(con)
cat("\nDOC BLOCK 6 R\n")
library(datapond)
dp_download('qcew')
con <- dp_connect('qcew', local = TRUE)
DBI::dbGetQuery(con, "SELECT annual_avg_emplvl, total_annual_wages FROM annual WHERE area_fips = 'US000' AND own_code = '0' AND industry_code = '10' AND agglvl_code = '10'")
dp_disconnect(con)
con <- dp_connect('qcew',local=TRUE,quiet=TRUE)
stopifnot(nrow(dp_describe(con)) == 6, nrow(DBI::dbGetQuery(con,'SELECT * FROM _columns')) == 48)
print(DBI::dbGetQuery(con,'SELECT table_name,row_count,column_count FROM _metadata ORDER BY table_name'))
dp_disconnect(con)
cat('FINAL DOCUMENTATION EXAMPLES PASS\n')
