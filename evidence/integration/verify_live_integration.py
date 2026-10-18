from pathlib import Path
import contextlib,datetime,hashlib,importlib.metadata,io,json,os,subprocess,sys
from unittest.mock import patch
import datapond,datapond.registry as registry_module,duckdb
ROOT=Path('/home/inason/datapond-maintenance/merge-integration-2026-10-18');OUT=ROOT/'evidence'/('live'+(sys.argv[1] if len(sys.argv)>1 else ''));OUT.mkdir(exist_ok=False)
merge=json.loads((ROOT/'evidence/merges.json').read_text());expected=json.loads((ROOT/'registry/registry.json').read_text())
expected_ids=[x['id'] for x in expected['databases']]
queries={
 'onet':[('metadata','SELECT count(*),sum(row_count),sum(column_count) FROM _metadata',[12,468857,89]),('skill_occupations','SELECT count(DISTINCT onet_soc_code) FROM v_skills',[910])],
 'qcew':[('metadata','SELECT count(*),sum(row_count),sum(column_count) FROM _metadata',[6,3096467,48]),('national_annual',"SELECT annual_avg_emplvl,total_annual_wages FROM annual WHERE area_fips='US000' AND own_code='0' AND industry_code='10' AND agglvl_code='10'",[155732363,12259226899972]),('suppressed',"SELECT count(*) FILTER(WHERE disclosure_code='N'),count(*) FILTER(WHERE lq_disclosure_code='N'),count(*) FILTER(WHERE oty_disclosure_code='N') FROM annual_raw",[1860359,1872172,1937791])],
 'fars':[('metadata','SELECT count(*),sum(row_count),sum(column_count) FROM _metadata',[4,190798,413]),('safe_crash_aggregate','SELECT count(*),sum(fatals),sum(vehicle_records),sum(person_records) FROM crashes',[36297,39254,56011,88326])],
 'fec':[('metadata','SELECT count(*),sum(row_count) FROM _metadata',[10,356327912]),('candidate_cycles','SELECT min(cycle),max(cycle),count(DISTINCT cycle) FROM candidates',[2004,2026,12])],
 'fjc-judges':[('metadata','SELECT count(*),sum(row_count) FROM _metadata',[6,37797]),('judges','SELECT count(*) FROM judges',[4077]),('appointments','SELECT count(*) FROM federal_judicial_service',[4777])],
 'courtlistener':[('metadata','SELECT count(*),sum(row_count) FROM _metadata',[20,2277934]),('judges','SELECT count(*) FROM judges',[16191]),('courts','SELECT count(*) FROM courts',[3361]),('oral_arguments','SELECT count(*) FROM oral_arguments',[103710])]
}
cfg={'memory_limit':'128MiB','threads':'1','max_temp_directory_size':'0B','autoinstall_known_extensions':'false'}
original=duckdb.connect
class Bounded:
 def __init__(self,*a,**kw):
  kw['config']=dict(kw.get('config',{}),**cfg);self.con=original(*a,**kw)
 def install_extension(self,n):
  assert n=='httpfs';self.con.execute('LOAD httpfs')
 def __getattr__(self,n):return getattr(self.con,n)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def manifest(p):return {str(f.relative_to(p)):sha(f) for f in sorted(p.rglob('*')) if f.is_file() and '__pycache__' not in f.parts}
cache=OUT/'python-cache';cache.mkdir();pylog=io.StringIO();pyresults={};known_failures=[]
with patch.object(registry_module,'CACHE_DIR',cache),patch.object(registry_module,'CACHE_FILE',cache/'registry.json'),contextlib.redirect_stdout(pylog):
 ids=datapond.list();assert set(ids)==set(expected_ids) and len(ids)==19,ids
 cached=json.loads((cache/'registry.json').read_text());assert cached==expected,'default catalog differs from reviewed merge candidate'
 with patch.object(duckdb,'connect',side_effect=Bounded):
  for name,qs in queries.items():
   try:
    con=datapond.connect(name,quiet=True)
    # Python 0.1.1 defers ATTACH until the first execution.
    assert con.execute('SELECT count(*) FROM information_schema.tables').fetchone()[0]>0
   except duckdb.ParserException as exc:
    assert name=='fjc-judges' and importlib.metadata.version('datapond')=='0.1.1' and 'syntax error at or near "-"' in str(exc)
    known_failures.append({'id':name,'operation':'datapond.connect','error':str(exc),'scope':'Installed Python 0.1.1 fails to quote hyphenated database IDs. This is a client compatibility limitation, not a failed artifact query. Direct DuckDB quoted-alias check follows separately.'})
    con=duckdb.connect();con.execute('LOAD httpfs');url=next(x['attach_url'] for x in expected['databases'] if x['id']==name)
    con.execute("ATTACH '"+url+"' AS \"fjc-judges\" (READ_ONLY)");con.execute('USE "fjc-judges"')
   runs=[]
   try:
    assert con.execute('SELECT count(*) FROM information_schema.tables').fetchone()[0]>0
    for label,sql,want in qs:
     got=list(con.execute(sql).fetchone());assert got==want,(name,label,got,want)
     runs.append({'label':label,'sql':sql,'result':got})
   finally:con.close()
   pyresults[name]={'connection_mode':'direct_DuckDB_quoted_alias' if name=='fjc-judges' else 'datapond.connect','queries':runs};print(name,'queries passed',flush=True)
   (OUT/'python-progress.json').write_text(json.dumps({'results':pyresults,'known_failures':known_failures},indent=2,default=str)+'\n')
