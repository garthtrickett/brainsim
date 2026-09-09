"""Registered finite tuning and independent confirmation with immutable provenance."""
import argparse
from functools import lru_cache
import hashlib
import json
from pathlib import Path

import numpy as np

from study_io import Evidence
from study_v3_burst import SOURCES as BURST_SOURCES
from study_v3_slice1 import require_committed, write
from v3_discovery import (ARMS, CUE_BASE, FAMILIES, GRIDS, cue_observations,
                          random_splits, run, shuffled_cue, true_contexts)
from v3_discovery_policy import KEYS, PROTOCOL, SEEDS, complete, digest, finite, select
from v3_persistent import FIXTURES, fixture
from v3_slice1_streams import learning_metrics

DIRECTORY = Path('results/v3-discovery')
SOURCES = sorted(set(BURST_SOURCES + ['DESIGN-v3-discovery.md', 'v3_discovery.py',
    'v3_forgetting.py', 'v3_adwin.py', 'v3_discovery_policy.py', 'study_v3_discovery.py',
    'report_v3_discovery.py', 'check_v3_discovery.py']))


def source_hashes():
    return {p: hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in SOURCES}


def registration_check():
    if source_hashes()['DESIGN-v3-discovery.md'] != PROTOCOL['registration_sha256']:
        raise ValueError('registered protocol changed')


@lru_cache(maxsize=200)
def observations(seed, name):
    data = fixture(seed, name)
    contexts = true_contexts(data)
    cues = cue_observations(seed, FIXTURES.index(name), contexts)
    data.y.flags.writeable = contexts.flags.writeable = cues.flags.writeable = False
    return data, contexts, cues


def auc_score(scores, labels):
    scores = np.asarray(scores, dtype=float)
    labels = np.asarray(labels, dtype=float)
    if scores.shape != labels.shape or scores.ndim != 1 or not len(scores):
        raise ValueError('aligned score/label vectors required')
    if not np.isfinite(scores).all() or not np.isfinite(labels).all():
        raise ValueError('finite scores/labels required')
    if set(np.unique(labels).tolist()) - {0.0, 1.0}:
        raise ValueError('binary labels required')
    pos = labels == 1.0
    n1, n0 = int(pos.sum()), int((~pos).sum())
    if not n1 or not n0:
        return None
    order = np.argsort(scores, kind='mergesort')
    ranked = labels[order]
    # Average-rank AUC with deterministic tie handling via mergesort stability.
    ranks = np.empty_like(scores)
    i = 0
    while i < len(scores):
        j = i
        while j + 1 < len(scores) and scores[order[j + 1]] == scores[order[i]]:
            j += 1
        ranks[order[i:j + 1]] = (i + j) / 2.0 + 1.0
        i = j + 1
    return float((ranks[pos].sum() - n1 * (n1 + 1) / 2.0) / (n0 * n1))


def discovery_metrics(data, contexts, result, arm, tau=None, conditioning=True):
    preds, sigmas, norms, scores, hats = result[0], result[1], result[2], result[3], result[4]
    records = {}
    for j, coordinate in enumerate(data.coordinates):
        rec = {}
        if arm in ('discover', 'oracle', 'oracle_matched', 'random', 'shuffled', 'nocontext_matched'):
            post = slice(1000, len(scores))
            rec['auc'] = auc_score(scores[post, j], contexts[post, j])
            rec['contested_rate'] = float(np.mean(sigmas[:, j] >= tau)) if tau is not None else None
            rec['conditional_use_rate'] = (float(np.mean(sigmas[:, j] >= tau))
                                           if (tau is not None and conditioning) else 0.0)
            rec['hat_mean'] = float(np.mean(hats[:, j]))
            rec['sigma_mean'] = float(np.mean(sigmas[1000:, j]))
            rec['sigma_final'] = float(sigmas[-1, j])
        else:
            rec['auc'] = None
        records[coordinate] = rec
    return records


def memory_metrics(data, result, arm):
    preds, sigmas, norms = result[0], result[1], result[2]
    records = {}
    for j, coordinate in enumerate(data.coordinates):
        if arm in ('discover', 'oracle', 'oracle_matched', 'random', 'shuffled', 'nocontext_matched'):
            records[coordinate] = {'kind': 'conditional',
                'sigma_mean': float(np.mean(sigmas[1000:, j])),
                'sigma_final': float(sigmas[-1, j]),
                'hat_mean': float(np.mean(result[4][:, j]))}
        elif arm == 'window':
            widths, removed = result[5][:, j], result[6][:, j]
            records[coordinate] = {'kind': 'window',
                'width_mean': float(np.mean(widths[1000:])), 'width_final': int(widths[-1]),
                'width_min': int(widths[1000:].min()), 'width_max': int(widths[1000:].max()),
                'total_discarded': int(removed.sum())}
        elif arm == 'sgd':
            records[coordinate] = {'kind': 'exponential'}
        else:
            widths, removed = result[5][:, j], result[6][:, j]
            records[coordinate] = {'kind': 'adaptive',
                'width_mean': float(np.mean(widths[1000:])), 'width_final': int(widths[-1]),
                'total_discarded': int(removed.sum())}
    return records


