import unittest
from scripts.export_call_usage import extract

class CallUsageTest(unittest.TestCase):
    def test_repeated_context_and_unrelated_session(self):
        text = '[s] API call #1: model=x in=100 out=5 latency=1.0s\n[other] API call #1: in=999 out=99 latency=9s\n[s] API call #2: model=x in=120 out=7 latency=2.0s\n[s] Turn ended: api_calls=2/8'
        result = extract(text, 's')
        self.assertEqual(result['total_input_tokens'], 220)
        self.assertEqual(result['total_output_tokens'], 12)
        with self.assertRaises(ValueError):
            extract(text.replace('api_calls=2/8', 'api_calls=3/8'), 's')
        with self.assertRaises(ValueError):
            extract(text.replace('call #2', 'call #1'), 's')
        with self.assertRaises(ValueError):
            extract(text.split('[s] Turn ended:')[0], 's')
