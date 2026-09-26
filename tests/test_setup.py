import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]

class SetupTest(unittest.TestCase):
    def test_profile_resolves_paths_and_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as home:
            env = dict(os.environ, HOME=home,
                       LEGAL_DATA_DIR='fixtures/weekly-review-v3',
                       LEGAL_WORKSTATION_STATE=str(Path(home) / 'register.json'))
            env.pop('LEGAL_GOOGLE_TOKEN', None)
            env.pop('LEGAL_GOOGLE_TOKEN_FILE', None)
            command = [sys.executable, 'setup.py', '--profile', 'setup-check']
            result = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            config = Path(home) / '.hermes/profiles/setup-check/config.yaml'
            original = config.read_bytes()
            server = json.loads(original)['mcp_servers']['legal_workstation']
            self.assertEqual(server['env']['LEGAL_DATA_DIR'], str(ROOT / 'fixtures/weekly-review-v3'))
            request = {'jsonrpc': '2.0', 'id': 1, 'method': 'tools/call',
                       'params': {'name': 'review_commitments', 'arguments': {}}}
            result = subprocess.run([server['command'], *server['args']], cwd=home,
                       env={**env, **server['env']}, input=json.dumps(request)+'\n',
                       capture_output=True, text=True, check=True)
            reply = json.loads(result.stdout)['result']
            self.assertFalse(reply.get('isError'), reply)
            self.assertEqual(json.loads(reply['content'][0]['text'])['count'], 6)
            again = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True)
            self.assertNotEqual(again.returncode, 0)
            self.assertEqual(config.read_bytes(), original)

    def test_profile_preserves_opt_in_tracing_settings(self):
        with tempfile.TemporaryDirectory() as home:
            env = dict(os.environ, HOME=home, LEGAL_TRACE="1",
                       MLFLOW_TRACKING_URI="http://127.0.0.1:5210")
            subprocess.run([sys.executable, "setup.py", "--profile", "trace-check"],
                           cwd=ROOT, env=env, capture_output=True, text=True, check=True)
            config = json.loads((Path(home) / ".hermes/profiles/trace-check/config.yaml").read_text())
            settings = config["mcp_servers"]["legal_workstation"]["env"]
            self.assertEqual(settings["LEGAL_TRACE"], "1")
            self.assertEqual(settings["MLFLOW_TRACKING_URI"], "http://127.0.0.1:5210")

    def test_python_symlink_is_preserved_for_virtual_environment(self):
        with tempfile.TemporaryDirectory() as home:
            interpreter = Path(home) / "venv" / "bin" / "python"
            interpreter.parent.mkdir(parents=True)
            interpreter.symlink_to(sys.executable)
            env = dict(os.environ, HOME=home, LEGAL_PYTHON=str(interpreter))
            subprocess.run([sys.executable, "setup.py", "--profile", "interpreter-check"],
                           cwd=ROOT, env=env, capture_output=True, text=True, check=True)
            config = json.loads((Path(home) / ".hermes/profiles/interpreter-check/config.yaml").read_text())
            self.assertEqual(config["mcp_servers"]["legal_workstation"]["command"], str(interpreter.absolute()))
