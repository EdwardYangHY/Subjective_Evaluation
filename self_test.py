"""Synthetic analysis assertions; no study results are generated."""
import argparse
import csv
import tempfile
from pathlib import Path
from analyze_annotations import analyze

root = Path(__file__).resolve().parent
with tempfile.TemporaryDirectory() as tmp:
    args = argparse.Namespace(a=root/'synthetic/synthetic_annotations_A.csv', b=root/'synthetic/synthetic_annotations_B.csv', items=root/'synthetic/synthetic_items.csv', out=Path(tmp)/'output', replicates=500, seed=2027)
    r = analyze(args)
    g = r['groups']['overall']
    assert g['items'] == 4 and g['adequacy_mean'] == 4.375
    assert g['major_error_rate'] == .125
    assert g['exact_agreement'] == .5 and g['within_one_point_agreement'] == .75
    assert r['methods']['resampling_unit'] == 'conversation'
    # Observed squared disagreement = 5/4; expected = 9/4; kappa = 4/9.
    assert abs(g['quadratic_weighted_kappa'] - 4/9) < 1e-12
    with (args.out/'disagreements.csv').open(encoding='utf-8-sig', newline='') as f:
        assert [x['id'] for x in csv.DictReader(f)] == ['SYNTHETIC_002']
    assert analyze(args) == r
    with args.b.open(encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f); fields=reader.fieldnames; records=list(reader)
    for problem in ['missing', 'duplicate', 'incomplete', 'direction']:
        broken = [dict(x) for x in records]
        if problem == 'missing': broken.pop()
        elif problem == 'duplicate': broken.append(broken[0])
        elif problem == 'incomplete': broken[0]['adequacy'] = ''
        else: broken[0]['direction'] = 'en-zh'
        path = Path(tmp)/f'{problem}.csv'
        with path.open('w',encoding='utf-8',newline='') as f:
            writer=csv.DictWriter(f,fieldnames=fields);writer.writeheader();writer.writerows(broken)
        args.b=path
        try: analyze(args)
        except ValueError: pass
        else: raise AssertionError(f'Accepted {problem}')
print('PASS: fabricated paired analysis, reversed rows, deterministic CI, disagreements, invalid-input rejection. Not research findings.')
