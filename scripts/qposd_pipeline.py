"""Image-only QPOSD inference. Reference masks are not accepted by this API."""
import time
import numpy as np

from extract_qposd_regions import display_normalize
from sar_oil import core, reference


def infer(linear_t11, config, model, backend='numpy'):
    if backend not in ('numpy', 'reference'):
        raise ValueError('Unknown backend')
    raw = np.asarray(linear_t11, dtype=float)
    if raw.ndim != 2 or min(raw.shape) < 2 or not np.isfinite(raw).all() or np.any(raw < 0):
        raise ValueError('Expected finite nonnegative 2D linear T11')
    if config['morphology'] != 'none':
        raise ValueError('Frozen QPOSD protocol permits no morphology')
    ops = core if backend == 'numpy' else reference
    start = time.perf_counter()
    feature_linear = ops.filter_image(raw, 'lee', size=7, looks=4)
    feature_image, feature_bounds = display_normalize(feature_linear)
    candidate_linear = (feature_linear if config['filter'] == 'lee' and config['size'] == 7
                        and config['looks'] == 4 else
                        ops.filter_image(raw, config['filter'], size=config['size'], looks=config['looks']))
    candidate_image, candidate_bounds = display_normalize(candidate_linear)
    dark = ops.threshold(candidate_image, **config['threshold'])
    kept = ops.postprocess(dark, operation='none', min_area=config['min_area'])
    labels = ops.label(kept)
    X, ids = ops.features(feature_image, labels)
    scores = model.scores(X)
    if len(scores) != len(ids) or not np.isfinite(X).all() or not np.isfinite(scores).all():
        raise ValueError('Invalid features or scores')
    classes = np.zeros(int(labels.max())+1, dtype=np.uint8)
    classes[ids] = np.where(scores > 0, 1, 2)
    prediction = classes[labels]
    areas = np.bincount(labels.ravel())
    return {'prediction': prediction, 'candidate_mask': kept,
            'feature_image': feature_image,
            'rows': [{'region_id': int(i), 'area': int(areas[i]),
                      'features': X[j].tolist(), 'score': float(scores[j]),
                      'predicted_class': int(classes[i])} for j, i in enumerate(ids)],
            'feature_log_bounds': feature_bounds, 'candidate_log_bounds': candidate_bounds,
            'seconds_single_run': time.perf_counter()-start}
