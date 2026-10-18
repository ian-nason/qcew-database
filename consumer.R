args <- commandArgs(TRUE)
flavor <- if(length(args)>=3) args[[3]] else 'patched'
.libPaths(c(file.path(args[[4]],flavor),.libPaths()))
library(datapond)
cat('R',R.version.string,'duckdb',as.character(packageVersion('duckdb')),'datapond',as.character(packageVersion('datapond')),'\n')
cfg <- list(memory_limit='128MiB',threads='1',max_temp_directory_size='0B',autoinstall_known_extensions='false')
options(datapond.registry_url=args[[1]],datapond.cache_dir=args[[2]],datapond.duckdb_config=cfg)
driver <- duckdb::duckdb(config=cfg)
probe <- DBI::dbConnect(driver)
stopifnot(isTRUE(DBI::dbGetQuery(probe,"SELECT installed FROM duckdb_extensions() WHERE extension_name='httpfs'")$installed[[1]]))
DBI::dbDisconnect(probe,shutdown=TRUE)
if(flavor=='cran') {
  originalDuckdb <- duckdb::duckdb
  testthat::local_mocked_bindings(duckdb=function(...) originalDuckdb(...,config=cfg),.package='duckdb')
  cat('CRAN driver constructor bounded by test harness; datapond functions unchanged.\n')
}
# dp_connect calls INSTALL; replace only that instruction in this process with
# LOAD of the preinstalled extension. No software download/install is allowed.
originalExecute <- DBI::dbExecute
testthat::local_mocked_bindings(dbExecute=function(conn,statement,...) {
  if(grepl('INSTALL httpfs',statement,fixed=TRUE)) statement <- gsub('INSTALL httpfs','LOAD httpfs',statement,fixed=TRUE)
  originalExecute(conn,statement,...)
},.package='DBI')
con <- dp_connect('qcew',quiet=TRUE)
tryCatch({
  stopifnot(DBI::dbGetQuery(con,'SELECT count(*) AS n FROM annual_raw')$n[[1]]==3089813)
  stopifnot(DBI::dbGetQuery(con,'SELECT sum(row_count) AS n FROM _metadata')$n[[1]]==3096467)
  stopifnot(nrow(dp_describe(con))==6,nrow(dp_describe(con,table='annual_raw'))==38)
  stopifnot(DBI::dbGetQuery(con,'SELECT count(*) AS n FROM _columns')$n[[1]]==48)
  x <- DBI::dbGetQuery(con,"SELECT area_title,annual_avg_emplvl,total_annual_wages,avg_annual_pay FROM annual WHERE area_fips='US000' AND own_code='0' AND industry_code='10' AND agglvl_code='10'")
  stopifnot(nrow(x)==1,as.numeric(x$annual_avg_emplvl[[1]])==155732363,as.numeric(x$total_annual_wages[[1]])==12259226899972,x$avg_annual_pay[[1]]==78720)
  print(x)
  suppressed <- DBI::dbGetQuery(con,"SELECT annual_avg_estabs,annual_avg_emplvl FROM annual WHERE disclosure_code='N' AND annual_avg_estabs>0 LIMIT 1")
  stopifnot(nrow(suppressed)==1,is.na(suppressed$annual_avg_emplvl[[1]]),suppressed$annual_avg_estabs[[1]]>0)
  print(dplyr::collect(utils::head(dplyr::tbl(con,'annual'),3)))
  cat('R localhost HTTP consumer PASS\n')
},finally=dp_disconnect(con))
