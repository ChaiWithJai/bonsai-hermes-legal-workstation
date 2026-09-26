"""Export per-request Hermes usage, refusing incomplete or duplicate call sequences."""
import argparse
import hashlib
import json
from pathlib import Path
import re


def extract(text, session_id):
    calls = []
    for line in text.splitlines():
        if f'[{session_id}]' not in line or 'API call #' not in line:
            continue
        match = re.search(r'API call #(\d+):.*? in=(\d+) out=(\d+).*?latency=([\d.]+)s', line)
        if not match:
            raise ValueError('Unrecognized usage line; inspect the log format')
        calls.append({'call': int(match[1]), 'input_tokens': int(match[2]),
                      'output_tokens': int(match[3]), 'seconds': float(match[4])})
    if not calls or [c['call'] for c in calls] != list(range(1, len(calls) + 1)):
        raise ValueError('Missing, duplicate or out-of-order request usage')
    ending = [line for line in text.splitlines() if f'[{session_id}]' in line and 'Turn ended:' in line]
    if len(ending) != 1:
        raise ValueError('Require one completed turn; partial or multi-turn logs need separate accounting')
    count = re.search(r'api_calls=(\d+)/', ending[0])
    if not count or int(count[1]) != len(calls):
        raise ValueError('Turn call count does not match recorded usage')
    return {'session_id': session_id, 'calls': calls,
            'total_input_tokens': sum(c['input_tokens'] for c in calls),
            'total_output_tokens': sum(c['output_tokens'] for c in calls),
            'scope': 'One logged model turn; repeated context included; cache discounts not modeled',
            'log_sha256': hashlib.sha256(text.encode()).hexdigest()}

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--log', type=Path, required=True)
    parser.add_argument('--session-id', required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    result = extract(args.log.read_text(), args.session_id)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2) + '\n')
    print(args.out)
