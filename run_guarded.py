"""Run a build under measured outer limits; writes only a new evidence folder."""
import argparse,datetime,fcntl,hashlib,json,os,pathlib,shutil,signal,subprocess,time
ROOT=pathlib.Path(__file__).resolve().parent
def workspace_bytes():
 total=0
 for path in ROOT.rglob('*'):
  try:
   if path.is_file():total+=path.stat().st_size
  except FileNotFoundError:pass  # A WAL or spill file can disappear between reads.
 return total
def stop(proc):
 if proc.poll() is None:
  try:os.killpg(proc.pid,signal.SIGTERM)
  except ProcessLookupError:pass  # The worker can finish after poll().
  try:proc.wait(timeout=5)
  except subprocess.TimeoutExpired:
   try:os.killpg(proc.pid,signal.SIGKILL)
   except ProcessLookupError:pass
   proc.wait()
def main():
 p=argparse.ArgumentParser();p.add_argument('evidence_dir',type=pathlib.Path);p.add_argument('command',nargs=argparse.REMAINDER);a=p.parse_args()
 if not a.command:raise ValueError('A command is required')
 lock=(ROOT/'.build.lock').open('a');fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
 a.evidence_dir.mkdir(parents=True,exist_ok=False)
 env=os.environ.copy();env.update(OPENBLAS_NUM_THREADS='1',OMP_NUM_THREADS='1',DATAPOND_MEMORY_LIMIT='256MiB',DATAPOND_THREADS='1')
 start=time.monotonic();peak_rss=peak_disk=0;minimum_free=2**63;reason=None
 with (a.evidence_dir/'stdout.txt').open('w') as out,(a.evidence_dir/'stderr.txt').open('w') as err:
  proc=subprocess.Popen(a.command,cwd=ROOT,env=env,stdout=out,stderr=err,start_new_session=True)
  try:
   while proc.poll() is None:
    rss=0
    for status in pathlib.Path('/proc').glob('[0-9]*/status'):
     try:
      if os.getpgid(int(status.parent.name))==proc.pid:
       rss+=sum(int(x.split()[1])*1024 for x in status.read_text().splitlines() if x.startswith('VmRSS:'))
     except OSError:pass
    disk=workspace_bytes()
    available=next(int(x.split()[1])*1024 for x in pathlib.Path('/proc/meminfo').read_text().splitlines() if x.startswith('MemAvailable:'))
    peak_rss=max(peak_rss,rss);peak_disk=max(peak_disk,disk);minimum_free=min(minimum_free,available)
    if rss>768*1024**2:reason='RSS over 768 MiB'
    elif disk>2*1024**3:reason='workspace files over 2 GiB'
    elif available<1536*1024**2:reason='available RAM below 1.5 GiB'
    elif shutil.disk_usage(ROOT).free<10*1024**3:reason='free disk below 10 GiB'
    elif time.monotonic()-start>900:reason='15 minute deadline'
    if reason:stop(proc);break
    time.sleep(.25)
  except BaseException as exc:
   reason='supervisor exception: '+type(exc).__name__
   stop(proc)
  code=proc.wait()
 report={'command':a.command,'guard_sha256':hashlib.sha256(pathlib.Path(__file__).read_bytes()).hexdigest(),'exit_code':code,'stop_reason':reason,'elapsed_seconds':time.monotonic()-start,'peak_process_group_rss_bytes_sampled':peak_rss,'peak_workspace_file_bytes_sampled':peak_disk,'workspace_file_scope':'All files under this isolated repository, including retained attempts and .git','minimum_available_memory_bytes':minimum_free,'sample_interval_seconds':.25,'completed_utc':datetime.datetime.now(datetime.timezone.utc).isoformat()}
 (a.evidence_dir/'resources.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
 lock.close()
 raise SystemExit(code or bool(reason))
if __name__=='__main__':
 def terminate(signum,frame):raise InterruptedError('Supervisor termination requested')
 signal.signal(signal.SIGTERM,terminate)
 main()