(OUT/'python.txt').write_text(pylog.getvalue())
python={'datapond_version':importlib.metadata.version('datapond'),'duckdb_version':duckdb.__version__,'executable':sys.executable,'runtime':sys.version,'module_path':datapond.__file__,'package_files_sha256':manifest(Path(datapond.__file__).parent),'default_ids':ids,'queries':pyresults,'known_failures':known_failures,'status':'passed_with_documented_client_limitation' if known_failures else 'passed'}
(OUT/'python.json').write_text(json.dumps(python,indent=2,default=str)+'\n')
(OUT/'queries.json').write_text(json.dumps(queries,indent=2)+'\n')
rscript=r'''
args <- commandArgs(TRUE); flavor <- args[[1]]; lib <- args[[2]]; out <- args[[3]]
.libPaths(c(lib,.libPaths()));library(datapond)
cfg <- list(memory_limit='128MiB',threads='1',max_temp_directory_size='0B',autoinstall_known_extensions='false')
cache <- file.path(out,paste0('r-cache-',flavor));dir.create(cache)
options(datapond.cache_dir=cache,datapond.data_dir=file.path(out,paste0('data-',flavor)),datapond.duckdb_config=cfg)
stopifnot(is.null(getOption('datapond.registry_url')))
actual <- dp_registry(refresh=TRUE)
expected <- jsonlite::fromJSON(file.path(dirname(out),'candidate-pr7.json'),simplifyVector=FALSE)
stopifnot(identical(actual,expected),length(dp_list())==19)
originalDuckdb <- duckdb::duckdb
if(flavor=='cran') testthat::local_mocked_bindings(duckdb=function(...) {
 a <- list(...); if(is.null(a$config))a$config <- cfg;do.call(originalDuckdb,a)
},.package='duckdb')
originalExecute <- DBI::dbExecute
testthat::local_mocked_bindings(dbExecute=function(conn,statement,...) {
 if(grepl('INSTALL httpfs',statement,fixed=TRUE))statement <- gsub('INSTALL httpfs','LOAD httpfs',statement,fixed=TRUE)
 originalExecute(conn,statement,...)
},.package='DBI')
qs <- jsonlite::read_json(file.path(out,'queries.json'));results <- list()
for(name in names(qs)) {
 con <- dp_connect(name,quiet=TRUE)
 stopifnot(nrow(dp_describe(con))>0)
 runs <- list()
 for(q in qs[[name]]) {
  row <- DBI::dbGetQuery(con,q[[2]])
  got <- as.numeric(row[1,]);want <- as.numeric(unlist(q[[3]]));stopifnot(identical(got,want))
  runs[[length(runs)+1L]] <- list(label=q[[1]],sql=q[[2]],result=got)
 }
 dp_disconnect(con);results[[name]] <- runs;cat(name,'passed\n')
}
jsonlite::write_json(list(status='passed',datapond_version=as.character(packageVersion('datapond')),duckdb_version=as.character(packageVersion('duckdb')),runtime=R.version.string,library=find.package('datapond'),default_ids=dp_list(),queries=results),file.path(out,paste0('r-',flavor,'.json')),auto_unbox=TRUE,pretty=TRUE)
'''
(OUT/'verify.R').write_text(rscript);rproof={}
for flavor,library in [('cran','/mnt/c/Users/ignna/Documents/Codex/2026-10-17/task-2/libraries/cran'),('patched',str(ROOT/'evidence/r-library'))]:
 with (OUT/('r-'+flavor+'.txt')).open('w') as log:
  run=subprocess.run(['/home/inason/miniconda3/envs/datapond-r/bin/Rscript','--vanilla',str(OUT/'verify.R'),flavor,library,str(OUT)],stdout=log,stderr=subprocess.STDOUT,timeout=360,env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1'))
 assert run.returncode==0,'R '+flavor+' failed; inspect retained log'
 rproof[flavor]=json.loads((OUT/('r-'+flavor+'.json')).read_text());rproof[flavor]['package_files_sha256']=manifest(Path(library)/'datapond')
report={'status':'completed_with_documented_client_limitation' if known_failures else 'passed','completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'merge_commits':merge,'registry_sha256':sha(cache/'registry.json'),'default_registry_url':registry_module.REGISTRY_URL,'registry_override':False,'python':python,'r':rproof,'scope':'Fresh test-owned caches use the unchanged default public registry. Sequential read-only remote queries; no full FEC/CourtListener downloads. Python/CRAN constructors bounded to 128MiB, one thread, no spill; patched R native config. INSTALL httpfs replaced with LOAD of preinstalled extension. Patched project package installed in isolated evidence library; no third-party software or extensions installed. Python 0.1.1 failed the hyphenated FJC identifier; its FJC query results use a separate direct DuckDB connection with a quoted alias, not a claimed successful package connection.'}
(ROOT/'evidence/live-consumers.json').write_text(json.dumps(report,indent=2,default=str)+'\n');print('LIVE DEFAULT CATALOG: 19 IDs in all clients; all six datasets queried, with the documented Python 0.1.1 FJC connection limitation.')
