import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('legal_settings_proxy', ROOT / 'scripts/settings_proxy.py')
proxy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(proxy)

class SamplingTests(unittest.TestCase):
    def test_preserves_tool_conversation_and_applies_explicit_settings(self):
        messages = [{'role':'user','content':'Read APL-008'}]
        tools = [{'type':'function','function':{'name':'get_commitment'}}]
        original = {'messages':messages,'tools':tools,'reasoning_effort':'high','max_completion_tokens':4096,'stream':True}
        result = proxy.configure(original)
        self.assertEqual(result['messages'], messages)
        self.assertEqual(result['tools'], tools)
        self.assertEqual(result['max_tokens'],1536)
        self.assertNotIn('max_completion_tokens',result)
        self.assertNotIn('reasoning_effort',result)
        self.assertEqual(result['chat_template_kwargs'],{'enable_thinking':True,'reasoning_effort':'medium'})
        self.assertFalse(result['stream'])
        self.assertTrue(original['stream'])

    def test_preserves_a_smaller_response_limit(self):
        self.assertEqual(proxy.configure({'max_tokens':512})['max_tokens'],512)
