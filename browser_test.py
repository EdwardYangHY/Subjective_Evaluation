"""Developer smoke test using installed Chrome and optional playwright package."""
import csv
import io
import tempfile
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright
ROOT = Path(__file__).resolve().parent
with tempfile.TemporaryDirectory() as tmp, sync_playwright() as p:
    browser = p.chromium.launch(channel='chrome', headless=True)
    context = browser.new_context(accept_downloads=True)
    page = context.new_page()
    errors=[]; requests=[]
    page.on('pageerror', lambda e: errors.append(str(e)))
    page.on('request', lambda r: requests.append(r.url) if r.url.startswith(('http:', 'https:')) else None)
    source='Synthetic, "quoted"\n中文 <img src=x onerror=alert(1)>'
    dataset=Path(tmp)/'items.csv'
    with dataset.open('w',encoding='utf-8-sig',newline='') as f:
        w=csv.writer(f);w.writerow(['id','direction','source','reference','conversation_id','context'])
        for i in range(100): w.writerow([f'SYNTHETIC_{i:03}', 'en-zh' if i%2==0 else 'zh-en', source, '合成测试 / synthetic only', f'fake_{i//4}', 'Fake context'])
    def start(name):
        page.locator('#file').set_input_files([])
        page.locator('#file').set_input_files(dataset)
        page.locator('#annotator').fill(name)
        page.locator('#begin').click()
    target = Path(sys.argv[1]).resolve() if len(sys.argv)>1 else ROOT/'index.html'
    page.goto(target.as_uri())
    assert not page.locator('#file').is_visible()
    page.locator('#annotator').fill('DEMO_TEST')
    page.locator('#begin').click()
    assert page.locator('#counts').inner_text().startswith('225 items · en-zh: 136 · zh-en: 89')
    assert not page.locator('#demoNotice').is_visible()
    assert '[Turn 1]' in page.locator('#source').inner_text()
    assert '[Turn 1]' in page.locator('#reference').inner_text()
    assert not page.locator('#creditPanel').is_visible()
    assert page.locator('input[type=radio]:checked').count()==0
    with page.expect_download() as demo_download: page.locator('#export').click()
    with Path(demo_download.value.path()).open(encoding='utf-8-sig',newline='') as f: demo_rows=list(csv.DictReader(f))
    assert len(demo_rows)==225 and all(r['adequacy']=='' for r in demo_rows)
    page.reload();start('A')
    assert page.locator('#counts').inner_text().startswith('100 items · en-zh: 50 · zh-en: 50')
    assert page.locator('#source').inner_text()==source
    assert page.locator('#source img').count()==0
    assert page.locator('input[type=radio]:checked').count()==0
    page.locator('#finish').click();assert 'Complete all three' in page.locator('#message').inner_text()
    page.locator('input[name=adequacy][value="5"]').check()
    assert page.locator('#progressText').inner_text()=='0 / 100 completed'
    page.locator('input[name=major_error][value=No]').check()
    assert page.locator('#progressText').inner_text()=='0 / 100 completed'
    page.locator('input[name=naturalness][value="3"]').check()
    page.locator('#comment').fill('Synthetic "note", 中文\nsecond line')
    with page.expect_download() as d: page.locator('#export').click()
    downloaded=Path(d.value.path());assert downloaded.read_bytes().startswith(b'\xef\xbb\xbf')
    with downloaded.open(encoding='utf-8-sig',newline='') as f: rows=list(csv.DictReader(f))
    assert len(rows)==100 and rows[0]['adequacy']=='5' and rows[1]['adequacy']==''
    assert rows[0]['naturalness']=='3' and rows[1]['naturalness']==''
    assert rows[0]['comment']=='Synthetic "note", 中文\nsecond line'
    page.reload();start('A');assert page.locator('input[name=adequacy]:checked').input_value()=='5'
    page.locator('#switch').click();start('B');assert page.locator('input[type=radio]:checked').count()==0
    page.locator('#switch').click();start('A');assert page.locator('#comment').input_value().startswith('Synthetic')
    page.locator('input[name=adequacy][value="4"]').check();page.reload();start('A')
    assert page.locator('input[name=adequacy]:checked').input_value()=='4'
    assert page.locator('input[name=naturalness]:checked').input_value()=='3'
    page.locator('#incomplete').click();assert 'Item 2 of 100' in page.locator('#position').inner_text()
    for i in range(1,100):
        page.locator('input[name=adequacy][value="5"]').check();page.locator('input[name=major_error][value=No]').check()
        page.locator('input[name=naturalness][value="4"]').check()
        if i<99: page.locator('#next').click()
    page.locator('#finish').click();assert 'nothing has been submitted' in page.locator('#summary').inner_text()
    # Simulate an existing pre-naturalness browser save and verify migration.
    page.evaluate('''() => {for(let i=0;i<localStorage.length;i++){const k=localStorage.key(i);if(k.startsWith('translation-validation:v1:A:')){const s=JSON.parse(localStorage.getItem(k));s.ratings.forEach(r=>delete r.naturalness);localStorage.setItem(k,JSON.stringify(s));}}}''')
    page.reload();start('A')
    assert 'previous ratings were restored' in page.locator('#message').inner_text()
    assert page.locator('#progressText').inner_text()=='0 / 100 completed'
    assert page.locator('input[name=adequacy]:checked').count()==1
    assert page.locator('input[name=naturalness]:checked').count()==0
    assert page.locator('#summary').inner_text()==''
    page.locator('#switch').click()
    dataset.write_text(dataset.read_text(encoding='utf-8-sig').replace('Fake context','Changed fake context'),encoding='utf-8')
    start('A');assert 'different dataset' in page.locator('#message').inner_text()
    assert page.locator('input[type=radio]:checked').count()==0
    assert not errors,errors
    assert not requests,requests
    browser.close()
print('PASS: 225-item study v2 import/export plus 100 synthetic items; escaping, blank defaults, completion, Unicode, resume/edit, isolation, no network requests. Test ratings only.')
