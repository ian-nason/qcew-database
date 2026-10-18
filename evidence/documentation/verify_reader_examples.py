"""Execute final Markdown examples with deliberately selected installed clients."""
import contextlib,datetime,hashlib,importlib,importlib.metadata,io,json,os,pathlib,re,subprocess,sys
from unittest.mock import patch
import datapond,duckdb,datapond.registry as registry_module
ROOT=pathlib.Path('/home/inason/datapond-maintenance/additions-2026-10-18/documentation-2026-10-18')
name=sys.argv[1];out=ROOT/'qa'/name/(sys.argv[2] if len(sys.argv)>2 else 'attempt01');out.mkdir(parents=True,exist_ok=False)
baseline=json.loads((ROOT/'baseline.json').read_text())['sources'][name]
registry=json.loads((ROOT/'qa/candidate-registry.json').read_text())
blocks=json.loads((ROOT/'qa'/(name+'-doc-blocks.json')).read_text())
cfg={'memory_limit':'128MiB','threads':'1','max_temp_directory_size':'0B','autoinstall_known_extensions':'false'}
def sha(p):
 with pathlib.Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def manifest(p):return {str(f.relative_to(p)):sha(f) for f in sorted(p.rglob('*')) if f.is_file() and '__pycache__' not in f.parts}
original_connect=duckdb.connect;connections=[]
class Bounded:
 def __init__(self,*a,**kw):
  kw['config']=dict(kw.get('config',{}),**cfg);self.con=original_connect(*a,**kw);connections.append(self.con)
 def install_extension(self,n):
  assert n=='httpfs';self.con.execute('LOAD httpfs')
 def __getattr__(self,k):return getattr(self.con,k)

cache=out/'python-cache';data=out/'python-home'/'.datapond';cache.mkdir(exist_ok=True);data.mkdir(parents=True,exist_ok=True)
pylog=io.StringIO();results=[]
with patch.object(registry_module,'CACHE_DIR',cache),patch.object(registry_module,'CACHE_FILE',cache/'registry.json'),contextlib.redirect_stdout(pylog):
 live=datapond.list();assert all(n not in live for n in ['onet','qcew','fars']),live
 # Local candidate cache exercises list/get_database normally; no private get_database mock.
 (cache/'registry.json').write_text(json.dumps(registry))
 assert set(datapond.list())=={x['id'] for x in registry['databases']}
 globals_to_patch=[]
 for module_name in ['datapond.connection','datapond.download']:
  mod=importlib.import_module(module_name)
  if hasattr(mod,'DATAPOND_DIR'):globals_to_patch.append(mod)
 with contextlib.ExitStack() as stack:
  for mod in globals_to_patch:stack.enter_context(patch.object(mod,'DATAPOND_DIR',data))
  class IsolatedPath(type(pathlib.Path())):
   @classmethod
   def home(cls):return data.parent
  stack.enter_context(patch.object(importlib.import_module('datapond.connection'),'Path',IsolatedPath))
  stack.enter_context(patch.object(duckdb,'connect',side_effect=Bounded))
  # Execute Python and standalone SQL exactly, except no INSTALL: load preinstalled httpfs.
  for index,b in enumerate(blocks):
   if b['language']=='python':
    print('\nDOC BLOCK',index,'python');namespace={}
    exec(compile(b['code'].replace('INSTALL httpfs','LOAD httpfs'),str(ROOT/'hf-cards'/(name+'.md')),'exec'),namespace)
    results.append({'block':index,'language':'python','sha256':hashlib.sha256(b['code'].encode()).hexdigest(),'status':'passed'})
   elif b['language']=='sql':
    if 'ATTACH ' in b['code']:
     sqlcon=duckdb.connect();cur=sqlcon.execute(b['code'].replace('INSTALL httpfs','LOAD httpfs'))
    else:cur=sqlcon.execute(b['code'])
    rows=cur.fetchall();assert rows;print('SQL BLOCK',index,'rows',len(rows),'first',rows[0])
    results.append({'block':index,'language':'sql','sha256':hashlib.sha256(b['code'].encode()).hexdigest(),'rows':rows,'columns':[x[0] for x in cur.description]})
  con=datapond.connect(name,quiet=True)
  meta=con.execute('SELECT count(*),sum(row_count),sum(column_count) FROM _metadata').fetchone()
  assert meta=={'onet':(12,468857,89),'qcew':(6,3096467,48),'fars':(4,190798,413)}[name]
  schema=con.execute('SELECT table_name,column_name,data_type FROM information_schema.columns ORDER BY table_name,ordinal_position').fetchall()
  if name=='onet':
   assert con.execute('SELECT count(DISTINCT onet_soc_code) FROM v_skills').fetchone()[0]==910
   assert con.execute('SELECT count(DISTINCT onet_soc_code),count(DISTINCT element_id) FROM v_work_context_means').fetchone()==(911,57)
   assert con.execute('SELECT count(DISTINCT onet_soc_code) FROM v_work_context_percentages').fetchone()[0]==902
  elif name=='qcew':
   assert con.execute("SELECT count(*) FILTER(WHERE disclosure_code='N'),count(*) FILTER(WHERE lq_disclosure_code='N'),count(*) FILTER(WHERE oty_disclosure_code='N') FROM annual_raw").fetchone()==(1860359,1872172,1937791)
   assert con.execute("SELECT annual_avg_emplvl,total_annual_wages FROM annual WHERE area_fips='US000' AND own_code='0' AND industry_code='10' AND agglvl_code='10'").fetchone()==(155732363,12259226899972)
  else:
   assert con.execute('SELECT count(*),sum(fatals),sum(vehicle_records),sum(person_records) FROM crashes').fetchone()==(36297,39254,56011,88326)
   assert con.execute('SELECT count(*) FROM crashes WHERE latitude_degrees IS NULL OR longitude_degrees IS NULL').fetchone()[0]==170
  con.close()
 for c in connections:
  try:c.close()
  except Exception:pass
