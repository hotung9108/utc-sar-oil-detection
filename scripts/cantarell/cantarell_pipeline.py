"""Image-only inference for the frozen physical SAR supplement.

No ground-truth input, scene metadata lookup, fitting, or implicit model selection.
"""

import sys as _sys
from pathlib import Path as _Path
_project_root = _Path(__file__).resolve().parents[2]
_sys.path.insert(0, str(_project_root))
_sys.path.insert(0, str(_project_root / "src"))

import sys
import time
from pathlib import Path

import numpy as np
from scipy import ndimage

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from sar_oil import core, reference
from scripts.qposd.qposd_fast_features import features as grouped_features


def normalize_power(linear):
    log = 10*np.log10(np.maximum(linear,1e-12))
    low,high = np.percentile(log,[1,99])
    image = np.zeros(log.shape) if high-low<1e-12 else np.clip((log-low)/(high-low),0,1)
    return image,[float(low),float(high)]


def candidates(linear_power,config,backend='numpy'):
    if backend not in ('numpy','reference'):
        raise ValueError('Unknown image-operator backend')
    raw = np.asarray(linear_power,dtype=float)
    if raw.ndim!=2 or min(raw.shape)<2 or not np.all(np.isfinite(raw)) or np.any(raw<0):
        raise ValueError('Expected a finite nonnegative 2D linear-power image')
    ops = core if backend=='numpy' else reference
    start = time.perf_counter()
    params = config['filter']
    if params['name']=='mean':
        filtered = core.mean_filter(raw,params['size']) if backend=='numpy' else ndimage.uniform_filter(raw,size=params['size'],mode='mirror')
    else:
        filtered = ops.filter_image(raw,**params)
    image,bounds = normalize_power(filtered)
    dark = ops.threshold(image,**config['threshold'])
    mask = ops.postprocess(dark,**config['morphology'])
    labels = ops.label(mask)
    return {'filtered_linear':filtered,'image':image,'log_bounds':bounds,'candidate_mask':mask,
            'labels':labels,'seconds_single_run':time.perf_counter()-start}


def extract(image,labels,backend='numpy'):
    if backend=='numpy':
        X,ids = grouped_features(image,labels)
    elif backend=='reference':
        X,ids = reference.features(image,labels)
    else:
        raise ValueError('Unknown feature backend')
    if not np.isfinite(X).all() or X.shape!=(len(ids),8):
        raise ValueError('Invalid extracted region features')
    return X,ids


def infer(linear_power,config,model,backend='numpy'):
    start = time.perf_counter()
    result = candidates(linear_power,config,backend)
    X,ids = extract(result['image'],result['labels'],backend)
    scores = np.asarray(model.scores(X))
    if scores.shape!=(len(ids),) or not np.isfinite(scores).all():
        raise ValueError('Invalid model scores')
    keep = np.zeros(int(result['labels'].max())+1,dtype=bool)
    keep[ids] = scores>0
    result.update({'prediction':keep[result['labels']],'features':X,'region_ids':ids,
                   'scores':scores,'seconds_single_run':time.perf_counter()-start})
    return result
