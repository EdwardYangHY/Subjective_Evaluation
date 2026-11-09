"""Paired two-annotator analysis. Synthetic inputs are not research findings."""
import argparse
import csv
import json
import warnings
from pathlib import Path
import numpy as np
import pandas as pd
from sklearn.metrics import cohen_kappa_score
from validate_items import read_csv, validate


def load(path):
    rows = read_csv(path, ['annotator_id', 'id', 'direction', 'adequacy', 'major_error', 'naturalness'])
    if len({r['annotator_id'] for r in rows}) != 1:
        raise ValueError(f'{path}: expected one annotator ID')
    for r in rows:
        if r['adequacy'] not in ('1', '2', '3', '4', '5'):
            raise ValueError(f'{path}: {r["id"]}: adequacy must be an integer 1–5')
        if r['naturalness'] not in ('1', '2', '3', '4', '5'):
            raise ValueError(f'{path}: {r["id"]}: naturalness must be an integer 1–5; legacy exports require additional annotation')
        if r['major_error'] not in ('Yes', 'No'):
            raise ValueError(f'{path}: {r["id"]}: major_error must be Yes or No')
        r.setdefault('comment', '')
        r.setdefault('conversation_id', '')
    return pd.DataFrame(rows).set_index('id')


def kappa(a, b, labels, weights=None):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        value = cohen_kappa_score(a, b, labels=labels, weights=weights)
    return float(value) if np.isfinite(value) else None


def summarize(frame, reps, seed, clustered):
    a = frame.adequacy_A.to_numpy(dtype=int)
    b = frame.adequacy_B.to_numpy(dtype=int)
    ma = (frame.major_error_A == 'Yes').to_numpy(dtype=float)
    mb = (frame.major_error_B == 'Yes').to_numpy(dtype=float)
    na = frame.naturalness_A.to_numpy(dtype=int)
    nb = frame.naturalness_B.to_numpy(dtype=int)
    naturalness = (na+nb)/2
    quality = (a+b)/2
    error = (ma+mb)/2
    labels = frame.conversation_id.to_numpy() if clustered else frame.index.to_numpy()
    units = list(dict.fromkeys(labels))
    groups = [np.flatnonzero(labels == unit) for unit in units]
    totals = np.array([[quality[g].sum(), error[g].sum(), naturalness[g].sum(), len(g)] for g in groups])
    rng = np.random.default_rng(seed)
    samples = np.empty((reps, 3))
    for i in range(reps):
        total = totals[rng.integers(0, len(groups), size=len(groups))].sum(axis=0)
        samples[i] = total[:3]/total[3]
    notes = []
    if len(groups) < 2:
        notes.append('Fewer than two resampling units: confidence intervals are not estimable.')
    if max(np.bincount(np.concatenate([a, b]), minlength=6)[1:])/(2*len(a)) >= .9:
        notes.append('Near-uniform adequacy ratings: kappa may be unstable or low despite high raw agreement; kappa is not a quality score.')
    qw = kappa(a, b, [1, 2, 3, 4, 5], 'quadratic')
    if qw is None:
        notes.append('Quadratic-weighted kappa is undefined because expected disagreement is zero.')
    nq = kappa(na, nb, [1, 2, 3, 4, 5], 'quadratic')
    if max(np.bincount(np.concatenate([na, nb]), minlength=6)[1:])/(2*len(na)) >= .9:
        notes.append('Near-uniform naturalness ratings: kappa may be unstable; report raw agreement alongside it.')
    if nq is None:
        notes.append('Naturalness quadratic-weighted kappa is undefined because expected disagreement is zero.')
    ci = np.quantile(samples, [.025, .975], axis=0).T.tolist() if len(groups) >= 2 else [None, None, None]
    return dict(items=len(a), annotations=2*len(a), resampling_units=len(groups),
                naturalness_mean=float(naturalness.mean()), naturalness_ci95=ci[2],
                annotator_A_naturalness_mean=float(na.mean()), annotator_B_naturalness_mean=float(nb.mean()),
                naturalness_quadratic_weighted_kappa=nq,
                naturalness_exact_agreement=float((na==nb).mean()),
                naturalness_within_one_point_agreement=float((abs(na-nb)<=1).mean()),
                adequacy_mean=float(quality.mean()), adequacy_ci95=ci[0],
                major_error_rate=float(error.mean()), major_error_ci95=ci[1],
                annotator_A_adequacy_mean=float(a.mean()), annotator_B_adequacy_mean=float(b.mean()),
                annotator_A_major_error_rate=float(ma.mean()), annotator_B_major_error_rate=float(mb.mean()),
                quadratic_weighted_kappa=qw, exact_agreement=float((a==b).mean()),
                within_one_point_agreement=float((abs(a-b)<=1).mean()),
                major_error_kappa=kappa(ma, mb, [0, 1]), warnings=notes)


