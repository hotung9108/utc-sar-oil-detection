"""Retrieve public metadata for one DARTIS-linked Sentinel-1 scene, without imagery."""
import hashlib
import json
import re
import urllib.error
import urllib.request
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main():
    manifest = json.loads((ROOT/'data/dartis/catalog_manifest.json').read_text(encoding='utf-8'))
    patch = sorted(manifest, key=lambda r:r['filename'])[0]
    scene = patch['scene_ids'][0].removesuffix('.SAFE')
    match = re.fullmatch(r'S1[AB]_IW_GRDH_1SDV_(\d{4})(\d{2})(\d{2})T\d{6}_[A-Z0-9_]+', scene)
    if not match:
        raise ValueError('Unsupported source scene naming')
    year, month, day = map(int,match.groups())
    base = f'https://roda.sentinel-hub.com/sentinel-s1-l1c/GRD/{year}/{month}/{day}/IW/DV/{scene}/'
    directory = ROOT/'data/sentinel_metadata'/scene
    directory.mkdir(parents=True,exist_ok=True)
    audit_path = ROOT/'docs/management/sentinel_metadata_audit.json'
    previous = json.loads(audit_path.read_text(encoding='utf-8')) if audit_path.exists() else {}
    evidence = {'scene':scene,'dartis_patch':patch['filename'],'base_url':base,'files':[],
                'image_downloaded':False,'wind_downloaded':False,
                'sos_scene_link_available':False,'patch_to_original_pixel_mapping_verified':False}

    def fetch(name):
        dest = directory/name
        url = base+name
        try:
            if dest.exists():
                raw = dest.read_bytes()
                prior = [f for f in previous.get('files',[]) if
                         f.get('file')==dest.relative_to(ROOT).as_posix() and
                         f.get('sha256')==hashlib.sha256(raw).hexdigest()]
                if prior:
                    url = prior[-1]['url']
                else:
                    raise ValueError('Cached metadata lacks matching source receipt')
            else:
                with urllib.request.urlopen(url,timeout=45) as response:
                    raw = response.read(15_000_001)
                if len(raw)>15_000_000: raise ValueError('Metadata exceeds 15 MB limit')
                dest.parent.mkdir(parents=True,exist_ok=True)
                dest.write_bytes(raw)
            evidence['files'].append({'file':dest.relative_to(ROOT).as_posix(),'url':url,
                'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
            return raw
        except (urllib.error.URLError, TimeoutError) as exc:
            evidence['files'].append({'url':url,'error':str(exc)})
            # Anonymous GET only: never enable Requester Pays or use credentials.
            if name.startswith('annotation/'):
                alternative = url.replace('https://roda.sentinel-hub.com/sentinel-s1-l1c/',
                                          'https://sentinel-s1-l1c.s3.amazonaws.com/')
                try:
                    with urllib.request.urlopen(alternative,timeout=45) as response:
                        raw = response.read(15_000_001)
                    if len(raw)>15_000_000: raise ValueError('Metadata exceeds 15 MB limit')
                    dest.parent.mkdir(parents=True,exist_ok=True)
                    dest.write_bytes(raw)
                    evidence['files'].append({'file':dest.relative_to(ROOT).as_posix(),
                        'url':alternative,'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
                    return raw
                except (urllib.error.URLError, TimeoutError) as fallback_error:
                    evidence['files'].append({'url':alternative,'error':str(fallback_error)})
            return None

    raw = fetch('productInfo.json')
    if raw is None: raise RuntimeError('Product information unavailable')
    product = json.loads(raw)
    assert product['id']==scene
    evidence['start_time'] = product['startTime']
    evidence['footprint'] = product['footprint']
    paths = ['annotation/iw-vv.xml','annotation/calibration/calibration-iw-vv.xml',
             'annotation/calibration/noise-iw-vv.xml']
    for name in paths:
        if name not in product['filenameMap'].values():
            raise ValueError('Asset is absent from publisher filename map')
        raw = fetch(name)
        if raw is None: continue
        tree = ET.fromstring(raw)
        if name == 'annotation/iw-vv.xml':
            assert tree.findtext('.//adsHeader/polarisation')=='VV'
            points = tree.findall('.//geolocationGridPoint')
            angles = [float(p.findtext('incidenceAngle')) for p in points]
            assert angles and all(0<a<90 for a in angles)
            evidence['incidence_grid'] = {'points':len(points),'min_degrees':min(angles),
                'max_degrees':max(angles),'sample':{key:points[0].findtext(key) for key in
                ['line','pixel','latitude','longitude','incidenceAngle','azimuthTime']}}
            evidence['original_image_dimensions'] = {key:int(tree.findtext('.//imageInformation/'+key))
                for key in ['numberOfLines','numberOfSamples']}
        elif 'calibration-' in name:
            evidence['calibration_vectors'] = len(tree.findall('.//calibrationVector'))
    output = ROOT/'docs/management/sentinel_metadata_audit.json'
    output.write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(evidence,ensure_ascii=True,indent=2))


if __name__=='__main__':
    main()
