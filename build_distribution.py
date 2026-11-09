"""Build an allowlisted static site and a standalone offline HTML file."""
from pathlib import Path
import shutil
import zipfile

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'dist'
ASSETS = ('index.html', 'styles.css', 'app.js')

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
    css = (ROOT / 'styles.css').read_text(encoding='utf-8')
    js = (ROOT / 'app.js').read_text(encoding='utf-8')
    # Inline resources use exact CSP hashes, with no external dependencies.
    import hashlib, base64
    digest = lambda s: base64.b64encode(hashlib.sha256(s.encode('utf-8')).digest()).decode('ascii')
    html = html.replace("script-src 'self'", f"script-src 'sha256-{digest(js)}'")
    html = html.replace("style-src 'self'", f"style-src 'sha256-{digest(css)}'")
    html = html.replace('<link rel="stylesheet" href="styles.css">', '<style>'+css+'</style>')
    html = html.replace('<script src="app.js" defer></script>', '')
    html = html.replace('</body>', '<script>'+js+'</script></body>')
    (OUT / 'translation-validation-offline.html').write_text(html, encoding='utf-8')
    archive = ROOT / 'translation-validation-web.zip'
    with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
        for name in sorted(allowed):
            z.write(OUT / name, name)
    print(f'Static site: {OUT}\nOffline single file: {OUT / "translation-validation-offline.html"}\nWeb package: {archive}')

if __name__ == '__main__':
    build()
