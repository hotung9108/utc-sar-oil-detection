"""Read-only inventory of the retained course report template."""

import sys as _sys
from pathlib import Path as _Path
_project_root = _Path(__file__).resolve().parents[2]
_sys.path.insert(0, str(_project_root))
_sys.path.insert(0, str(_project_root / "scripts"))

import hashlib
import json
from pathlib import Path
from zipfile import ZipFile
from lxml import etree

ROOT = Path(__file__).resolve().parents[2]
reference = next(ROOT.glob('*12_11.docx'))
destination = ROOT / '.cache/report'
destination.mkdir(parents=True, exist_ok=True)
ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
with ZipFile(reference) as archive:
    parts = {i.filename: {'bytes': i.file_size, 'sha256': hashlib.sha256(archive.read(i)).hexdigest(),
                         'policy': 'editable' if i.filename in ('word/document.xml', 'word/_rels/document.xml.rels', 'word/settings.xml', '[Content_Types].xml') else 'preserve'}
             for i in archive.infolist()}
    doc = etree.fromstring(archive.read('word/document.xml'))
    styles = etree.fromstring(archive.read('word/styles.xml'))
    data = {'reference': str(reference), 'sha256': hashlib.sha256(reference.read_bytes()).hexdigest(),
            'parts': parts,
            'sections': [etree.tostring(s, encoding='unicode') for s in doc.xpath('//w:sectPr', namespaces=ns)],
            'styles': [etree.tostring(s, encoding='unicode') for s in styles.xpath('//w:style', namespaces=ns)],
            'paragraph_properties': [{'index': i, 'xml': etree.tostring(p, encoding='unicode')}
                                     for i, p in enumerate(doc.xpath('//w:body/w:p', namespaces=ns))],
            'tables': [etree.tostring(t, encoding='unicode') for t in doc.xpath('//w:body/w:tbl', namespaces=ns)],
            'controls': len(doc.xpath('//w:sdt', namespaces=ns)),
            'fields': doc.xpath('//w:instrText/text()', namespaces=ns),
            'drawings': len(doc.xpath('//w:drawing', namespaces=ns))}
(destination / 'template_inventory.json').write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
print('Inventoried', len(parts), 'parts;', len(data['tables']), 'tables;', data['controls'], 'controls;', data['drawings'], 'drawings')
