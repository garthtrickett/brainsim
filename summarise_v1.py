"""Render descriptive paired contrasts from checkpointed v1 evidence."""
import json
from pathlib import Path
from study_io import paired_summary


def summary():
    lines = ['# V1 paired contrasts', '',
             'Exploratory seed-paired bootstrap intervals; no multiple-comparison adjustment.',
             'A positive delta is higher external task reward. These are screening results,',
             'not automatic decisions to enable a feature.', '',
             '| Study/task | Treatment vs control | Control | Treatment | Delta | 95% interval | Wins |',
             '| --- | --- | ---: | ---: | ---: | --- | --- |']
    for study in ['pools', 'curiosity', 'replay', 'dyna', 'failure', 'failure-capacity']:
        path = Path(f'results/v1-{study}.json')
        if not path.exists(): continue
        data = json.loads(path.read_text())
        groups = {}
        for key, row in data['rows'].items():
            task, arm, seed = key.split('/')
            if arm == 'controls': continue
            groups.setdefault(task, {}).setdefault(arm, {})[int(seed)] = row['score']
        for task, arms in groups.items():
            base = 'P1' if study == 'pools' else 'off'
            comparisons = [(base, arm) for arm in arms if arm != base]
            if study == 'replay': comparisons.append(('shuffled', 'context'))
            if study == 'dyna': comparisons.append(('real', 'model'))
            if study.startswith('failure'): comparisons.extend([('gain-0.9', 'fail-0.1'), ('gain-0.5', 'fail-0.5')])
            for control, treatment in comparisons:
                if control not in arms or treatment not in arms: continue
                seeds = sorted(arms[control].keys() & arms[treatment].keys())
                if not seeds: continue
                stats = paired_summary([arms[control][s] for s in seeds],
                                       [arms[treatment][s] for s in seeds])
                lo, hi = stats['interval95']
                lines.append(f"| {study}/{task} | {treatment} vs {control} | {stats['control']:.4f} | "
                             f"{stats['treatment']:.4f} | {stats['delta']:+.4f} | [{lo:+.4f}, {hi:+.4f}] | "
                             f"{stats['wins']}/{stats['n']} |")
    return '\n'.join(lines)+'\n'


if __name__ == '__main__':
    Path('results/v1-contrasts.md').write_text(summary())
