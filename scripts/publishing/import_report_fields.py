"""Import only refreshed TOC results and their bookmark targets from Word.

Word rewrites styles, footers and metadata on save. Copy only refreshed TOC
containers, their bookmark targets, and newly generated TOC styles. Preserve
every existing style definition and all other package parts.
"""

import sys as _sys
from pathlib import Path as _Path
_project_root = _Path(__file__).resolve().parents[2]
_sys.path.insert(0, str(_project_root))
_sys.path.insert(0, str(_project_root / "scripts"))

import hashlib
import json
from copy import deepcopy
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED
from lxml import etree as ET

ROOT = Path(__file__).resolve().parents[2]
FOLDER = ROOT / '.cache/report'
NS = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
W = '{' + NS['w'] + '}'
refresh = json.loads((FOLDER / 'word_refresh.json').read_text(encoding='utf-8-sig'))
assert refresh['source_sha256'] == hashlib.sha256((FOLDER / 'Bao_cao_SAR_SOS.docx').read_bytes()).hexdigest(), 'Word fields are stale: rerun update_report_fields.ps1'
assert refresh['refreshed_sha256'] == hashlib.sha256((FOLDER / 'Bao_cao_SAR_SOS_word.docx').read_bytes()).hexdigest(), 'Refreshed Word copy changed'


def paragraph_key(p):
    return ''.join(p.xpath('.//w:t/text()', namespaces=NS)).strip()


with ZipFile(FOLDER / 'Bao_cao_SAR_SOS.docx') as source, ZipFile(FOLDER / 'Bao_cao_SAR_SOS_word.docx') as refreshed:
    original = ET.fromstring(source.read('word/document.xml'))
    word = ET.fromstring(refreshed.read('word/document.xml'))
    styles = ET.fromstring(source.read('word/styles.xml'))
    word_styles = ET.fromstring(refreshed.read('word/styles.xml'))
    existing_styles = set(styles.xpath('./w:style/@w:styleId', namespaces=NS))
    added_styles = []
    for style in word_styles.findall(W + 'style'):
        ident = style.get(W + 'styleId')
        if ident not in existing_styles and (ident.startswith('TOC') or ident == 'TableofFigures'):
            added = deepcopy(style)
            if ident.startswith('TOC'):
                properties = added.find(W + 'pPr')
                if properties is None:
                    properties = ET.SubElement(added, W + 'pPr')
                spacing = properties.find(W + 'spacing')
                if spacing is None:
                    spacing = ET.SubElement(properties, W + 'spacing')
                for key, value in {'before': '0', 'after': '0', 'line': '312', 'lineRule': 'auto'}.items():
                    spacing.set(W + key, value)
            styles.append(added)
            added_styles.append(ident)
    original_controls = original.xpath('//w:sdt', namespaces=NS)
    word_controls = word.xpath('//w:sdt', namespaces=NS)
    assert len(original_controls) == len(word_controls) == 3
    targets = {}
    for p in original.xpath('//w:body/w:p', namespaces=NS):
        targets.setdefault(paragraph_key(p), []).append(p)
    imported = []
    used_ids = [int(x) for x in original.xpath('//w:bookmarkStart/@w:id', namespaces=NS)]
    next_id = max(used_ids, default=0) + 1
    for p in word.xpath('//w:body/w:p', namespaces=NS):
        bookmarks = p.xpath('./w:bookmarkStart[starts-with(@w:name,"_Toc")]', namespaces=NS)
        if not bookmarks:
            continue
        matches = targets.get(paragraph_key(p), [])
        assert len(matches) == 1, ('Ambiguous bookmark target', paragraph_key(p))
        target = matches[0]
        for bookmark in bookmarks:
            name = bookmark.get(W + 'name')
            start = ET.Element(W + 'bookmarkStart', {W + 'id': str(next_id), W + 'name': name})
            end = ET.Element(W + 'bookmarkEnd', {W + 'id': str(next_id)})
            target.insert(1 if target.find(W + 'pPr') is not None else 0, start)
            target.append(end)
            imported.append(name)
            next_id += 1
    for old, new in zip(original_controls, word_controls):
        old_content = old.find(W + 'sdtContent')
        new_content = deepcopy(new.find(W + 'sdtContent'))
        old.replace(old_content, new_content)
    anchors = original.xpath('//w:sdt//w:hyperlink/@w:anchor', namespaces=NS)
    assert set(anchors).issubset(set(imported)), set(anchors) - set(imported)
    payload = ET.tostring(original, xml_declaration=True, encoding='UTF-8', standalone=True)
    style_payload = ET.tostring(styles, xml_declaration=True, encoding='UTF-8', standalone=True)
    destination = FOLDER / 'Bao_cao_SAR_SOS_fields.docx'
    with ZipFile(destination, 'w', ZIP_DEFLATED) as result:
        for name in source.namelist():
            result.writestr(name, payload if name == 'word/document.xml' else style_payload if name == 'word/styles.xml' else source.read(name))
    with ZipFile(destination) as result:
        assert all(source.read(name) == result.read(name) for name in source.namelist() if name not in ('word/document.xml', 'word/styles.xml'))
        before = ET.fromstring(source.read('word/styles.xml'))
        after = ET.fromstring(result.read('word/styles.xml'))
        for style in before:
            ident = style.get(W + 'styleId')
            match = after.xpath('./w:style[@w:styleId=$ident]', namespaces=NS, ident=ident) if ident else after.findall(style.tag)
            assert len(match) == 1 and ET.tostring(style) == ET.tostring(match[0]), 'Existing style changed'
audit = {'output': str(destination), 'bookmarks_imported': len(imported), 'toc_controls': 3,
         'existing_styles_preserved': True, 'added_field_styles': added_styles,
         'sha256': hashlib.sha256(destination.read_bytes()).hexdigest(),
         'layout_verified': False, 'note': 'Word page numbers still require comparison with final render'}
(FOLDER / 'field_import_audit.json').write_text(json.dumps(audit, indent=2), encoding='utf-8')
print('Imported contents, bookmarks and missing field styles; existing styles and other parts unchanged.')
