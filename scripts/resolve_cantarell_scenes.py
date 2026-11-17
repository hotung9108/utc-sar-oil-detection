"""Resolve all publisher acquisition prefixes to full public Sentinel identities."""
import csv
import hashlib
import io
import json
import re
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode
from urllib.request import urlopen

from audit_cantarell_all import fetch, CACHE
from audit_cantarell_source import ROOT, REVISION


def resolve(filename):
    match = re.fullmatch(r'(\d+) (S1[AB]_IW_GRDH_1SDV_(\d{8}T\d{6}))_NR_Orb_Cal_TC.tif', filename)
    if not match:
        raise ValueError(f'Unsupported publisher filename: {filename}')
    number, prefix, stamp = match.groups()
    date = datetime.strptime(stamp, '%Y%m%dT%H%M%S').replace(tzinfo=timezone.utc)
    folder = CACHE / 'scene_catalog' / prefix
    folder.mkdir(parents=True, exist_ok=True)
    receipts = []

    def get(name, url):
        target = folder / name
        if not target.exists():
            with urlopen(url, timeout=45) as response:
                raw = response.read(10_000_001)
            if len(raw) > 10_000_000:
                raise ValueError('Metadata size limit exceeded')
            target.write_bytes(raw)
        raw = target.read_bytes()
        receipts.append({'url': url, 'file': target.relative_to(ROOT).as_posix(),
                         'sha256': hashlib.sha256(raw).hexdigest(), 'bytes': len(raw)})
        return json.loads(raw)

    params = {'platform': 'Sentinel-1A' if prefix.startswith('S1A') else 'Sentinel-1B',
              'processingLevel': 'GRD_HD', 'start': (date-timedelta(seconds=1)).isoformat(),
              'end': (date+timedelta(seconds=1)).isoformat(), 'output': 'geojson'}
    catalog = get('asf.json', 'https://api.daac.asf.alaska.edu/services/search/param?' + urlencode(params))
    matches = [f for f in catalog['features'] if f['properties']['sceneName'].startswith(prefix+'_')]
    if len(matches) != 1:
        raise ValueError(f'Expected one exact acquisition match, got {len(matches)}')
    scene = matches[0]['properties']['sceneName']
    base = f'https://sentinel-s1-l1c.s3.amazonaws.com/GRD/{date.year}/{date.month}/{date.day}/IW/DV/{scene}/'
    product = get('productInfo.json', base+'productInfo.json')
    if product['id'] != scene or product['startTime'] != date.strftime('%Y-%m-%dT%H:%M:%S'):
        raise ValueError('Product identity/start time mismatch')
    return {'publisher_filename': filename, 'group': f'IMG_{number}', 'scene': scene,
            'start_time': product['startTime'], 'footprint': product['footprint'],
            'polarization': product['polarization'], 'base_url': base, 'receipts': receipts,
            'vv_available': 'measurement/iw-vv.tiff' in product['filenameMap'].values()}


def main():
    raw, csv_receipts = fetch('CSV/Oil_Stats_manual_windows_16bits_800x600.csv')
    rows = list(csv.DictReader(io.StringIO(raw.decode('utf-8-sig')), delimiter=';'))
    filenames = sorted({r['IMG_FNAME'] for r in rows})
    results, errors = [], []
    with ThreadPoolExecutor(max_workers=3) as pool:
        pending = {pool.submit(resolve, name): name for name in filenames}
        for future in as_completed(pending):
            try:
                result = future.result()
                results.append(result)
                print(f"Resolved {result['group']}: {result['scene']}", flush=True)
            except Exception as exc:
                errors.append({'filename': pending[future], 'error': f'{type(exc).__name__}: {exc}'})
    results.sort(key=lambda r: r['group'])
    splits = {}
    for split in ('train', 'val', 'test'):
        content, _ = fetch(f'splits/{split}.csv')
        for row in csv.DictReader(io.StringIO(content.decode('utf-8-sig'))):
            group = row['sample_id'].split('_TILE_')[0]
            if group in splits and splits[group] != split:
                raise ValueError('Publisher group crosses splits')
            splits[group] = split
    scene_splits = {}
    for item in results:
        item['split'] = splits[item['group']]
        scene_splits.setdefault(item['scene'], set()).add(item['split'])
    audit = {'revision': REVISION, 'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
             'csv_receipts': csv_receipts, 'expected_acquisitions': len(filenames),
             'resolved_acquisitions': len(results), 'complete': len(results) == len(filenames) and not errors,
             'results': results, 'errors': errors,
             'cross_split_full_scene_ids': {k: sorted(v) for k, v in scene_splits.items() if len(v) > 1},
             'limits': ['Exact platform/mode/acquisition timestamp plus public product identity; not a pixel-level registration check for every tile.',
                        'Scene IDs distinguish acquisitions, not independent spill events or weather conditions.']}
    (ROOT / 'docs/management/cantarell_scenes_audit.json').write_text(json.dumps(audit, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k: audit[k] for k in ('expected_acquisitions', 'resolved_acquisitions', 'complete', 'errors', 'cross_split_full_scene_ids')}, indent=2))


if __name__ == '__main__':
    main()