def simulation(seed, name, arm, config):
    data, contexts, cues = observations(seed, name)
    ordinal = FIXTURES.index(name)
    kwargs = {}
    if arm in ('discover', 'oracle', 'oracle_matched', 'nocontext_matched'):
        kwargs['x'] = cues
    elif arm == 'shuffled':
        kwargs['x'] = shuffled_cue(np.array(cues), seed, ordinal)
    elif arm == 'random':
        kwargs['x'] = np.array(cues)
        kwargs['splits'] = random_splits(seed, ordinal, data.y.shape)
    else:
        kwargs['x'] = np.zeros_like(data.y)
    if arm in ('oracle', 'oracle_matched'):
        kwargs['contexts'] = np.array(contexts)
    return data, contexts, cues, run(data.y, kwargs.pop('x'), arm, config, **kwargs)


def measure_row(seed, arm, config, manifest=None):
    row = {'status': 'ok', 'config': config,
           'privileged_context': arm in ('oracle', 'oracle_matched'),
           'fixtures': {}, 'memory': {}}
    if manifest is not None:
        row['manifest_digest'] = digest(manifest)
        row['discovery'] = {}
    for name in FIXTURES:
        data, contexts, cues, result = simulation(seed, name, arm, config)
        if not all(np.isfinite(x).all() for x in result[:3]):
            return {**{k: v for k, v in row.items() if k not in ('fixtures', 'memory', 'discovery')},
                    'status': 'nonfinite', 'reason': name + ' trajectory'}
        with np.errstate(over='ignore', invalid='ignore'):
            metrics = learning_metrics(data, *result[:3])
        if not finite(metrics):
            return {**{k: v for k, v in row.items() if k not in ('fixtures', 'memory', 'discovery')},
                    'status': 'nonfinite', 'reason': name + ' metrics'}
        row['fixtures'][name] = metrics
        row['memory'][name] = memory_metrics(data, result, arm)
        if manifest is not None:
            row['discovery'][name] = discovery_metrics(
                data, contexts, result, arm, config.get('tau'),
                conditioning=(arm != 'nocontext_matched'))
    if not finite(row):
        raise ValueError('non-finite explanatory record')
    return row


def read_stage(directory, stage):
    envelope = json.loads((directory / (stage + '.json')).read_text())
    if envelope['protocol'] != PROTOCOL or envelope['sources'] != source_hashes():
        raise ValueError('changed source/protocol')
    rows = envelope['rows']
    complete(rows, stage)
    manifest = json.loads((directory / 'manifest.json').read_text()) if stage == 'confirmation' else None
    for key, row in rows.items():
        parts = key.split('/')
        arm = parts[0]
        expected = GRIDS[arm][int(parts[1])] if stage == 'tuning' else manifest['screen']['selected'][arm]
        if row.get('config') != expected or row.get('privileged_context') is not (arm in ('oracle', 'oracle_matched')):
            raise ValueError('row configuration/privilege mismatch')
        if manifest is not None and row.get('manifest_digest') != digest(manifest):
            raise ValueError('row belongs to another manifest')
    return rows


def make_manifest(rows):
    result = {'protocol': PROTOCOL, 'sources': source_hashes(), 'seeds': SEEDS,
              'grids': GRIDS, 'screen': select(rows),
              'tuning_digest': digest(rows), 'expected_counts': {s: len(k) for s, k in KEYS.items()}}
    return json.loads(json.dumps(result, allow_nan=False))


def verified_manifest(directory):
    registration_check()
    for source in SOURCES:
        require_committed(Path(source))
    require_committed(directory / 'manifest.json')
    require_committed(directory / 'tuning.json')
    manifest = json.loads((directory / 'manifest.json').read_text())
    if manifest != make_manifest(read_stage(directory, 'tuning')):
        raise ValueError('manifest differs from tuning')
    if manifest['screen']['status'] != 'eligible':
        raise ValueError('tuning prerequisite failed; confirmation forbidden')
    return manifest


def tune(directory):
    registration_check()
    for source in SOURCES:
        require_committed(Path(source))
    if (directory / 'confirmation.json').exists():
        raise ValueError('cannot reopen tuning after confirmation')
    evidence = Evidence(directory / 'tuning.json', SOURCES, PROTOCOL)
    for arm in FAMILIES:
        for i, config in enumerate(GRIDS[arm]):
            for seed in SEEDS['tuning']:
                evidence.measure(f'{arm}/{i}/{seed}', lambda s=seed, a=arm, c=config: measure_row(s, a, c))
    manifest = make_manifest(read_stage(directory, 'tuning'))
    path = directory / 'manifest.json'
    if path.exists() and json.loads(path.read_text()) != manifest:
        raise ValueError('frozen manifest changed')
    write(path, manifest)
    print('TUNING', manifest['screen']['status'], 'Commit complete evidence/manifest before confirmation.', flush=True)


def confirm(directory):
    manifest = verified_manifest(directory)
    evidence = Evidence(directory / 'confirmation.json', SOURCES, PROTOCOL)
    for arm in ARMS:
        config = manifest['screen']['selected'][arm]
        for seed in SEEDS['confirmation']:
            evidence.measure(f'{arm}/{seed}', lambda s=seed, a=arm, c=config: measure_row(s, a, c, manifest))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=('tune', 'confirm', 'report'))
    parser.add_argument('--directory', type=Path, default=DIRECTORY)
    args = parser.parse_args()
    if args.stage == 'report':
        from report_v3_discovery import publish_report
        publish_report(args.directory)
    else:
        {'tune': tune, 'confirm': confirm}[args.stage](args.directory)


if __name__ == '__main__':
    main()
