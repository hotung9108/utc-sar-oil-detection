"""Retrieve verified VV geolocation and calibration metadata for all source scenes."""
import hashlib
import json
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.request import urlopen

import numpy as np

from audit_cantarell_source import ROOT, REVISION


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inspect(scene):
    for receipt in scene['receipts']:
        if sha(ROOT / receipt['file']) != receipt['sha256']:
            raise ValueError('Source catalog/product hash mismatch')
    folder = ROOT / '.cache/cantarell_source' / REVISION / 'physical_metadata' / scene['scene']
    folder.mkdir(parents=True, exist_ok=True)
    files = []

    def get(name, relative):
        path = folder / name
        url = scene['base_url']+relative
        if not path.exists():
            with urlopen(url, timeout=45) as response:
                raw = response.read(15_000_001)
            if len(raw)>15_000_000:
                raise ValueError('Metadata exceeds size limit')
            # Validate XML before caching to avoid persisting an HTTP error document.
            ET.fromstring(raw)
            path.write_bytes(raw)
        raw = path.read_bytes()
        files.append({'file': path.relative_to(ROOT).as_posix(), 'url': url, 'bytes': len(raw), 'sha256': sha(path)})
        return ET.fromstring(raw)

    annotation = get('annotation-vv.xml', 'annotation/iw-vv.xml')
    calibration = get('calibration-vv.xml', 'annotation/calibration/calibration-iw-vv.xml')
    points = annotation.findall('.//geolocationGridPoint')
    rows = sorted({int(p.findtext('line')) for p in points})
    cols = sorted({int(p.findtext('pixel')) for p in points})
    if len({(p.findtext('line'), p.findtext('pixel')) for p in points}) != len(rows)*len(cols):
        raise ValueError('Incomplete rectangular geolocation grid')
    angles = np.array([float(p.findtext('incidenceAngle')) for p in points])
    if not np.all(np.isfinite(angles)) or np.any((angles<=0)|(angles>=90)):
        raise ValueError('Invalid incidence angles')
    vectors = calibration.findall('.//calibrationVector')
    lut_rows = np.array([int(v.findtext('line')) for v in vectors])
    lut_cols = np.fromstring(vectors[0].findtext('pixel'), sep=' ')
    if np.any(np.diff(lut_rows)<=0) or np.any(np.diff(lut_cols)<=0):
        raise ValueError('Unsorted calibration coordinates')
    if not all(np.array_equal(lut_cols, np.fromstring(v.findtext('pixel'), sep=' ')) for v in vectors):
        raise ValueError('Nonrectangular calibration coordinates')
    lut_ranges = {}
    for name in ('sigmaNought', 'gamma'):
        lut = np.array([np.fromstring(v.findtext(name), sep=' ') for v in vectors])
        if lut.shape != (len(lut_rows), len(lut_cols)) or not np.all(np.isfinite(lut)) or np.any(lut<=0):
            raise ValueError('Invalid calibration LUT')
        lut_ranges[name] = [float(lut.min()), float(lut.max())]
    height = int(annotation.findtext('.//imageInformation/numberOfLines'))
    width = int(annotation.findtext('.//imageInformation/numberOfSamples'))
    pol = annotation.findtext('.//adsHeader/polarisation')
    if pol != 'VV' or calibration.findtext('.//adsHeader/polarisation') != 'VV':
        raise ValueError('Unexpected polarization')
    return {'group': scene['group'], 'scene': scene['scene'], 'files': files,
            'shape': [height, width], 'polarization': pol,
            'geolocation_points': len(points), 'geolocation_shape': [len(rows), len(cols)],
            'geolocation_support_line_pixel': [[rows[0], rows[-1]], [cols[0], cols[-1]]],
            'incidence_range': [float(angles.min()), float(angles.max())],
            'calibration_vectors': len(vectors), 'calibration_shape': [len(lut_rows), len(lut_cols)],
            'calibration_support_line_pixel': [[int(lut_rows[0]), int(lut_rows[-1])], [float(lut_cols[0]), float(lut_cols[-1])]],
            'lut_ranges': lut_ranges,
            'thermal_noise_correction_performed_in_source': annotation.findtext('.//thermalNoiseCorrectionPerformed')}


def main():
    folder = ROOT / 'docs/management'
    protocol_path = folder / 'cantarell_data_protocol_v1.json'
    protocol = json.loads(protocol_path.read_text())
    scenes_path = folder / 'cantarell_scenes_audit.json'
    if sha(scenes_path) != protocol['scenes_audit_sha256']:
        raise ValueError('Source identities changed since protocol freeze')
    scenes = json.loads(scenes_path.read_text())['results']
    results, errors = [], []
    with ThreadPoolExecutor(max_workers=3) as pool:
        pending = {pool.submit(inspect, scene): scene for scene in scenes}
        for future in as_completed(pending):
            scene = pending[future]
            try:
                results.append(future.result())
                print(f"Verified physical metadata {scene['group']}", flush=True)
            except Exception as exc:
                errors.append({'group': scene['group'], 'scene': scene['scene'], 'error': f'{type(exc).__name__}: {exc}'})
    results.sort(key=lambda r: r['group'])
    audit = {'protocol_sha256': sha(protocol_path), 'script_sha256': sha(Path(__file__)),
             'expected_scenes': len(scenes), 'verified_scenes': len(results),
             'complete': len(scenes) == len(results) and not errors, 'errors': errors, 'results': results,
             'limits': ['Metadata verification only; does not establish image registration or detection quality.',
                        'No thermal-noise correction has been added to the frozen preparation protocol.']}
    (folder / 'cantarell_physical_metadata_audit.json').write_text(json.dumps(audit, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k: audit[k] for k in ('expected_scenes', 'verified_scenes', 'complete', 'errors')}, indent=2))


if __name__ == '__main__':
    main()
