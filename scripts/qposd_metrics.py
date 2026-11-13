"""QPOSD raster-object metrics; separate class-aware and spatial matching."""
import numpy as np
from scipy.ndimage import label
from scipy.optimize import linear_sum_assignment

NAMES = ('oil', 'look_alike')


def ratio(numerator, denominator):
    return numerator / denominator if denominator else None


def binary_summary(tp, fp, fn):
    return {'tp': int(tp), 'fp': int(fp), 'fn': int(fn),
            'precision': ratio(tp, tp+fp), 'recall': ratio(tp, tp+fn),
            'f1': ratio(2*tp, 2*tp+fp+fn)}


def classification(truth, predicted):
    """Binary region labels: 1 oil, 0 look-alike; rows true, columns predicted."""
    truth, predicted = np.asarray(truth), np.asarray(predicted)
    if truth.ndim != 1 or truth.shape != predicted.shape:
        raise ValueError('Expected equal one-dimensional label arrays')
    if not np.isin(truth, [0, 1]).all() or not np.isin(predicted, [0, 1]).all():
        raise ValueError('Expected binary class IDs')
    cm = np.bincount((2*truth+predicted).astype(int), minlength=4).reshape(2, 2)
    scores = {}
    for value, name in ((1, 'oil'), (0, 'look_alike')):
        scores[name] = binary_summary(cm[value, value], cm[:, value].sum()-cm[value, value],
                                     cm[value, :].sum()-cm[value, value])
    f1 = [scores[name]['f1'] for name in NAMES]
    return {'class_order': ['look_alike', 'oil'], 'confusion_true_by_predicted': cm.tolist(),
            'classes': scores, 'macro_f1': float(np.mean(f1)) if all(v is not None for v in f1) else None,
            'oil_as_look_alike_rate': ratio(int(cm[1, 0]), int(cm[1].sum())),
            'look_alike_as_oil_rate': ratio(int(cm[0, 1]), int(cm[0].sum()))}


def objects(classes):
    ids = np.zeros(classes.shape, dtype=np.int32)
    categories = []
    for value in (1, 2):
        part, count = label(classes == value, np.ones((3, 3)))
        nonzero = part > 0
        ids[nonzero] = part[nonzero] + len(categories)
        categories.extend([value]*count)
    return ids, np.array(categories, dtype=int), np.bincount(ids.ravel())[1:]


def matches(iou, valid):
    """Maximize eligible pair count first, then summed IoU; no double matching."""
    if not iou.size:
        return np.empty(0, dtype=int), np.empty(0, dtype=int)
    weight = valid * (min(iou.shape)+1+iou)
    pi, gi = linear_sum_assignment(-weight)
    keep = valid[pi, gi]
    return pi[keep], gi[keep]


