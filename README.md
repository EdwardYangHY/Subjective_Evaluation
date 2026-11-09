# Offline translation reference validation

This project implements a two-independent-annotator validation of source transcripts against translation references. No system outputs are loaded or evaluated. The annotation interface uses neutral labels; do not disclose reference provenance to annotators while rating. Researcher-facing filenames and this README should not be shown during blinded rating.

## Launch (no installation or internet needed for annotation)

1. Open `index.html` in a current desktop browser, preferably Chrome or Firefox.
2. If your browser restricts local-file storage or hashing, use a local server:

```sh
cd /Users/edwardyang/code/pseudo_gt_validation
python3 -m http.server 8000 --bind 127.0.0.1
```

Open `http://127.0.0.1:8000`. Use the same browser, URL/port, and device to resume. The server only serves static files; CSV content is read in-browser and never uploaded. There are no external libraries, APIs, analytics, fonts, or network calls from the page. A content security policy prohibits connections.

## Prepare data

Copy `annotation_items_template.csv` and populate it with actual study items. Required columns: `id,direction,source,reference`; optional: `conversation_id,context`. IDs must be unique, direction must be `en-zh` or `zh-en`, and required fields must be nonempty. UTF-8 (with or without BOM) is required. Quote fields containing commas, quotes (double embedded quotes), or newlines. Original text is preserved; no extraction or translation takes place. Unknown columns are ignored by the interface and never displayed; distribute only the six specified columns to avoid disclosing unnecessary metadata.

Target 100 pairs, preferably 50 per direction, sampled across distinct conversations and varied utterance lengths. The app accepts other counts. Record your actual sampling procedure separately. Both annotators receive the identical CSV and rubric. Supply conversation IDs consistently if you want clustered uncertainty.

```sh
python3 validate_items.py annotation_items.csv
```

The template intentionally has headers only and will fail validation until populated. `synthetic/` contains four **fake test examples** and fabricated ratings, never real study results. Do not mix them with study data.

## Annotator workflow

Import the supplied CSV, enter an anonymous code such as `A` or `B`, read the rubric, then Begin. Rate adequacy and major semantic error independently; neither has a default. Comments are optional. Navigate freely; Jump to incomplete finds remaining work. Finish requires both responses on every item. Export CSV regularly and again at completion. Send the exported file to researchers yourself: the tool does not submit anything.

Each change saves to browser localStorage under annotator code plus SHA-256 of canonical imported fields in input order, including context and conversation IDs. A changed dataset starts a separate session with a warning; no results are merged. Reload, import the same dataset, and enter the same code to resume. Other annotators' sessions remain separate. This is not authentication; use separate browser profiles/devices if annotations must remain private from other local users. Avoid opening the same session in multiple tabs, which can overwrite each other's saves.

Storage failures are visibly reported. Clearing browser data, private browsing, changing origin or file path, or changing devices may lose browser saves. Exported CSVs are independent analysis backups; importing them to resume in the UI is not supported. Copy the entire project folder when distributing the interface (HTML, CSS and JS must stay together). Keep researcher documentation and test ratings away from annotators during rating.

Exports are BOM-prefixed UTF-8, fully quoted, one row per original item, with blank ratings for incomplete items. Columns: `annotator_id,id,direction,conversation_id,adequacy,major_error,comment,dataset_fingerprint`. For Excel, use Data → From Text/CSV and set identifier and comment columns to Text to preserve IDs exactly and avoid interpreting text as spreadsheet formulas.

## Analysis setup and execution

Python 3.9+ is supported. Install dependencies once (internet or an offline wheel directory is needed only for installation):

```sh
cd /Users/edwardyang/code/pseudo_gt_validation
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python analyze_annotations.py annotations_A.csv annotations_B.csv --items annotation_items.csv --out analysis_output
```

`--items` is optional. The script aligns by ID, rejects duplicates, incomplete responses, differing item sets/directions/fingerprints, conflicting metadata and identical annotator IDs. If some conversation IDs are missing, it asks for complete metadata rather than silently falling back to independent items. CSVs from other tools may omit fingerprints; without them source/reference identity cannot be verified from exports alone.

Outputs: tabular stdout, `results_summary.json`, and `disagreements.csv` with both ratings/comments for major-error disagreement or adequacy difference ≥2. Existing outputs in the specified directory are overwritten. Disagreements support optional separate adjudication; the script does not replace ratings or invent consensus.

Headline adequacy averages all individual ratings. Headline major-error rate is the **per-annotation** Yes fraction, not item consensus or adjudicated rate. Both equal an average of paired item means. Confidence intervals use 5,000 percentile bootstrap replicates (seed 2027; configurable with `--replicates` and `--seed`), keeping both judgments together. Complete conversation IDs select conversation cluster bootstrap; otherwise items are resampled. Cluster samples retain all included items and compute item-weighted means. Direction-specific CIs resample units within each direction. With fewer than two units, CIs are null. Small numbers of clusters limit precision.

Agreement includes quadratic-weighted Cohen's kappa on fixed ordinal labels 1–5, exact agreement, within-one-point agreement, and unweighted binary major-error kappa. Undefined kappa is JSON null. Near-uniform adequacy ratings (≥90% in one category) trigger a warning. Agreement is not translation quality.

## Reproducible smoke tests

```sh
source .venv/bin/activate
python self_test.py
# Optional developer browser test; requires installed Google Chrome:
python -m pip install playwright
python browser_test.py
```

The analysis self-test uses only fabricated data, reversed row order, expected numerical values, deterministic CIs, disagreement output, and malformed-input rejection. Results go to a temporary directory. Browser checks generate 100 synthetic multilingual items and test real local-file import, text safety, reload/edit/export, annotator/dataset separation, completion gating, and absence of network requests. Playwright is not needed by annotators.

## Reporting

Report actual sample size, sampling strategy, non-identifying annotator qualifications, rubric, means, per-annotation error rates with paired/clustered 95% CIs, and agreement. If a third person adjudicates, report that process separately from pre-adjudication agreement. Validation measures sampled reference accuracy, not that all references are error-free; 100 pairs provide limited precision. High agreement alone does not establish accuracy or eliminate BLEU style bias. Reference-free GEMBA-MQM is a separate complementary system evaluation.

## Website and single-file distribution

Run `python3 build_distribution.py` to create a UI-only `dist/`, a self-contained `dist/translation-validation-offline.html`, and `translation-validation-web.zip`. See [DEPLOY.md](DEPLOY.md) for GitHub Pages publishing and annotator distribution. A GitHub Actions workflow is included; a repository and Pages setup are still required before a public URL exists.
