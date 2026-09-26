import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]

class VersionedFixtureTest(unittest.TestCase):
    def test_review_context_assignment_and_original_state(self):
        original = (ROOT / 'state.json').read_bytes() if (ROOT / 'state.json').exists() else None
        with tempfile.TemporaryDirectory() as directory:
            env = dict(os.environ, LEGAL_DATA_DIR=str(ROOT / 'fixtures/weekly-review-v2'),
                       LEGAL_WORKSTATION_STATE=str(Path(directory) / 'state.json'))
            env.pop('LEGAL_GOOGLE_TOKEN', None)
            env.pop('LEGAL_GOOGLE_TOKEN_FILE', None)
            calls = [
                ('review_commitments', {}),
                ('get_commitment', {'commitment_id': 'APL-007'}),
                ('assign_owner', {'commitment_id': 'APL-007', 'owner': 'Khizar', 'expected_revision': 0}),
                ('get_commitment', {'commitment_id': 'APL-007'}),
            ]
            requests = '\n'.join(json.dumps({'jsonrpc': '2.0', 'id': i, 'method': 'tools/call',
                'params': {'name': name, 'arguments': args}}) for i, (name, args) in enumerate(calls)) + '\n'
            proc = subprocess.run([sys.executable, str(ROOT / 'commitments.py')], input=requests,
                                  text=True, capture_output=True, env=env, check=True)
            results = [json.loads(line)['result'] for line in proc.stdout.splitlines()]
            self.assertTrue(all(not result.get('isError') for result in results), results)
            values = [json.loads(result['content'][0]['text']) for result in results]
            self.assertEqual(values[0]['count'], 6)
            self.assertNotIn('APL-001', [row['id'] for row in values[0]['commitments']])
            self.assertIn('September 18', values[1]['delivery_context']['text'])
            self.assertEqual(values[1]['delivery_context']['source_kind'], 'local_sample_account_history')
            self.assertEqual(values[2]['sheet_sync'], 'mocked_local_only')
            self.assertEqual(values[3]['owner'], 'Khizar')
            self.assertEqual(values[3]['revision'], 1)
        self.assertEqual((ROOT / 'state.json').read_bytes() if (ROOT / 'state.json').exists() else None, original)

    def test_harbor_trigger_is_delivery_without_customer_blame(self):
        seed = json.loads((ROOT / 'fixtures/weekly-review-v3/seed.json').read_text())
        row = next(item for item in seed['commitments'] if item['id'] == 'APL-004')
        self.assertEqual(row['due_date'], '')
        self.assertEqual(row['status'], 'awaiting_delivery_confirmation')
        self.assertIn('five business days after that delivery', row['evidence_needed'])
        self.assertNotEqual(row['status'], 'waiting_on_client')
