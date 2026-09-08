"""Check archived study completeness and every source snapshot digest."""
import hashlib
import json
import math
from pathlib import Path


EXPECTED = {
    'v1-pools.json': 150,
    'v1-representation.json': 8,
    'v1-model.json': 8,
    'v1-curiosity.json': 24,
    'v1-replay.json': 24,
    'v1-dyna.json': 24,
    'v1-failure.json': 144,
    'v1-failure-capacity.json': 36,
    'v1-reference.json': 56,
    'v1-reference-final.json': 56,
}


def finite(value):
    if isinstance(value, float): assert math.isfinite(value)
    elif isinstance(value, dict):
        for child in value.values(): finite(child)
    elif isinstance(value, list):
        for child in value: finite(child)


def main():
    for name, count in EXPECTED.items():
        path = Path('results')/name
        data = json.loads(path.read_text())
        assert len(data['rows']) == count, (name, len(data['rows']), count)
        finite(data)
        for source, digest in data['sources'].items():
            snapshot = path.parent/'source-snapshots'/(digest+'.txt')
            assert hashlib.sha256(snapshot.read_bytes()).hexdigest() == digest, (name, source)
        print('PASS evidence', name, count, 'rows; source hashes verified', flush=True)
    print('PASS all archived evidence complete', flush=True)


if __name__ == '__main__': main()
