"""Check the frozen per-seed table without overwriting it or rerunning baselines."""
import json
import argparse
import numpy as np
import reference
from study_io import Evidence


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--out', default='results/v1-reference.json')
    args = parser.parse_args()
    expected = json.load(open('reference.json'))
    reference.use_fast()
    evidence = Evidence(args.out,
                        ['brainsim.py', 'fastsim.py', 'tasks.py', 'reference.py', 'reference.json'],
                        {'seeds': expected['seeds'], 'comparison': 'exact per-seed score'})
    for name, mk, nact, decisions, tail, runner in reference.SUITE:
        for seed in range(expected['seeds']):
            def measure():
                score = reference.brainsim_run(mk, nact, decisions, tail, seed, runner)
                target = expected['suite'][name]['brainsim'][seed]
                assert score == target, (name, seed, score, target)
                return {'score': score, 'expected': target, 'exact': True}
            evidence.measure(f'{name}/{seed}', measure)
    print('PASS: all 56 frozen per-seed scores reproduced exactly', flush=True)


if __name__ == '__main__': main()
