"""只核对视频使用的条文对照库。"""
import csv
import hashlib
import json
from pathlib import Path

def audit():
    root=Path(__file__).resolve().parents[1]
    manifest=json.loads((root/'data/corpus_manifest.json').read_text())
    path=root/manifest['path']
    with path.open(encoding='utf-8-sig',newline='') as stream:
        rows=list(csv.DictReader(stream))
    numbers=[int(row['条文数']) for row in rows]
    ok=(hashlib.sha256(path.read_bytes()).hexdigest()==manifest['sha256']
        and len(rows)==manifest['rows']
        and len(set(numbers))==len(rows)
        and set(numbers)==set(range(manifest['first_number'],manifest['last_number']+1))
        and all(row['吉凶断词'].strip() for row in rows))
    return {'ok':ok,'rows':len(rows),'corpus_role':'comparison_only'}

if __name__=='__main__':
    result=audit();print(json.dumps(result,ensure_ascii=False))
    raise SystemExit(0 if result['ok'] else 1)
