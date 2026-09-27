import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'export_live_session.py'

class ExportTest(unittest.TestCase):
    def export(self, final_role, final_content, calls=None):
        with tempfile.TemporaryDirectory() as directory:
            db = Path(directory) / 'state.db'
            out = Path(directory) / 'export.json'
            with sqlite3.connect(db) as connection:
                connection.execute('CREATE TABLE messages(id INTEGER PRIMARY KEY, session_id, active, role, content, tool_calls, tool_name)')
                connection.execute('CREATE TABLE session_model_usage(session_id, model, api_call_count, input_tokens, output_tokens, reasoning_tokens, cost_status)')
                for role, content, tool_calls in [('user','Read the agreement',None),('assistant','I will inspect it',None),(final_role,final_content,calls)]:
                    connection.execute('INSERT INTO messages(session_id,active,role,content,tool_calls) VALUES (?,1,?,?,?)',('run',role,content,tool_calls))
            subprocess.run([sys.executable,str(SCRIPT),'--state-db',str(db),'--session-id','run','--out',str(out)],check=True,capture_output=True)
            return json.loads(out.read_text())

    def test_incomplete_turn_does_not_export_earlier_prose_as_final(self):
        for role, content, calls in [('assistant','',None),('tool','Retrieved',None),('assistant','Fetching',json.dumps([{'function':{'name':'get_commitment'}}]))]:
            with self.subTest(role=role,content=content):
                result=self.export(role,content,calls)
                self.assertFalse(result['final_answer_persisted'])
                self.assertEqual(result['final_answer'],'')

    def test_completed_answer_does_not_invent_integration_scope(self):
        result=self.export('assistant','Anthony is recorded as owner.')
        self.assertTrue(result['final_answer_persisted'])
        self.assertEqual(result['final_answer'],'Anthony is recorded as owner.')
        self.assertNotIn('No Google',result['scope'])
        self.assertNotIn('fictional',result['scope'])
