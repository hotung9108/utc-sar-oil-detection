"""Read complete, provenance-checked DARTIS diagnostics for reporting."""
import json
from evaluate_dartis import ROOT, aggregate, digest, ensure_run


def verified_results():
    ensure_run()
    destination = ROOT / 'results/dartis'
    report = json.loads((destination / 'evaluation.json').read_text(encoding='utf-8'))
    protocol = json.loads((destination / 'protocol.json').read_text(encoding='utf-8'))
    selected_path = ROOT / 'results/sos/selected.json'
    selected = json.loads(selected_path.read_text(encoding='utf-8'))
    sources = {
        'protocol_sha256': destination / 'protocol.json',
        'manifest_sha256': ROOT / 'data/dartis/catalog_manifest.json',
        'script_sha256': ROOT / 'scripts/evaluate_dartis.py',
        'selected_sha256': selected_path,
        'model_sha256': selected_path.parent / selected['model_file'],
    }
    for key, source in sources.items():
        if digest(source) != report['provenance'][key]:
            raise ValueError(f'Provenance changed: {source}')
    for key in ('selected_sha256', 'model_sha256'):
        if protocol[key] != report['provenance'][key]:
            raise ValueError(f'Model differs from frozen protocol: {key}')
    manifest = json.loads(sources['manifest_sha256'].read_text(encoding='utf-8'))
    expected = {r['filename']: r for r in manifest if r['subset'] in {'nc', 'nw'}}
    rows = report['per_image']
    if (not report['complete'] or report['expected'] != 2290 or
            report['completed'] != 2290 or len(rows) != 2290 or
            len(expected) != 2290 or {r['filename'] for r in rows} != set(expected)):
        raise ValueError('Incomplete or duplicate population; cannot publish full-set metrics')
    for row in rows:
        source = expected[row['filename']]
        if row['subset'] != source['subset'] or row['scene_ids'] != source['scene_ids']:
            raise ValueError('Image metadata differs from manifest')
        if row['cluster'] != row['filename'].split('-')[2]:
            raise ValueError('Invalid cluster')
        if row['pixels'] != source['width'] * source['height']:
            raise ValueError('Invalid pixel denominator')
        if not 0 <= row['predicted_oil_pixels'] <= row['pixels']:
            raise ValueError('Invalid predicted pixel count')
        if not 0 <= row['retained_regions'] <= row['candidate_regions']:
            raise ValueError('Invalid region counts')
        if row['false_alarm'] != (row['retained_regions'] > 0):
            raise ValueError('False-alarm indicator inconsistent with regions')
        if row['false_alarm'] != (row['predicted_oil_pixels'] > 0):
            raise ValueError('False-alarm indicator inconsistent with mask')
        if digest(ROOT / 'data/dartis' / row['filename']) != row['image_sha256']:
            raise ValueError('Image bytes changed after inference')
    if aggregate(rows) != report['overall']:
        raise ValueError('Overall aggregate differs from per-image counts')
    for subset in ('nc', 'nw'):
        if aggregate([r for r in rows if r['subset'] == subset]) != report['by_subset'][subset]:
            raise ValueError('Subset aggregate differs from per-image counts')
    keys = {r['subset'] + '-' + r['cluster'] for r in rows}
    if set(report['by_cluster']) != keys:
        raise ValueError('Cluster population mismatch')
    for key in keys:
        if aggregate([r for r in rows if r['subset'] + '-' + r['cluster'] == key]) != report['by_cluster'][key]:
            raise ValueError('Cluster aggregate differs from per-image counts')
    return report
