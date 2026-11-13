"""Check rendered report pagination and TOC targets; visual review is separate."""
import argparse
import hashlib
import json
import re
from pathlib import Path
from zipfile import ZipFile
from lxml import etree as ET
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser()
parser.add_argument('--render-dir', required=True)
args = parser.parse_args()
folder = ROOT / args.render_dir
docx = ROOT / '.cache/report/Bao_cao_SAR_SOS_fields.docx'
pdf = folder / (docx.stem + '.pdf')
pages = [p.extract_text() for p in PdfReader(pdf).pages]
normalize = lambda text: re.sub(r'\s+', '', text)
normalized = [normalize(p) for p in pages]
with ZipFile(docx) as archive:
    xml = ET.fromstring(archive.read('word/document.xml'))
ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
W = '{' + ns['w'] + '}'
body = xml.find(W + 'body')
targets = {}
for p in body.findall(W + 'p'):
    text = ''.join(p.xpath('.//w:t/text()', namespaces=ns))
    for name in p.xpath('./w:bookmarkStart/@w:name', namespaces=ns):
        targets[name] = text
main_start = next(i for i, text in enumerate(pages) if i >= 8 and 'CHƯƠNG 1' in text)
reference_start = next(i for i, text in enumerate(pages) if i > main_start and 'TÀI LIỆU THAM KHẢO' in text)
checks = []
for p in xml.xpath('//w:sdt//w:p', namespaces=ns):
    names = p.xpath('.//w:hyperlink/@w:anchor', namespaces=ns)
    texts = p.xpath('.//w:t/text()', namespaces=ns)
    if not names or not texts:
        continue
    page_number = texts[-1].strip()
    target = targets[names[0]]
    if not page_number.isdigit():
        continue  # Roman preface checked visually.
    expected = main_start + int(page_number) - 1
    found = 0 <= expected < len(pages) and normalize(target) in normalized[expected]
    checks.append({'target': target, 'cached_page': int(page_number), 'pdf_page': expected + 1, 'found': found})
result = {'docx_sha256': hashlib.sha256(docx.read_bytes()).hexdigest(),
          'pdf_sha256': hashlib.sha256(pdf.read_bytes()).hexdigest(),
          'render': str(pdf.relative_to(ROOT)), 'pages': len(pages),
          'main_start': main_start + 1, 'main_end': reference_start,
          'main_page_count': reference_start - main_start,
          'latest_template_20_to_35': 20 <= reference_start - main_start <= 35,
          'original_guide_25_to_40': 25 <= reference_start - main_start <= 40,
          'toc_checks': checks, 'toc_all_found': all(x['found'] for x in checks),
          'layout_verified': False, 'note': 'Text-level audit is not visual verification'}
(ROOT / 'docs/report/render_audit.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({k: v for k, v in result.items() if k != 'toc_checks'}, ensure_ascii=True))
for check in checks:
    if not check['found']:
        print('CHECK:', json.dumps(check, ensure_ascii=True))
