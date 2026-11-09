# Distribute the annotation interface

## GitHub Pages

The site is entirely static. Hosting serves the HTML/CSS/JavaScript; imported datasets and annotations stay in the browser. Opening the hosted page requires internet, but rating and exporting after it loads do not call a server. Offline reopening is supported by the separate standalone file, not by a service worker.

1. Create a GitHub repository, preferably with a neutral name such as `translation-validation` to preserve blinded rating.
2. Push the project source to its `main` branch, excluding ignored files and any study data. A public source repository exposes its README and synthetic test files; if that would compromise blinding, publish only the contents of `dist/` using the manual method below.
3. In repository **Settings → Pages → Build and deployment → Source**, choose **GitHub Actions**.
4. Run **Actions → Deploy annotation site → Run workflow**, or push a change to `main`.
5. Open the URL shown by the deployment. It normally has the form `https://ACCOUNT.github.io/translation-validation/`.

The supplied workflow packages an explicit allowlist of UI files. The deployed website does not include study data, Python analysis, researcher documentation, or synthetic ratings. GitHub repository visibility and website contents are separate: avoid placing sensitive data anywhere in a public repository.

Official setup reference: https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages

### Manual publishing with a neutral, UI-only repository

Run `python3 build_distribution.py`. Upload the **contents** of `dist/` (not the folder itself) to the root of a new repository, then choose **Settings → Pages → Deploy from a branch → main → /(root)**. This publishes only the interface. No Actions workflow is needed for this method. Rebuild and replace these files when updating the app.

## A single file to send directly

`dist/translation-validation-offline.html` contains the complete CSS and JavaScript with a restrictive hash-based content security policy. Send that one file to annotators, who can save and open it in Chrome. No installation, Python, or internet is needed. This file has exactly the same rating and export behavior as the hosted page.

`translation-validation-web.zip` contains the website assets and standalone file for distribution. It contains no datasets or fabricated ratings. Regenerate it with `python3 build_distribution.py` after editing the source files; do not edit generated copies.

## What to send annotators

Send the website link (or offline HTML file), the study input CSV separately, and each person's anonymous annotator code. They import the CSV, rate items, export `annotations_CODE.csv`, and return the file to you. There is no automatic collection or backend.

Local-file and hosted-page browser storage are separate. Before moving from a local file to the website, export any existing work. CSV backup re-import into the UI is not currently supported; use the original location to finish an existing session. Keep the URL stable during the study.

## This repository

Remote: `git@github.com:EdwardYangHY/Subjective_Evaluation.git`

Local checkout: `/Users/edwardyang/code/pseudo_gt_validation`

For routine updates:

```sh
cd /Users/edwardyang/code/pseudo_gt_validation
git pull --ff-only
# Edit the source files, then build and check changes.
python3 build_distribution.py
git diff
git add <changed-source-files>
git commit -m "Describe the change"
git push
```

Select GitHub Actions as the Pages source before the first deployment.
Expected site URL after successful deployment: `https://edwardyanghy.github.io/Subjective_Evaluation/`.
This URL is not a claim that deployment has completed.
