"""Select ten complete English-Chinese test conversations; no translation generation."""
import csv, hashlib, io, json, random, sys
from pathlib import Path
root=Path(__file__).resolve().parents[1]
en_path,zh_path=map(Path,sys.argv[1:3])
en=en_path.read_text(encoding='utf-8').splitlines();zh=zh_path.read_text(encoding='utf-8').splitlines()
assert len(en)==len(zh)
eligible=[]
for i,(a,b) in enumerate(zip(en,zh),1):
 ea,za=a.split('\t'),b.split('\t')
 et=[s.strip() for s in ea[0].split('__eou__') if s.strip()]
 zt=[s.strip() for s in za[0].split('__eou__') if s.strip()]
 if len(et)==len(zt) and 4<=len(et)<=12:
  eligible.append((i,et,zt,ea,za))
selected=random.Random(2027).sample(eligible,10)
rows=[];provenance=[]
credit='XDailyDialog — Zeming Liu et al.; English from DailyDialog. Dataset: CC BY-NC-SA 4.0. https://github.com/liuzeming01/XDailyDialog'
for n,(line,et,zt,ea,za) in enumerate(selected,1):
 cid=f'xdailydialog_test_{line:04d}'
 rows.append(dict(id=f'DEMO_XDAILY_{line:04d}',direction='en-zh',source='\n\n'.join(f'[Turn {i}] {t}' for i,t in enumerate(et,1)),reference='\n\n'.join(f'[Turn {i}] {t}' for i,t in enumerate(zt,1)),conversation_id=cid,context='',attribution=credit))
 provenance.append(dict(id=rows[-1]['id'],conversation_id=cid,split='test',line_1based=line,turn_count=len(et),english_turns=et,chinese_turns=zt,metadata=ea[1:]))
stream=io.StringIO(newline='');w=csv.DictWriter(stream,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
text=stream.getvalue()
(root/'placeholder_items.csv').write_bytes(b'\xef\xbb\xbf'+text.encode('utf-8'))
(root/'placeholder_data.js').write_text('/* XDailyDialog demo conversations; see DATA_ATTRIBUTION.md. */\nwindow.PLACEHOLDER_CSV = '+json.dumps(text,ensure_ascii=False)+';\n',encoding='utf-8')
(root/'placeholder_provenance.json').write_text(json.dumps(dict(dataset='XDailyDialog',repository='https://github.com/liuzeming01/XDailyDialog',source_files={lang:dict(url=f'https://raw.githubusercontent.com/liuzeming01/XDailyDialog/main/data/{lang}_test_human.txt',sha256=hashlib.sha256(p.read_bytes()).hexdigest()) for lang,p in [('en',en_path),('zh',zh_path)]},seed=2027,sampling='Ten distinct test conversations sampled without replacement from conversations with 4–12 matched turns. All English→Chinese, following dataset provenance. Full dialogues retained, no turn truncation.',formatting='Split at __eou__; trim surrounding whitespace; prefix each unchanged turn with [Turn N]. No invented speaker identities.',items=provenance),indent=2,ensure_ascii=False)+'\n',encoding='utf-8')
(root/'DATA_ATTRIBUTION.md').write_text('''# XDailyDialog placeholder conversations

Ten complete English–Chinese conversations from the XDailyDialog test split. Dataset authors: Zeming Liu, Ping Nie, Jie Cai, Haifeng Wang, Zheng-Yu Niu, Peng Zhang, Mrinmaya Sachan, Kaiping Peng. English originates in DailyDialog (Yanran Li, Hui Su, Xiaoyu Shen, Wenjie Li, Ziqiang Cao, Shuzi Niu).

Source: https://github.com/liuzeming01/XDailyDialog . Files: `data/en_test_human.txt` and `data/zh_test_human.txt`, retrieved 2026-11-09. Line numbers, original turn text and file checksums are recorded in `placeholder_provenance.json`.

Data license: Creative Commons Attribution-NonCommercial-ShareAlike 4.0, https://creativecommons.org/licenses/by-nc-sa/4.0/ . The redistributed dialogue subset and its formatting adaptation remain under that license. The repository also lists Apache-2.0 for code; this does not replace the data license. See https://github.com/liuzeming01/XDailyDialog#8-license . Retain attribution and license information when sharing.

Selection: seed 2027, ten distinct test dialogues with 4–12 matching English/Chinese turns, sampled without replacement. Every selected dialogue is included in full. One item is one complete conversation, evaluated as a whole. All items use English as source and Chinese as translation. The published Chinese text is used as-is, not newly generated GPT output and not presumed perfect.

Formatting changes only: split the original __eou__ turn markers, trim surrounding whitespace, and add neutral [Turn N] labels and paragraph spacing. No sentences are rewritten or translated; speaker identities are not inferred. Metadata labels are not included in the rated text.

This is a UI placeholder set, not the proposed blinded human-versus-GPT comparison or actual study results. No GPT translations or user-provided conversations have been mixed in yet. No quality scores are provided.

Reproduce: `python3 scripts/prepare_xdaily_placeholders.py /path/to/en_test_human.txt /path/to/zh_test_human.txt`.
''',encoding='utf-8')
print('Selected dialogues:',[(p['line_1based'],p['turn_count']) for p in provenance]);print('Total turns:',sum(p['turn_count'] for p in provenance))