def detection(prediction, truth, iou_threshold=.5):
    """0 background, 1 oil, 2 look-alike; truth also permits 3 land/255 ignore.

    Ignore pixels are removed before component labeling, so they can split a
    region. This is an evaluation convention, never an inference operation.
    Sea and land are kept as negative reference pixels, not prediction masks.
    """
    prediction, truth = np.asarray(prediction), np.asarray(truth)
    if prediction.ndim != 2 or prediction.shape != truth.shape:
        raise ValueError('Expected equal two-dimensional class rasters')
    if not np.isin(prediction, [0, 1, 2]).all() or not np.isin(truth, [0, 1, 2, 3, 255]).all():
        raise ValueError('Unexpected class IDs')
    if not 0 < iou_threshold <= 1:
        raise ValueError('IoU threshold must be in (0,1]')
    p = np.where(truth == 255, 0, prediction)
    g = np.where(np.isin(truth, [1, 2]), truth, 0)
    pl, pc, pa = objects(p)
    gl, gc, ga = objects(g)
    npred, ngt = len(pc), len(gc)
    joint = np.bincount((pl*(ngt+1)+gl).ravel(), minlength=(npred+1)*(ngt+1))
    intersection = joint.reshape(npred+1, ngt+1)[1:, 1:]
    union = pa[:, None]+ga[None, :]-intersection
    iou = intersection/np.maximum(union, 1)
    eligible = iou >= iou_threshold
    pi, gi = matches(iou, eligible & (pc[:, None] == gc[None, :]))
    classes = {}
    for value, name in ((1, 'oil'), (2, 'look_alike')):
        tp = int((pc[pi] == value).sum())
        row = binary_summary(tp, int((pc == value).sum())-tp, int((gc == value).sum())-tp)
        for size_name, group in (('below_64', ga < 64), ('at_least_64', ga >= 64)):
            total = int(((gc == value) & group).sum())
            detected = int(((gc[gi] == value) & group[gi]).sum())
            row[size_name] = {'gt': total, 'tp': detected, 'recall': ratio(detected, total)}
        classes[name] = row
    spatial_p, spatial_g = matches(iou, eligible)
    cm = np.zeros((2, 2), dtype=int)
    np.add.at(cm, (gc[spatial_g]-1, pc[spatial_p]-1), 1)
    f1 = [classes[name]['f1'] for name in NAMES]
    return {'classes': classes,
            'macro_f1': float(np.mean(f1)) if all(v is not None for v in f1) else None,
            'ignored_pixels': int((truth == 255).sum()),
            'spatial_confusion': {
                'class_order': list(NAMES), 'true_by_predicted': cm.tolist(),
                'unmatched_truth': [int((gc == v).sum()-cm[v-1].sum()) for v in (1, 2)],
                'unmatched_predictions': [int((pc == v).sum()-cm[:, v-1].sum()) for v in (1, 2)],
                'scope': 'Class-agnostic spatial matching; different assignment from class-aware F1 may occur.'},
            'class_aware_matches': [{'predicted_id': int(p+1), 'truth_id': int(g+1),
                                     'iou': float(iou[p, g])} for p, g in zip(pi, gi)],
            'spatial_matches': [{'predicted_id': int(p+1), 'truth_id': int(g+1),
                                'predicted_class': int(pc[p]), 'truth_class': int(gc[g]),
                                'iou': float(iou[p, g])} for p, g in zip(spatial_p, spatial_g)]}


def summarize_detections(rows):
    """Pool object counts across images before computing class F1."""
    if not rows:
        raise ValueError('Cannot summarize an empty image population')
    classes = {}
    for name in NAMES:
        total = {k: sum(r['classes'][name][k] for r in rows) for k in ('tp', 'fp', 'fn')}
        result = binary_summary(**total)
        for size in ('below_64', 'at_least_64'):
            gt = sum(r['classes'][name][size]['gt'] for r in rows)
            tp = sum(r['classes'][name][size]['tp'] for r in rows)
            result[size] = {'gt': gt, 'tp': tp, 'recall': ratio(tp, gt)}
        classes[name] = result
    cm = np.sum([r['spatial_confusion']['true_by_predicted'] for r in rows], axis=0)
    f1 = [classes[name]['f1'] for name in NAMES]
    return {'images': len(rows), 'classes': classes,
            'macro_f1': float(np.mean(f1)) if all(v is not None for v in f1) else None,
            'ignored_pixels': sum(r['ignored_pixels'] for r in rows),
            'spatial_confusion': {
                'class_order': list(NAMES), 'true_by_predicted': cm.tolist(),
                'unmatched_truth': np.sum([r['spatial_confusion']['unmatched_truth'] for r in rows], axis=0).tolist(),
                'unmatched_predictions': np.sum([r['spatial_confusion']['unmatched_predictions'] for r in rows], axis=0).tolist(),
                'oil_as_look_alike_among_spatial_matches': ratio(int(cm[0, 1]), int(cm[0].sum())),
                'look_alike_as_oil_among_spatial_matches': ratio(int(cm[1, 0]), int(cm[1].sum())),
                'scope': 'Confusion rates condition on spatially matched objects; unmatched misses/false alarms are reported separately.'}}
