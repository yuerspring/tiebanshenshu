"""Offline CSV integrity checks; this is not a claim of textual authenticity."""
import argparse
import csv
import hashlib
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / 'data' / 'csv_manifest.json'


def inventory(root):
    result = {}
    for folder in ('DB', 'reference_os/DB'):
        for path in sorted((root / folder).glob('*.csv')):
            result[path.relative_to(root).as_posix()] = {
                'sha256': hashlib.sha256(path.read_bytes()).hexdigest(),
                'bytes': path.stat().st_size,
            }
    return result


def check_corpus(path):
    errors = []
    with path.open(encoding='utf-8-sig', newline='') as handle:
        reader = csv.DictReader(handle)
        required = {'集', '条文数', '年龄', '吉凶断词'}
        if not required.issubset(reader.fieldnames or []):
            return ['List.csv: required columns are missing'], {}
        rows = list(reader)
    numbers = []
    for line, row in enumerate(rows, 2):
        try:
            numbers.append(int(row['条文数']))
        except (ValueError, TypeError):
            errors.append(f'List.csv:{line}: invalid verse number')
        if not (row.get('吉凶断词') or '').strip():
            errors.append(f'List.csv:{line}: empty verse text')
    counts = Counter(numbers)
    duplicates = sorted(n for n, count in counts.items() if count > 1)
    missing = sorted(set(range(1001, 13001)) - set(numbers))
    unexpected = sorted(set(numbers) - set(range(1001, 13001)))
    if duplicates:
        errors.append(f'List.csv: duplicate verse numbers {duplicates[:20]}')
    if missing:
        errors.append(f'List.csv: {len(missing)} missing verse numbers')
    if unexpected:
        errors.append(f'List.csv: out-of-range verse numbers {unexpected[:20]}')
    return errors, {'rows': len(rows), 'unique_numbers': len(counts),
                    'missing_count': len(missing), 'duplicate_count': len(duplicates)}


def audit(root=ROOT, manifest=MANIFEST):
    expected = json.loads(manifest.read_text(encoding='utf-8'))
    current = inventory(root)
    errors = []
    for name in sorted(set(expected['files']) | set(current)):
        if expected['files'].get(name) != current.get(name):
            errors.append(f'{name}: CSV snapshot differs; review the source before updating the manifest')
    corpus_errors, corpus = check_corpus(root / 'DB' / 'List.csv')
    errors.extend(corpus_errors)
    return {'ok': not errors, 'errors': errors, 'corpus': corpus,
            'file_count': len(current),
            'textual_authenticity': 'not_verified_against_a_fixed_printed_edition'}


def compare_reference(root, reference):
    """Compare a separately downloaded corpus without copying it into this repo."""
    differences = []
    def read(path):
        return list(csv.DictReader(path.open(encoding='utf-8-sig', newline='')))
    own = read(root / 'DB' / 'List.csv')
    other = read(reference / 'verses' / 'tiaowen.csv')
    if own != other:
        differences.append('verse rows differ')
    for path in sorted((root / 'DB').glob('14-*.csv')):
        candidate = reference / 'tables' / path.name
        if not candidate.exists():
            differences.append(f'{path.name}: reference missing')
        elif path.read_text(encoding='utf-8-sig').strip() != candidate.read_text(encoding='utf-8-sig').strip():
            differences.append(f'{path.name}: table differs')
    return {'verse_rows_equal': own == other, 'differences': differences,
            'independent_book_verification': False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--reference-dir', type=Path, help='Optional tbss-ts-lib docs/corpus path')
    args = parser.parse_args()
    result = audit()
    if args.reference_dir:
        result['reference_comparison'] = compare_reference(ROOT, args.reference_dir)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result['ok'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
