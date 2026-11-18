"""In-memory web adapter for the existing, frozen inference engine."""

import sys as _sys
from pathlib import Path as _Path
_project_root = _Path(__file__).resolve().parents[2]
_sys.path.insert(0, str(_project_root))
_sys.path.insert(0, str(_project_root / "scripts"))

import hashlib
import io
import json
import tempfile
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image

from scripts.desktop import demo_engine

ROOT = Path(__file__).resolve().parents[2]
MAX_UPLOAD = 16 * 1024 * 1024


def fingerprint(data, selection):
    path = Path(selection)
    config = json.loads(path.read_text(encoding='utf-8'))
    model = path.parent / config['model_file']
    return hashlib.sha256(data + path.read_bytes() + model.read_bytes()).hexdigest()


def infer_bytes(data, selection):
    if not data or len(data) > MAX_UPLOAD:
        raise ValueError('Ảnh phải có dữ liệu và không vượt quá 16 MB.')
    with tempfile.TemporaryDirectory(prefix='sar-web-') as tmp:
        path = Path(tmp) / 'input.png'
        path.write_bytes(data)
        result = demo_engine.infer(path, selection)
    result['metadata']['input_file'] = 'input.png'
    return result


def assess_bytes(result, data):
    if not data or len(data) > MAX_UPLOAD:
        raise ValueError('Mask phải có dữ liệu và không vượt quá 16 MB.')
    with tempfile.TemporaryDirectory(prefix='sar-truth-') as tmp:
        path = Path(tmp) / 'truth.png'
        path.write_bytes(data)
        metrics = demo_engine.assess(result, path)
    return {'metrics': metrics, 'truth_sha256': hashlib.sha256(data).hexdigest(),
            'truth_threshold': 128, 'matching': 'one-to-one object IoU >= 0.5'}


def download_zip(result, evaluation=None):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, 'w', zipfile.ZIP_DEFLATED) as archive:
        for key in ('image', 'filtered', 'candidates', 'mask', 'overlay'):
            image = io.BytesIO()
            Image.fromarray(np.clip(result[key] * 255, 0, 255).astype('uint8')).save(image, format='PNG')
            archive.writestr(f'{key}.png', image.getvalue())
        payload = dict(result['metadata'])
        if evaluation is not None:
            payload['post_inference_evaluation'] = evaluation
        archive.writestr('regions.json', json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False))
    return stream.getvalue()


def examples():
    manifest = ROOT / 'data/manifest.json'
    if not manifest.exists():
        return []
    records = json.loads(manifest.read_text(encoding='utf-8'))['records']
    return [r for r in records if r['split'] == 'test'
            and (ROOT / r['image']).is_file() and (ROOT / r['mask']).is_file()][:12]
