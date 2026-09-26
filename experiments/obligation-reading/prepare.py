"""Freeze a development comparison; preparation never runs inference."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
SOURCE = ROOT / 'agreements/northstar-order-form.md'


def prepare():
    source = SOURCE.read_text()
    prompt = (
        'Read Section 2.1 of the supplied agreement. Return a JSON object with '
        'provider, provider_deliverables, provider_due_date, customer, '
        'customer_deliverables and customer_due_date. Use an ISO date when the '
        'section states one and null when it does not. Keep the obligations '
        'of the two parties separate. Do not infer a date for the customer.\n\n'
        + source
    )
    common = {
        'model': 'bonsai-ui-public-ternary-bonsai2',
        'messages': [{'role': 'user', 'content': prompt}],
        'temperature': 1.0, 'top_p': 0.95, 'top_k': 20, 'min_p': 0.05,
        'seed': 42, 'stream': False,
    }
    variants = [{**common, 'max_tokens': cap} for cap in (512, 1024)]
    protocol = {
        'status': 'prepared_not_executed',
        'scope': 'Development case derived from the observed APL-008 party-attribution error. Not held-out evaluation.',
        'question': 'Does the response limit prevent a complete, correct extraction of both parties and their obligations?',
        'changed_variable': 'max_tokens',
        'source': str(SOURCE.relative_to(ROOT)),
        'source_sha256': hashlib.sha256(SOURCE.read_bytes()).hexdigest(),
        'request_sha256': [hashlib.sha256(json.dumps(v, sort_keys=True).encode()).hexdigest() for v in variants],
        'execution': 'Run sequentially under the shared GPU queue. Capture model and runtime hashes, launch flags, hardware, server state and every raw response before interpreting results.',
        'timing': 'Use alternating order across repeated paired runs; record prompt-cache usage. A single pair cannot establish a latency improvement.',
        'review': 'Score JSON syntax, each party, each deliverable, date and missing-date handling separately. Human review is required for semantic equivalence and usefulness.',
        'claims_excluded': ['Hermes tool selection', 'Slack workflow completion', 'human acceptance', 'general legal accuracy', 'operating savings'],
    }
    for cap, payload in zip((512, 1024), variants):
        (OUT / f'request-{cap}.json').write_text(json.dumps(payload, indent=2)+'\n')
    (OUT / 'protocol.json').write_text(json.dumps(protocol, indent=2)+'\n')
    print('Prepared two requests from the same source and prompt. No inference was run.')


if __name__ == '__main__':
    prepare()
