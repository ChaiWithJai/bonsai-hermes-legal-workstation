"""Read the configured Google register and source clauses without changing data."""
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import commitments

def check():
    if not commitments.google_configured():
        raise RuntimeError('Configure LEGAL_GOOGLE_TOKEN_FILE before checking Google access')
    review = commitments.execute('review_commitments', {'unassigned_only': False})
    if not review['commitments']:
        raise RuntimeError('The Google Sheet contains no open commitments')
    sources = []
    for row in review['commitments']:
        source = commitments.execute('get_commitment', {'commitment_id': row['id']})
        sources.append({'commitment_id': row['id'], 'source_kind': source['source_kind'],
                        'clause_sha256': hashlib.sha256(source['clause'].encode()).hexdigest(),
                        'revision': source['revision']})
    return {'checked_at': datetime.now(timezone.utc).isoformat(),
            'register_kind': review['register_kind'], 'source_checks': sources,
            'writes_performed': False}

if __name__ == '__main__':
    try:
        print(json.dumps(check(), indent=2))
    except Exception as error:
        print(str(error), file=sys.stderr)
        raise SystemExit(1)
