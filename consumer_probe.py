"""Serve only this artifact on loopback; exercise actual Python/R client readers."""
import argparse,contextlib,hashlib,http.server,io,json,os,pathlib,re,shutil,subprocess,sys,tempfile,threading
from unittest.mock import patch
import duckdb,datapond
import qcew
ROOT=qcew.HERE
DB=ROOT/'releases/2025-release-final/qcew.duckdb'
LOG=[]
class Handler(http.server.BaseHTTPRequestHandler):
 def log_message(self,*args):pass
 def do_HEAD(self):self.send_file(False)
 def do_GET(self):self.send_file(True)
 def send_file(self,body):
  if self.path!='/qcew.duckdb':self.send_error(404);return
  size=DB.stat().st_size;start=0;end=size-1;ran=self.headers.get('Range')
  if ran:
   m=re.fullmatch(r'bytes=(\d+)-(\d*)',ran)
   if not m:self.send_error(416);return
   start=int(m[1]);end=int(m[2]) if m[2] else end
   if start>=size or start>end:self.send_error(416);return
   end=min(end,size-1)
  self.send_response(206 if ran else 200);self.send_header('Content-Length',str(end-start+1));self.send_header('Accept-Ranges','bytes')
  if ran:self.send_header('Content-Range',f'bytes {start}-{end}/{size}')
  self.end_headers()
  if body:
   with DB.open('rb') as f:
    f.seek(start);remaining=end-start+1
    while remaining:
     b=f.read(min(1024*1024,remaining));self.wfile.write(b);remaining-=len(b)
  LOG.append({'method':self.command,'range':ran,'bytes':end-start+1 if body else 0})
def main():
 global DB
 if not __debug__:raise RuntimeError('Run consumer validation without Python optimization')
 parser=argparse.ArgumentParser();parser.add_argument('--artifact',type=pathlib.Path,default=DB);parser.add_argument('--rscript',default=os.environ.get('QCEW_RSCRIPT') or shutil.which('Rscript'));parser.add_argument('--r-lib-root',type=pathlib.Path,default=os.environ.get('QCEW_R_LIB_ROOT'));args=parser.parse_args();DB=args.artifact
 if not args.rscript or not args.r_lib_root:raise ValueError('Specify existing --rscript and --r-lib-root (with cran/patched subdirectories); no software will be installed')
 expected=json.loads((DB.parent/'build-report.json').read_text())['database_sha256'];assert qcew.sha(DB)==expected
 server=http.server.ThreadingHTTPServer(('127.0.0.1',0),Handler);worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start()
 url=f'http://127.0.0.1:{server.server_port}/qcew.duckdb';registry={'databases':[{'id':'qcew','name':'QCEW 2025 annual','rows':3096467,'tables':6,'size_gb':DB.stat().st_size/1e9,'attach_url':url}]}
 path=ROOT/'evidence/consumer-registry.json';qcew.save(path,registry)
 original=duckdb.connect;connections=[];capture=io.StringIO()
 class Bounded:
  def __init__(self):
   self.con=original(config={'memory_limit':'128MiB','threads':'1','max_temp_directory_size':'0B','autoinstall_known_extensions':'false'});self.con.execute('LOAD httpfs');connections.append(self.con)
  def install_extension(self,name):
   assert name=='httpfs';self.con.execute('LOAD httpfs')
  def __getattr__(self,name):return getattr(self.con,name)
 try:
  getter=datapond.connect.__globals__['get_database']
  with patch.dict(getter.__globals__,{'get_registry':lambda **kwargs:registry}),patch.object(duckdb,'connect',side_effect=lambda *a,**k:Bounded()),contextlib.redirect_stdout(capture):
   con=datapond.connect('qcew',quiet=True)
   assert con.execute('SELECT count(*) FROM annual_raw').fetchone()[0]==3089813
   assert con.execute('SELECT sum(row_count) FROM _metadata').fetchone()[0]==3096467
   datapond.describe('qcew');datapond.describe('qcew',table='annual_raw')
   for sql in re.sub(r'--[^\n]*','',(ROOT/'examples.sql').read_text()).split(';'):
    if sql.strip():assert con.execute(sql).fetchall()
  for con in connections:con.close()
  (ROOT/'evidence/python-consumer.txt').write_text(capture.getvalue())
  assert 'annual_avg_emplvl' in capture.getvalue()
  env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1')
  r_provenance={}
  for flavor in ['cran','patched']:
   installed=args.r_lib_root/flavor/'datapond';files={str(f.relative_to(installed)):qcew.sha(f) for f in sorted(installed.rglob('*')) if f.is_file()}
   if not files:raise ValueError('Missing installed R client '+flavor)
   r_provenance[flavor]={'installed_files_sha256':files,'installed_manifest_sha256':hashlib.sha256(json.dumps(files,sort_keys=True).encode()).hexdigest()}
   cache=tempfile.mkdtemp(prefix='r-cache-'+flavor+'-',dir=ROOT/'evidence')
   r=subprocess.run([args.rscript,'--vanilla',str(ROOT/'consumer.R'),str(path),cache,flavor,str(args.r_lib_root)],env=env,capture_output=True,text=True,timeout=120)
   (ROOT/('evidence/r-consumer-'+flavor+'.txt')).write_text(r.stdout+r.stderr)
   assert r.returncode==0,r.stdout+r.stderr
  assert any(x['range'] for x in LOG)
  assert qcew.sha(DB)==expected and not pathlib.Path(str(DB)+'.wal').exists()
  report={'status':'passed_localhost_not_public_host','artifact_sha256':expected,'python_client':datapond.__file__,'python_duckdb':duckdb.__version__,'http_requests':LOG,'transferred_bytes':sum(x['bytes'] for x in LOG),'r_output':['r-consumer-cran.txt','r-consumer-patched.txt'],'r_client_provenance':r_provenance,'artifact_unchanged':True,'resource_limits':'128 MiB per client, one thread, no spill; outer guard covers process group','note':'Local HTTP confirms reader/range compatibility. Actual Hugging Face verification remains required after authorized publication.'}
  qcew.save(ROOT/'evidence/consumer-report.json',report);print(json.dumps({k:v for k,v in report.items() if k!='http_requests'},indent=2))
 finally:server.shutdown();server.server_close();worker.join()
if __name__=='__main__':main()
