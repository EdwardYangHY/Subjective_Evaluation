"""Validate an untouched UTF-8 annotation input CSV; Python standard library only."""
import argparse
import csv
from collections import Counter
from pathlib import Path


def read_csv(path, required):
    with open(path, encoding='utf-8-sig', newline='') as f:
        reader = csv.DictReader(f, strict=True)
        headers = reader.fieldnames or []
        if len(headers) != len(set(headers)):
            raise ValueError(f'{path}: duplicate headers')
        if not set(required) <= set(headers):
            raise ValueError(f'{path}: missing columns {sorted(set(required)-set(headers))}')
        rows = list(reader)
    if not rows:
        raise ValueError(f'{path}: no data rows')
    seen = set()
    for i, row in enumerate(rows, 2):
        if None in row or any(v is None for v in row.values()):
            raise ValueError(f'{path}: record {i} has incorrect field count')
        for col in required:
            if not row[col].strip():
                raise ValueError(f'{path}: record {i} has empty {col}')
        if row['id'] in seen:
            raise ValueError(f'{path}: duplicate id {row["id"]!r}')
        seen.add(row['id'])
        if row['direction'] not in ('en-zh', 'zh-en'):
            raise ValueError(f'{path}: invalid direction for {row["id"]!r}')
    return rows


def validate(path):
    return read_csv(path, ['id', 'direction', 'source', 'reference'])


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('csv', type=Path)
    args = parser.parse_args()
    try:
        rows = validate(args.csv)
        print(f'Valid: {len(rows)} items; directions: {dict(Counter(r["direction"] for r in rows))}')
        print('Target 100 items, ideally 50 per direction (informational only). Text was not changed.')
    except (ValueError, OSError, UnicodeError, csv.Error) as exc:
        parser.exit(2, f'Validation error: {exc}\n')
