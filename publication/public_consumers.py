"""Installed datapond Python/R readers against a verified immutable public HF URL."""
import contextlib,datetime,hashlib,importlib.metadata,io,json,os,pathlib,re,subprocess,sys,tempfile
from unittest.mock import patch
import datapond,duckdb
pub=pathlib.Path('/home/inason/datapond-maintenance/additions-2026-10-18/publication-2026-10-18')
name=sys.argv[1];plan=json.loads((pub/'publication-plan.json').read_text())['datasets'][name];root=pathlib.Path(plan['source_export']);out=pub/name
state=json.loads((out/'publication.json').read_text());assert state['public_bytes_verified_utc']
artifact=name+'.duckdb';url=state['public_file_verification'][artifact]['public_anonymous_url']
build=json.loads((root/'build-report.json').read_text());expected_rows=plan['manifest'].get('rows') or {'onet':468857,'qcew':3096467,'fars':190798}[name]
tables={'onet':12,'qcew':6,'fars':4}[name];columns={'onet':89,'qcew':48,'fars':413}[name]
registry={'databases':[{'id':name,'name':name.upper()+' audited release','rows':expected_rows,'tables':tables,'size_gb':plan['manifest']['files'][artifact]['bytes']/1e9,'attach_url':url}]}
(out/'public-registry.json').write_text(json.dumps(registry,indent=2)+'\n')
def sha(p):
 with p.open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
original=duckdb.connect;connections=[];capture=io.StringIO()
class Bounded:
 def __init__(self):
  self.con=original(config={'memory_limit':'128MiB','threads':'1','max_temp_directory_size':'0B','autoinstall_known_extensions':'false'});self.con.execute('LOAD httpfs');connections.append(self.con)
 def install_extension(self,n):
  assert n=='httpfs';self.con.execute('LOAD httpfs')
 def __getattr__(self,n):return getattr(self.con,n)
results=[]
try:
 getter=datapond.connect.__globals__['get_database']
 with patch.dict(getter.__globals__,{'get_registry':lambda **kwargs:registry}),patch.object(duckdb,'connect',side_effect=lambda *a,**k:Bounded()),contextlib.redirect_stdout(capture):
  con=datapond.connect(name,quiet=True)
  actual=con.execute('SELECT count(*),sum(row_count),sum(column_count) FROM _metadata').fetchone();assert actual==(tables,expected_rows,columns),actual
  assert con.execute('SELECT count(*) FROM _columns').fetchone()[0]==columns
  counts=con.execute('SELECT table_name,row_count FROM _metadata ORDER BY table_name').fetchall()
  for t,n in counts:assert con.execute('SELECT count(*) FROM "'+t.replace('"','""')+'"').fetchone()[0]==n,t
  datapond.describe(name)
  sample={'onet':'work_context','qcew':'annual_raw','fars':'person'}[name];datapond.describe(name,table=sample)
  for sql in re.sub(r'--[^\n]*','',(root/'examples.sql').read_text()).split(';'):
   if not sql.strip():continue
   cur=con.execute(sql);rows=cur.fetchall();assert rows
   results.append({'sql':sql.strip(),'columns':[c[0] for c in cur.description],'rows':rows})
  if name=='onet':assert str(con.execute("SELECT standard_error FROM work_context WHERE onet_soc_code='11-1011.00' AND element_id='4.C.1.a.2.c' AND scale_id='CX' AND category IS NULL").fetchone()[0])=='0.2851'
  elif name=='qcew':
   assert con.execute("SELECT annual_avg_emplvl,total_annual_wages,avg_annual_pay FROM annual WHERE area_fips='US000' AND own_code='0' AND industry_code='10' AND agglvl_code='10'").fetchone()==(155732363,12259226899972,78720)
   assert con.execute("SELECT count(*) FROM annual WHERE disclosure_code='N' AND annual_avg_emplvl IS NOT NULL").fetchone()[0]==0
  else:assert con.execute('SELECT count(*),sum(fatals),sum(vehicle_records),sum(person_records) FROM crashes').fetchone()==(36297,39254,56011,88326)
finally:
 for con in connections:con.close()
(out/'python-consumer.txt').write_text(capture.getvalue())
(out/'public-examples.json').write_text(json.dumps(results,indent=2,default=str)+'\n')
rscript='/home/inason/miniconda3/envs/datapond-r/bin/Rscript';libs=pathlib.Path('/mnt/c/Users/ignna/Documents/Codex/2026-10-17/task-2/libraries')
env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1');r_provenance={}
script=out/'public-consumer.R';script.write_text((root/'consumer.R').read_text().replace('R localhost HTTP consumer PASS','R immutable public HTTPS consumer PASS'))
for flavor in ['cran','patched']:
 installed=libs/flavor/'datapond';files={str(p.relative_to(installed)):sha(p) for p in sorted(installed.rglob('*')) if p.is_file()};assert files
 cache=tempfile.mkdtemp(prefix='r-cache-'+flavor+'-',dir=out)
 run=subprocess.run([rscript,'--vanilla',str(script),str(out/'public-registry.json'),cache,flavor,str(libs)],env=env,capture_output=True,text=True,timeout=180)
 (out/('r-consumer-'+flavor+'.txt')).write_text(run.stdout+run.stderr);assert run.returncode==0,'R '+flavor+' failed; inspect local output'
 r_provenance[flavor]={'installed_files_sha256':files,'installed_manifest_sha256':hashlib.sha256(json.dumps(files,sort_keys=True).encode()).hexdigest(),'result':'passed'}
report={'status':'passed_immutable_public_host','completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'dataset':name,'hf_commit':state['hf_commit'],'artifact_sha256':plan['manifest']['files'][artifact]['sha256'],'public_artifact_url':url,'python_duckdb':duckdb.__version__,'python_datapond':importlib.metadata.version('datapond'),'python_package_path':datapond.__file__,'python_package_sha256':sha(pathlib.Path(datapond.__file__)),'table_counts':counts,'documented_columns':columns,'example_queries':len(results),'r_clients':r_provenance,'harness':'Installed datapond functions use a local registry override pointing to the immutable public HF URL because the registry PR is not merged. Python/R constructors are bounded, INSTALL is replaced with LOAD of preinstalled httpfs only. All remote data reads use public HTTPS, not localhost.','limits':'128MiB per engine,1 thread,no spill; outer group guard 768MiB; R clients sequential, fresh caches.'}
(out/'public-consumer-report.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k!='r_clients'},indent=2))
