# Public placeholder data — not study results

100 unique English–Mandarin sentence pairs from the Tatoeba Project, distributed by ManyThings (Charles Kelly). Source: https://www.manythings.org/anki/ and https://www.manythings.org/anki/cmn-eng.zip . Downloaded 2026-11-09; archive dated 2026-02-13.

Sentence texts are unmodified. Authors and original sentence IDs are retained in the `attribution` CSV column and `placeholder_provenance.json`. Sentence-level notices specify CC-BY 2.0 (France): https://creativecommons.org/licenses/by/2.0/fr/ . The archive also links to https://creativecommons.org/licenses/by/2.0/ . Preserve these credits when redistributing this sample.

These are community bilingual examples, not GPT-generated study references, system translations, scored quality labels, or guaranteed-error-free gold data. Chinese includes the scripts present in the original corpus; no script conversion is performed. Original authorship direction is unknown. Fifty pairs are displayed English→Chinese and fifty Chinese→English solely to exercise the interface; each underlying pair appears once. There are no supplied conversation IDs or adjacent turns, so those fields are blank. No conversations or context have been invented.

Sampling is stratified by English length (34 short, 34 medium, 32 long), seed 2027. The source warning explicitly states that errors may remain. This is a convenience sample for UI testing, not a representative research sample. No ratings are included.

Reproduce with `python3 scripts/prepare_placeholders.py /path/to/cmn-eng.zip`; check the input archive SHA-256 against `placeholder_provenance.json` because the upstream download may change.

## Original distribution notice

** Info **

Check for newest version here:
  http://www.manythings.org/anki/
Date of this file:
  2026-02-13

This data is from the sentences_detailed.csv file from tatoeba.org.
http://tatoeba.org/files/downloads/sentences_detailed.csv



** Terms of Use **

See the terms of use.
These files have been released under the same license as the
source.

http://tatoeba.org/eng/terms_of_use
http://creativecommons.org/licenses/by/2.0

Attribution: www.manythings.org/anki and tatoeba.org



** Warnings ** 

The data from the Tatoeba Project contains errors.

To lower the number of errors you are likely to see, only
sentences by native speakers and proofread sentences have
been included.

For the non-English language, I made these (possibly wrong)
assumptions.
Assumption 1: Sentences written by native speakers can be
trusted.
Assumption 2: Contributors to the Tatoeba Project are honest
about what their native language is.

For English, I used the sentences that I have proofread
and thought were OK.
Of course, I may have missed a few errors.



** Downloading Anki ** 

See http://ankisrs.net/



** Importing into Anki ** 

Information is at http://ankisrs.net/docs/manual.html#importing

Of particular interest may be about "duplicates" at http://ankisrs.net/docs/manual.html#duplicates-and-updating.
You can choose:
1. not to allow duplicates (alternate translations) as cards.
2. allow duplicates (alternate translations) as cards.
