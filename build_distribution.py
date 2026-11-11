"""Build an allowlisted static site and a standalone offline HTML file."""
from pathlib import Path
import shutil
import zipfile
import hashlib

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'dist'
ASSETS = ('index.html', 'styles.css', 'app.js', 'placeholder_data.js', 'placeholder_items.csv', 'DATA_ATTRIBUTION.md')

def build():
    # Only replace known generated files; refuse unexpected content in dist.
    allowed = set(ASSETS) | {'.nojekyll', 'translation-validation-offline.html'}
    if OUT.exists():
        unexpected = {p.name for p in OUT.iterdir()} - allowed
        if unexpected:
            raise ValueError(f'Unexpected files in dist; move them before publishing: {sorted(unexpected)}')
    OUT.mkdir(exist_ok=True)
    for name in ASSETS:
        shutil.copyfile(ROOT / name, OUT / name)
    (OUT / '.nojekyll').write_text('')
    html = (ROOT / 'index.html').read_text(encoding='utf-8')
    hosted_html = html
    for asset in ('styles.css', 'app.js', 'placeholder_data.js'):
        version = hashlib.sha256((ROOT / asset).read_bytes()).hexdigest()[:16]
        hosted_html = hosted_html.replace(f'"{asset}"', f'"{asset}?v={version}"')
    (OUT / 'index.html').write_text(hosted_html, encoding='utf-8')
    css = (ROOT / 'styles.css').read_text(encoding='utf-8')
    js = (ROOT / 'placeholder_data.js').read_text(encoding='utf-8') + '\n' + (ROOT / 'app.js').read_text(encoding='utf-8')
    # Inline resources use exact CSP hashes, with no external dependencies.
    import base64
    digest = lambda s: base64.b64encode(hashlib.sha256(s.encode('utf-8')).digest()).decode('ascii')
    html = html.replace("script-src 'self'", f"script-src 'sha256-{digest(js)}'")
    html = html.replace("style-src 'self'", f"style-src 'sha256-{digest(css)}'")
    html = html.replace('<link rel="stylesheet" href="styles.css">', '<style>'+css+'</style>')
    html = html.replace('<script src="app.js" defer></script>', '').replace('<script src="placeholder_data.js" defer></script>', '')
    # Embed credits too, so the single-file edition retains attribution offline.
    import html as html_module
    credits = html_module.escape((ROOT / 'DATA_ATTRIBUTION.md').read_text(encoding='utf-8'))
    html = html.replace('</main>', '<details id="data-credits"><summary>Data sources and licenses</summary><pre class="text">'+credits+'</pre></details></main>')
    html = html.replace('<a href="placeholder_items.csv" download>Download demo CSV</a> · ', '')
    html = html.replace('href="DATA_ATTRIBUTION.md"', 'href="#data-credits"')
    html = html.replace('</body>', '<script>'+js+'</script></body>')
    (OUT / 'translation-validation-offline.html').write_text(html, encoding='utf-8')
    archive = ROOT / 'translation-validation-web.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
        for name in sorted(allowed):
            z.write(OUT / name, name)
    print(f'Static site: {OUT}\nOffline single file: {OUT / "translation-validation-offline.html"}\nWeb package: {archive}')

if __name__ == '__main__':
    build()
