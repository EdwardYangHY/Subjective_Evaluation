# XDailyDialog placeholder conversations

Ten complete English–Chinese conversations from the XDailyDialog test split. Dataset authors: Zeming Liu, Ping Nie, Jie Cai, Haifeng Wang, Zheng-Yu Niu, Peng Zhang, Mrinmaya Sachan, Kaiping Peng. English originates in DailyDialog (Yanran Li, Hui Su, Xiaoyu Shen, Wenjie Li, Ziqiang Cao, Shuzi Niu).

Source: https://github.com/liuzeming01/XDailyDialog . Files: `data/en_test_human.txt` and `data/zh_test_human.txt`, retrieved 2026-11-09. Line numbers, original turn text and file checksums are recorded in `placeholder_provenance.json`.

Data license: Creative Commons Attribution-NonCommercial-ShareAlike 4.0, https://creativecommons.org/licenses/by-nc-sa/4.0/ . The redistributed dialogue subset and its formatting adaptation remain under that license. The repository also lists Apache-2.0 for code; this does not replace the data license. See https://github.com/liuzeming01/XDailyDialog#8-license . Retain attribution and license information when sharing.

Selection: seed 2027, ten distinct test dialogues with 4–12 matching English/Chinese turns, sampled without replacement. Every selected dialogue is included in full. One item is one complete conversation, evaluated as a whole. All items use English as source and Chinese as translation. The published Chinese text is used as-is, not newly generated GPT output and not presumed perfect.

Formatting changes only: split the original __eou__ turn markers, trim surrounding whitespace, and add neutral [Turn N] labels and paragraph spacing. No sentences are rewritten or translated; speaker identities are not inferred. Metadata labels are not included in the rated text.

This is a UI placeholder set, not the proposed blinded human-versus-GPT comparison or actual study results. No GPT translations or user-provided conversations have been mixed in yet. No quality scores are provided.

Reproduce: `python3 scripts/prepare_xdaily_placeholders.py /path/to/en_test_human.txt /path/to/zh_test_human.txt`.
