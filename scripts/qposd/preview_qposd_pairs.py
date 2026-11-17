"""Render selected local QPOSD pairs without resizing their source arrays."""

import sys as _sys
from pathlib import Path as _Path
_project_root = _Path(__file__).resolve().parents[2]
_sys.path.insert(0, str(_project_root))
_sys.path.insert(0, str(_project_root / "src"))

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from PIL import Image
from scipy.io import loadmat

from scripts.qposd.qposd_labels import decode_mask

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--numbers', type=int, nargs='+', required=True)
    args = parser.parse_args()
    masks = json.loads((ROOT/'docs/management/qposd_mask_audit.json').read_text(encoding='utf-8'))
    shapes = json.loads((ROOT/'docs/management/qposd_shape_audit.json').read_text(encoding='utf-8'))
    output = ROOT/'.cache/qposd/pair_previews'
    output.mkdir(parents=True, exist_ok=True)
    rows = []
    for number in args.numbers:
        path = ROOT/f'data/lookalike_sources/qposd_features/image{number}.mat'
        raw = path.read_bytes()
        header = next(p for p in shapes['pairs'] if p['number'] == number)
        if hashlib.sha256(raw[:header['prefix_bytes']]).hexdigest() != header['prefix_sha256']:
            raise ValueError(f'Published prefix mismatch: {number}')
        T = loadmat(path, variable_names=['T'])['T']
        record = next(m for m in masks['masks'] if m['member'] == f'train_masks/mask{number}.png')
        mask_path = ROOT/record['local_path']
        if hashlib.sha256(mask_path.read_bytes()).hexdigest() != record['sha256']:
            raise ValueError('Mask hash mismatch')
        with Image.open(mask_path) as image:
            rgb = np.asarray(image.convert('RGB'))
        labels = decode_mask(rgb)
        if T.shape != (*labels.shape, 9) or not np.isfinite(T).all():
            raise ValueError(f'Ineligible dimensions or nonfinite values: {number}')
        visible = 10*np.log10(np.maximum(T[:, :, 0], 1e-12))
        low, high = np.percentile(visible, [1, 99])
        fig, axes = plt.subplots(1, 3, figsize=(15, 5), layout='constrained')
        axes[0].imshow(visible, cmap='gray', vmin=low, vmax=high)
        axes[1].imshow(rgb, interpolation='nearest')
        axes[2].imshow(visible, cmap='gray', vmin=low, vmax=high)
        for value, color in ((1, 'red'), (2, 'lime'), (3, 'yellow')):
            binary = labels == value
            if binary.any() and not binary.all():
                axes[2].contour(binary, levels=[0.5], colors=[color], linewidths=0.6)
        for ax, title in zip(axes, ('T11: display log, 1-99% limits',
                                    'Original RGB reference', 'Reference boundaries over T11')):
            ax.set_title(title)
        fig.suptitle(f'QPOSD {number} | {labels.shape} | red: oil; green: look-alike; yellow: land boundary')
        target = output/f'pair{number}.png'
        fig.savefig(target, dpi=120)
        plt.close(fig)
        rows.append({'number': number, 'mat_sha256': hashlib.sha256(raw).hexdigest(),
                     'mask_sha256': record['sha256'], 'shape': list(T.shape),
                     'published_prefix_matches': True,
                     'display_db_limits': [float(low), float(high)],
                     'png_path': target.relative_to(ROOT).as_posix(),
                     'png_sha256': hashlib.sha256(target.read_bytes()).hexdigest()})
    receipt = output/('receipt_' + '_'.join(map(str, args.numbers)) + '.json')
    receipt.write_text(json.dumps({'pairs': rows, 'scope': 'Visual preview only; '
                      'no quantitative registration, classification, or physical calibration.'},
                      indent=2) + '\n', encoding='utf-8')
    print(receipt)


if __name__ == '__main__':
    main()