assert sha(data/(name+'.duckdb'))==baseline['artifact']['sha256']
(out/'python.txt').write_text(pylog.getvalue())

# Execute the final R blocks with CRAN and patched libraries, separately.
libs=pathlib.Path('/mnt/c/Users/ignna/Documents/Codex/2026-10-17/task-2/libraries')
prefix=r'''
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
'''
rblocks='\n'.join('cat("\\nDOC BLOCK '+str(i)+' R\\n")\n'+b['code'] for i,b in enumerate(blocks) if b['language']=='r')
suffix=f'''
con <- dp_connect('{name}',local=TRUE,quiet=TRUE)
stopifnot(nrow(dp_describe(con)) == {meta[0]}, nrow(DBI::dbGetQuery(con,'SELECT * FROM _columns')) == {meta[2]})
print(DBI::dbGetQuery(con,'SELECT table_name,row_count,column_count FROM _metadata ORDER BY table_name'))
dp_disconnect(con)
cat('FINAL DOCUMENTATION EXAMPLES PASS\\n')
'''
script=out/'examples.R';script.write_text(prefix+rblocks+suffix)
rproof={}
for flavor,version in [('cran','0.1.0'),('patched','0.1.1')]:
 rc=out/('r-cache-'+flavor);rd=out/('r-data-'+flavor)
 run=subprocess.run(['/home/inason/miniconda3/envs/datapond-r/bin/Rscript','--vanilla',str(script),flavor,str(libs),str(ROOT/'qa/candidate-registry.json'),str(rc),str(rd)],capture_output=True,text=True,timeout=360,env=dict(os.environ,OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1'))
 (out/('r-'+flavor+'.txt')).write_text(run.stdout+run.stderr)
 assert run.returncode==0,'R '+flavor+' failed: '+run.stderr[-1400:]
 assert 'datapond '+version+' path' in run.stdout
 assert sha(rd/(name+'.duckdb'))==baseline['artifact']['sha256']
 rproof[flavor]={'version':version,'library':str(libs/flavor/'datapond'),'files_sha256':manifest(libs/flavor/'datapond'),'download_sha256':sha(rd/(name+'.duckdb')),'status':'passed'}
report={'dataset':name,'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'passed','python':{'executable':sys.executable,'version':sys.version,'datapond_version':importlib.metadata.version('datapond'),'module_path':datapond.__file__,'package_files_sha256':manifest(pathlib.Path(datapond.__file__).parent),'duckdb_version':duckdb.__version__,'download_sha256':sha(data/(name+'.duckdb'))},'r':rproof,'metadata_totals':meta,'schema':schema,'blocks':results,'live_default_ids':live,'candidate_ids':[x['id'] for x in registry['databases']],'artifact_sha256':baseline['artifact']['sha256'],'scope':'Final Markdown Python and R examples executed for remote, discovery/schema, download and local modes. Standalone SQL executed with Python DuckDB. Registry fixture supplied through isolated Python cache / R registry option. Default URL separately returned 16 entries without the additions. Constructors bounded to 128MiB/one thread/no spill; INSTALL replaced with LOAD of preinstalled httpfs. No software installed. Python Hugging Face optional dependency is absent, so download used the immutable requests fallback. No claim that a different default shell import or current source checkout was tested.'}
(out/'report.json').write_text(json.dumps(report,indent=2,default=str)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['python','r','schema','blocks']},indent=2))
