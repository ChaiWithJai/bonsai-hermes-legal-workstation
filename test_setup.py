import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parent

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
