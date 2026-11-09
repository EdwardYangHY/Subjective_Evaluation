"""Reproduce the 100 demo pairs from a locally downloaded ManyThings cmn-eng.zip."""
import csv, hashlib, io, json, random, re, sys, zipfile
from pathlib import Path
root=Path(__file__).resolve().parents[1]
archive=Path(sys.argv[1])
with zipfile.ZipFile(archive) as z:
    raw=z.read('cmn.txt').decode('utf-8')
    about=z.read('_about.txt').decode('utf-8')
pools=[[],[],[]]; seen_en=set(); seen_zh=set()
for line in raw.splitlines():
    en,zh,credit=line.split('\t')
    n=len(en.split())
    if not 4<=n<=30 or not re.search('[\u4e00-\u9fff]',zh): continue
    if en in seen_en or zh in seen_zh: continue
    seen_en.add(en);seen_zh.add(zh)
    pools[0 if n<=7 else 1 if n<=12 else 2].append((en,zh,credit))
rng=random.Random(2027)
chosen=[]
for pool,count in zip(pools,[34,34,32]): chosen.extend(rng.sample(pool,count))
rng.shuffle(chosen)
rows=[]; provenance=[]
for i,(en,zh,credit) in enumerate(chosen):
    enid,zhid=re.findall(r'#(\d+)',credit)
    direction='en-zh' if i%2==0 else 'zh-en'
    item_id=f'DEMO_TATOEBA_{enid}_{zhid}'
    rows.append(dict(id=item_id,direction=direction,source=en if direction=='en-zh' else zh,reference=zh if direction=='en-zh' else en,conversation_id='',context='',attribution=credit))
    provenance.append(dict(id=item_id,english_url=f'https://tatoeba.org/en/sentences/show/{enid}',chinese_url=f'https://tatoeba.org/en/sentences/show/{zhid}',attribution=credit))
s=io.StringIO(newline='');w=csv.DictWriter(s,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
csv_text=s.getvalue()
(root/'placeholder_items.csv').write_text(csv_text,encoding='utf-8-sig')
(root/'placeholder_data.js').write_text('/* Public Tatoeba demo data; attribution is retained in each CSV row. */\nwindow.PLACEHOLDER_CSV = '+json.dumps(csv_text,ensure_ascii=False)+';\n',encoding='utf-8')
(root/'placeholder_provenance.json').write_text(json.dumps(dict(dataset='Tatoeba via ManyThings Mandarin-English',download='https://www.manythings.org/anki/cmn-eng.zip',archive_sha256=hashlib.sha256(archive.read_bytes()).hexdigest(),seed=2027,sampling='Unique English and Chinese strings; English word counts 4–7:34, 8–12:34, 13–30:32; deterministic random sample. Alternating presentation direction, not original authorship language.',items=provenance),ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
(root/'DATA_ATTRIBUTION.md').write_text('''# Public placeholder data — not study results

100 unique English–Mandarin sentence pairs from the Tatoeba Project, distributed by ManyThings (Charles Kelly). Source: https://www.manythings.org/anki/ and https://www.manythings.org/anki/cmn-eng.zip . Downloaded 2026-11-09; archive dated 2026-02-13.

Sentence texts are unmodified. Authors and original sentence IDs are retained in the `attribution` CSV column and `placeholder_provenance.json`. Sentence-level notices specify CC-BY 2.0 (France): https://creativecommons.org/licenses/by/2.0/fr/ . The archive also links to https://creativecommons.org/licenses/by/2.0/ . Preserve these credits when redistributing this sample.

These are community bilingual examples, not GPT-generated study references, system translations, scored quality labels, or guaranteed-error-free gold data. Chinese includes the scripts present in the original corpus; no script conversion is performed. Original authorship direction is unknown. Fifty pairs are displayed English→Chinese and fifty Chinese→English solely to exercise the interface; each underlying pair appears once. There are no supplied conversation IDs or adjacent turns, so those fields are blank. No conversations or context have been invented.

Sampling is stratified by English length (34 short, 34 medium, 32 long), seed 2027. The source warning explicitly states that errors may remain. This is a convenience sample for UI testing, not a representative research sample. No ratings are included.

Reproduce with `python3 scripts/prepare_placeholders.py /path/to/cmn-eng.zip`; check the input archive SHA-256 against `placeholder_provenance.json` because the upstream download may change.

## Original distribution notice

'''+about,encoding='utf-8')
print('Prepared',len(rows),'unique pairs; 50 each presentation direction.')
