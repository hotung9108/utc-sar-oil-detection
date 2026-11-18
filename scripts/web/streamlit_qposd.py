"""QPOSD web adapter; image loading and inference never read reference masks."""

import sys as _sys
from pathlib import Path as _Path
_project_root = _Path(__file__).resolve().parents[2]
_sys.path.insert(0, str(_project_root))
_sys.path.insert(0, str(_project_root / "scripts"))

import hashlib
import io
import json
import sys
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image
from scipy.io import loadmat

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from scripts.qposd.extract_qposd_regions import display_normalize
from scripts.qposd.select_qposd_detection import frozen_classifier
from scripts.qposd.evaluate_qposd_test import frozen_detection
from scripts.qposd.qposd_pipeline import infer
from scripts.qposd.qposd_metrics import detection
from scripts.qposd.qposd_labels import decode_mask


def samples():
    protocol = json.loads((ROOT / 'results/qposd/protocol.json').read_text())
    return [n for n in protocol['splits']['test'] if (ROOT / f'data/lookalike_sources/qposd_features/image{n}.mat').exists()]


def load_image(number):
    if number not in samples():
        raise ValueError('Choose an available frozen QPOSD test sample')
    path = ROOT / f'data/lookalike_sources/qposd_features/image{number}.mat'
    expected = json.loads((ROOT / 'docs/management/qposd_matched_full_audit.json').read_text())
    row = next(r for r in expected['pairs'] if Path(r['member']).name == path.name)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    if digest != row['sha256']:
        raise ValueError('QPOSD image differs from verified input')
    matrix = loadmat(path, variable_names=['T'])['T']
    return matrix[:, :, 0].copy(), digest


def run_sample(number):
    raw, digest = load_image(number)
    model, model_record = frozen_classifier()
    protocol = json.loads((ROOT / 'results/qposd/protocol.json').read_text())
    config, config_record = frozen_detection(protocol, model_record)
    result = infer(raw, config, model)
    image, _ = display_normalize(raw)
    overlay = np.repeat(image[..., None], 3, axis=2)
    for label, color in [(1, [1, 0, 0]), (2, [0, 1, 0])]:
        mask = result['prediction'] == label
        overlay[mask] = .5 * overlay[mask] + .5 * np.array(color)
    result.update(image=image, overlay=overlay,
        metadata={'sample': number, 'image_sha256': digest, 'classifier': model_record,
                  'detector': config_record, 'ground_truth_used_for_inference': False,
                  'classes': {'0': 'background', '1': 'oil', '2': 'look_alike'},
                  'score_semantics': 'decision score, not probability',
                  'seconds_single_run': result['seconds_single_run'], 'regions': result['rows']})
    return result


def assess_sample(result):
    number = result['metadata']['sample']
    records = json.loads((ROOT / 'docs/management/qposd_mask_audit.json').read_text())
    row = next(r for r in records['masks'] if r['member'] == f'train_masks/mask{number}.png')
    path = ROOT / row['local_path']
    if hashlib.sha256(path.read_bytes()).hexdigest() != row['sha256']:
        raise ValueError('QPOSD reference mask changed')
    with Image.open(path) as image:
        truth = decode_mask(np.asarray(image.convert('RGB')))
    if truth.shape != result['prediction'].shape:
        raise ValueError('QPOSD mask shape differs; no automatic resizing')
    return {'metrics': detection(result['prediction'], truth), 'truth_sha256': row['sha256']}


def export_zip(result, evaluation=None):
    stream = io.BytesIO()
    with zipfile.ZipFile(stream, 'w', zipfile.ZIP_DEFLATED) as archive:
        for name, array in [('classes.png', result['prediction']),
                            ('overlay.png', np.clip(result['overlay']*255, 0, 255)),
                            ('candidates.png', result['candidate_mask']*255)]:
            output = io.BytesIO()
            Image.fromarray(array.astype('uint8')).save(output, format='PNG')
            archive.writestr(name, output.getvalue())
        metadata = dict(result['metadata'])
        if evaluation is not None:
            metadata['post_inference_evaluation'] = evaluation
        archive.writestr('regions.json', json.dumps(metadata, ensure_ascii=False, indent=2, allow_nan=False))
    return stream.getvalue()
