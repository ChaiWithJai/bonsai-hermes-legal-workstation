"""Serve the local cost worksheet, using the CLI's calculation implementation."""
import argparse
from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import math
from pathlib import Path
import sys
from types import SimpleNamespace
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from workload_tco import analyze

FIELDS = 'monthly_attempts machine_price amortization_months idle_watts incremental_watts online_hours end_to_end_seconds electricity_per_kwh local_operations_month hosted_operations_month local_review_per_attempt hosted_review_per_attempt hosted_input_per_million hosted_output_per_million local_acceptance_rate hosted_acceptance_rate'.split()
POSITIVE = {'monthly_attempts', 'amortization_months', 'online_hours', 'end_to_end_seconds', 'local_acceptance_rate', 'hosted_acceptance_rate'}
SESSION = ROOT / 'evidence/slack-anthony-request-usage.json'

def calculate(values):
    if set(values) != set(FIELDS):
        raise ValueError('Enter every assumption before calculating.')
    for key, value in values.items():
        if type(value) not in (int, float) or not math.isfinite(value) or value < 0:
            raise ValueError(f'{key} must be a finite nonnegative number.')
        if key in POSITIVE and value <= 0:
            raise ValueError(f'{key} must be positive.')
        if key.endswith('acceptance_rate') and value > 1:
            raise ValueError('Acceptance fractions must be between 0 and 1.')
    return analyze(json.loads(SESSION.read_text()), SimpleNamespace(**values))

class Handler(BaseHTTPRequestHandler):
    def reply(self, code, data, mime='application/json'):
        body = data.encode() if isinstance(data, str) else json.dumps(data).encode()
        self.send_response(code)
        self.send_header('Content-Type', mime)
        self.send_header('Content-Length', str(len(body)))
        self.send_header('Cache-Control', 'no-store')
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path == '/':
            self.reply(200, (ROOT / 'web/cost/index.html').read_text(), 'text/html; charset=utf-8')
        elif self.path == '/usage':
            self.reply(200, json.loads(SESSION.read_text()))
        else:
            self.reply(404, {'error': 'Not found'})

    def do_POST(self):
        if self.path != '/calculate':
            self.reply(404, {'error': 'Not found'}); return
        # Same-origin browser requests only. The worksheet never writes files.
        if self.headers.get('Origin') not in (None, 'http://' + self.headers.get('Host', '')):
            self.reply(403, {'error': 'Origin rejected'}); return
        try:
            length = int(self.headers.get('Content-Length', '0'))
            if not 0 < length < 16384:
                raise ValueError('Invalid request size')
            result = calculate(json.loads(self.rfile.read(length)))
            self.reply(200, result)
        except (ValueError, TypeError, KeyError) as exc:
            self.reply(400, {'error': str(exc)})

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=5292)
    args = parser.parse_args()
    print(f'Cost worksheet: http://127.0.0.1:{args.port}', flush=True)
    HTTPServer(('127.0.0.1', args.port), Handler).serve_forever()
