"""A failing telemetry fixture must terminate the owned worker, not orphan it."""
import contextlib,io,pathlib,subprocess,sys,tempfile,unittest
from unittest.mock import Mock,patch
import run_guarded
class Guard(unittest.TestCase):
 def test_worker_exits_before_term(self):
  proc=Mock(pid=999999);proc.poll.return_value=None
  with patch.object(run_guarded.os,'killpg',side_effect=ProcessLookupError):run_guarded.stop(proc)
  proc.wait.assert_called_once_with(timeout=5)
 def test_worker_exits_before_kill(self):
  proc=Mock(pid=999999);proc.poll.return_value=None
  proc.wait.side_effect=[subprocess.TimeoutExpired('worker',5),0]
  with patch.object(run_guarded.os,'killpg',side_effect=[None,ProcessLookupError]) as kill:run_guarded.stop(proc)
  self.assertEqual(kill.call_count,2);self.assertEqual(proc.wait.call_count,2)
 def test_sampler_failure_stops_worker(self):
  children=[];original=subprocess.Popen
  def spawn(*args,**kwargs):
   proc=original(*args,**kwargs);children.append(proc);return proc
  with tempfile.TemporaryDirectory() as d:
   root=pathlib.Path(d)
   with patch.object(run_guarded,'ROOT',root),patch.object(sys,'argv',['guard',str(root/'evidence'),sys.executable,'-c','import time; time.sleep(60)']),patch.object(run_guarded.subprocess,'Popen',side_effect=spawn),patch.object(run_guarded,'workspace_bytes',side_effect=OSError('injected telemetry failure')),contextlib.redirect_stdout(io.StringIO()):
    with self.assertRaises(SystemExit) as caught:run_guarded.main()
   self.assertNotEqual(caught.exception.code,0);self.assertEqual(len(children),1);self.assertIsNotNone(children[0].poll())
   self.assertIn('supervisor exception: OSError',(root/'evidence/resources.json').read_text())
if __name__=='__main__':unittest.main(verbosity=2)