def analyze(args):
    a, b = load(args.a), load(args.b)
    if a.annotator_id.iloc[0] == b.annotator_id.iloc[0]:
        raise ValueError('Two different annotator IDs are required')
    if set(a.index) != set(b.index):
        raise ValueError(f'Item sets differ: A-only {sorted(set(a.index)-set(b.index))[:10]}, B-only {sorted(set(b.index)-set(a.index))[:10]}')
    b = b.loc[a.index]
    if not a.direction.equals(b.direction):
        raise ValueError('Directions differ between annotators')
    fingerprints = []
    for name, df in [('A', a), ('B', b)]:
        if 'dataset_fingerprint' in df:
            values = set(df.dataset_fingerprint)
            if len(values) != 1 or not next(iter(values)):
                raise ValueError(f'{name}: inconsistent or empty dataset fingerprints')
            fingerprints.append(next(iter(values)))
    if len(set(fingerprints)) > 1:
        raise ValueError('Dataset fingerprints differ')
    original = pd.DataFrame(validate(args.items)).set_index('id') if args.items else None
    if original is not None:
        if set(original.index) != set(a.index):
            raise ValueError('Original items do not match annotation item set')
        original = original.loc[a.index]
        if not original.direction.equals(a.direction):
            raise ValueError('Original directions do not match annotations')
    conversations = []
    for item_id in a.index:
        values = [a.loc[item_id, 'conversation_id'], b.loc[item_id, 'conversation_id']]
        if original is not None and 'conversation_id' in original:
            values.append(original.loc[item_id, 'conversation_id'])
        nonempty = {v for v in values if v.strip()}
        if len(nonempty) > 1:
            raise ValueError(f'Conflicting conversation IDs for {item_id}')
        conversations.append(next(iter(nonempty), ''))
    if any(conversations) and not all(conversations):
        raise ValueError('Partial conversation IDs: supply complete metadata for cluster bootstrap, or consistently omit conversation IDs')
    f = a.join(b, lsuffix='_A', rsuffix='_B')
    f['conversation_id'] = conversations
    clustered = all(conversations)
    groups = {'overall': summarize(f, args.replicates, args.seed, clustered)}
    for direction in ('en-zh', 'zh-en'):
        part = f[f.direction_A == direction]
        groups[direction] = summarize(part, args.replicates, args.seed, clustered) if len(part) else {'items': 0, 'annotations': 0, 'warnings': ['No items in this direction; metrics are not estimable.']}
    result = {'annotators': {'A': a.annotator_id.iloc[0], 'B': b.annotator_id.iloc[0]},
              'dataset_fingerprint': fingerprints[0] if fingerprints else None,
              'methods': {'metric_roles': {'adequacy': 'primary', 'major_error': 'primary', 'naturalness': 'secondary'},
                          'naturalness': 'Mean paired item score; secondary measure of target-language expression, not evidence against reference stylistic bias.',
                          'headline_adequacy': 'Mean of all individual scores (equivalently mean paired item score).',
                          'headline_major_error': 'Per-annotation Yes fraction, averaged within item then across items; not consensus or adjudicated.',
                          'ci': '95% percentile bootstrap; paired judgments always kept together; sampled clusters retain all their items; metrics are item-weighted.',
                          'resampling_unit': 'conversation' if clustered else 'item',
                          'replicates': args.replicates, 'seed': args.seed,
                          'groups': 'Overall and subsets defined by input translation direction; conversations resampled within each subset.',
                          'agreement': 'Paired quadratic-weighted Cohen kappa with fixed labels 1–5; binary unweighted kappa with labels 0,1. Undefined values are null.',
                          'limitations': 'Sampled reference accuracy only; agreement is not accuracy. High adequacy and naturalness do not rule out reference wording preferences or their effect on BLEU. Report low naturalness agreement transparently. Reference-free GEMBA-MQM is a separate complementary system evaluation. Limited sample precision remains. No system outputs assessed.'},
              'groups': groups}
    mask = (f.major_error_A != f.major_error_B) | ((f.adequacy_A.astype(int)-f.adequacy_B.astype(int)).abs() >= 2)
    mask = mask | ((f.naturalness_A.astype(int)-f.naturalness_B.astype(int)).abs() >= 2)
    report = f.loc[mask, ['direction_A', 'conversation_id', 'annotator_id_A', 'adequacy_A', 'major_error_A', 'naturalness_A', 'comment_A', 'annotator_id_B', 'adequacy_B', 'major_error_B', 'naturalness_B', 'comment_B']].rename(columns={'direction_A': 'direction'})
    args.out.mkdir(parents=True, exist_ok=True)
    report.to_csv(args.out/'disagreements.csv', encoding='utf-8-sig')
    (args.out/'results_summary.json').write_text(json.dumps(result, indent=2, ensure_ascii=False, allow_nan=False)+'\n', encoding='utf-8')
    print(pd.DataFrame(groups).T[['items', 'annotations', 'adequacy_mean', 'adequacy_ci95', 'major_error_rate', 'major_error_ci95', 'quadratic_weighted_kappa', 'exact_agreement', 'within_one_point_agreement', 'naturalness_mean', 'naturalness_ci95', 'naturalness_quadratic_weighted_kappa', 'naturalness_exact_agreement', 'naturalness_within_one_point_agreement', 'major_error_kappa']].to_string())
    print(f'\nCI unit: {result["methods"]["resampling_unit"]}; replicates: {args.replicates}; seed: {args.seed}. Major-error headline: per annotation, paired uncertainty.')
    for name, group in groups.items():
        for note in group['warnings']:
            print(f'WARNING [{name}]: {note}')
    print(f'Disagreements: {len(report)}. Outputs: {args.out}')
    return result


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('a', type=Path)
    p.add_argument('b', type=Path)
    p.add_argument('--items', type=Path)
    p.add_argument('--out', type=Path, default=Path('analysis_output'))
    p.add_argument('--replicates', type=int, default=5000)
    p.add_argument('--seed', type=int, default=2027)
    args = p.parse_args()
    if args.replicates < 100:
        p.error('--replicates must be at least 100')
    try:
        analyze(args)
    except (ValueError, OSError, UnicodeError, csv.Error) as exc:
        p.exit(2, f'Analysis error: {exc}\n')
