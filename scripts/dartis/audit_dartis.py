"""Audit the supplementary PANGAEA catalog without changing the SOS experiment.

Input: data/dartis/catalog.tsv downloaded from the DOI's format=textfile URL.
This audits catalog metadata, not image pixels or annotation accuracy.
"""

import sys as _sys
from pathlib import Path as _Path
_project_root = _Path(__file__).resolve().parents[2]
_sys.path.insert(0, str(_project_root))
_sys.path.insert(0, str(_project_root / "src"))

import csv
import hashlib
import io
import json
import re
import xml.etree.ElementTree as ET
from collections import Counter
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[2]
SOURCE = 'https://doi.pangaea.de/10.1594/PANGAEA.980773?format=textfile'


def audit(path):
    raw = path.read_bytes()
    content = raw.decode('utf-8-sig')
    _, table = content.split('*/', 1)
    rows = list(csv.DictReader(io.StringIO(table.lstrip()), delimiter='\t'))
    assert rows, 'Empty catalog'
    fields = list(rows[0])

    def column(suffix):
        matches = [f for f in fields if f.endswith(f'({suffix})')]
        assert len(matches) == 1, (suffix, matches)
        return matches[0]

    image_key, tag_key = column('jpg_file'), column('tag')
    scene_key = column('Sentinel_ID')
    width_key, height_key = column('patch_width'), column('patch_height')
    grouped = {}
    for row in rows:
        grouped.setdefault(row[image_key], []).append(row)
    errors, samples, scenes, downloaded_checks = [], [], set(), []
    for filename, objects in sorted(grouped.items()):
        row = objects[0]
        subset = filename[:2]
        assert subset in {'oc', 'ow', 'nc', 'nw'}, filename
        width, height = int(row[width_key]), int(row[height_key])
        scene_ids = sorted(set(re.findall(r'S1[AB]_[A-Z0-9_]+\.SAFE', row[scene_key])))
        scenes.update(scene_ids)
        if not scene_ids:
            errors.append({'image': filename, 'error': 'Missing scene ID'})
        for other in objects:
            if any(other[k] != row[k] for k in [scene_key, width_key, height_key,
                                                column('start_time'), column('end_time')]):
                errors.append({'image': filename, 'error': 'Inconsistent patch metadata'})
            if subset.startswith('o'):
                x0, y0, x1, y1 = [float(other[column('obj_patchloc_' + key)])
                                   for key in ['xmin', 'ymin', 'xmax', 'ymax']]
                if not (0 <= x0 < x1 <= width and 0 <= y0 < y1 <= height):
                    errors.append({'image': filename, 'tag': other[tag_key],
                                   'error': 'Box outside bounds or degenerate',
                                   'box': [x0, y0, x1, y1]})
        samples.append({'filename': filename, 'subset': subset, 'scene_ids': scene_ids,
                        'width': width, 'height': height,
                        'object_rows': len(objects) if subset.startswith('o') else 0,
                        'url': 'https://download.pangaea.de/dataset/980773/files/' + filename})
        local = path.parent / filename
        if local.exists():
            with Image.open(local) as image:
                image.load()
                assert image.size == (width, height), filename
                mode = image.mode
            checked = {'filename': filename, 'size': [width, height], 'mode': mode,
                       'sha256': hashlib.sha256(local.read_bytes()).hexdigest()}
            annotation = local.with_suffix('.xml')
            if annotation.exists():
                xml = ET.parse(annotation).getroot()
                assert xml.findtext('filename') == row[column('patch_name')] + '.jpg'
                assert int(xml.findtext('size/width')) == width
                assert int(xml.findtext('size/height')) == height
                boxes = [tuple(int(o.findtext('bndbox/' + key)) for key in
                               ['xmin', 'ymin', 'xmax', 'ymax']) for o in xml.findall('object')]
                expected = [tuple(int(o[column('obj_patchloc_' + key)]) for key in
                                  ['xmin', 'ymin', 'xmax', 'ymax']) for o in objects]
                assert sorted(boxes) == sorted(expected), filename
                assert all(o.findtext('name') == 'oil' for o in xml.findall('object'))
                checked.update(xml_sha256=hashlib.sha256(annotation.read_bytes()).hexdigest(),
                               box_count=len(boxes), boxes_match_catalog=True,
                               original_xml_filename=xml.findtext('filename'))
            downloaded_checks.append(checked)
    counts = Counter(s['subset'] for s in samples)
    report = {'source': SOURCE, 'catalog_sha256': hashlib.sha256(raw).hexdigest(),
              'catalog_bytes': len(raw), 'rows': len(rows), 'unique_images': len(samples),
              'images_by_subset': dict(sorted(counts.items())), 'scene_count': len(scenes),
              'oil_object_rows': sum(s['object_rows'] for s in samples),
              'dimensions': dict(Counter(f"{s['width']}x{s['height']}" for s in samples)),
              'issues': errors, 'metadata_checks_passed': not errors,
              'downloaded_checks': downloaded_checks,
              'scope': 'All catalog rows; only downloaded files listed were decoded and checked',
              'subtype_labels_verified': False, 'incidence_angle_band_present': False,
              'wind_data_present': False,
              'warnings': ['No-oil cluster codes are K-means groups, not physical subtype labels.',
                           'Oil annotations are boxes, not pixel masks.',
                           'Keep all source scenes of a patch in the same split.',
                           'Do not combine box metrics with SOS mask-object metrics.']}
    return report, samples


if __name__ == '__main__':
    report, samples = audit(ROOT / 'data/dartis/catalog.tsv')
    output = ROOT / 'docs/management/dartis_catalog_audit.json'
    output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    (ROOT / 'data/dartis/catalog_manifest.json').write_text(
        json.dumps(samples, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(report, ensure_ascii=True, indent=2))
