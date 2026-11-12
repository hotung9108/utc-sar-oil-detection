"""Object matching: maximum cardinality, then maximum IoU, at IoU >= .5."""

import numpy as np
from scipy.optimize import linear_sum_assignment

from .reference import label


def counts(prediction, truth, iou_threshold=0.5):
    p, g = label(prediction), label(truth)
    npred, ngt = int(p.max()), int(g.max())
    joint = np.bincount((p * (ngt + 1) + g).ravel(), minlength=(npred + 1) * (ngt + 1)).reshape(
        npred + 1, ngt + 1
    )
    pa = np.bincount(p.ravel(), minlength=npred + 1)[1:]
    ga = np.bincount(g.ravel(), minlength=ngt + 1)[1:]
    intersection = joint[1:, 1:]
    union = pa[:, None] + ga[None, :] - intersection
    iou = intersection / np.maximum(union, 1)
    valid = iou >= iou_threshold
    pi, gi = linear_sum_assignment(-(valid * (min(npred, ngt) + 1) + iou * valid))
    matched = valid[pi, gi]
    tp = int(matched.sum())
    border = np.unique(np.concatenate([g[0], g[-1], g[:, 0], g[:, -1]]))
    border = border[border > 0]
    border_tp = int(np.isin(gi[matched] + 1, border).sum())
    return {
        "tp": tp,
        "fp": npred - tp,
        "fn": ngt - tp,
        "images": 1,
        "empty_images": int(ngt == 0),
        "intersection": int((prediction & truth).sum()),
        "union": int((prediction | truth).sum()),
        "predicted_pixels": int(prediction.sum()),
        "truth_pixels": int(truth.sum()),
        "edge_gt": len(border),
        "edge_tp": border_tp,
        "interior_gt": ngt - len(border),
        "interior_tp": tp - border_tp,
    }


def summarize(rows):
    total = {key: sum(r[key] for r in rows) for key in rows[0]} if rows else {}

    def ratio(a, b):
        return a / b if b else None

    if not total:
        return total
    t = total
    return dict(
        t,
        precision=ratio(t["tp"], t["tp"] + t["fp"]),
        recall=ratio(t["tp"], t["tp"] + t["fn"]),
        f1=ratio(2 * t["tp"], 2 * t["tp"] + t["fp"] + t["fn"]),
        pixel_iou=ratio(t["intersection"], t["union"]),
        dice=ratio(2 * t["intersection"], t["predicted_pixels"] + t["truth_pixels"]),
        fp_per_image=ratio(t["fp"], t["images"]),
        edge_recall=ratio(t["edge_tp"], t["edge_gt"]),
        interior_recall=ratio(t["interior_tp"], t["interior_gt"]),
    )


def region_geometry(labels, truth):
    """Cache sufficient statistics. Dropping disconnected regions cannot merge objects."""
    g = label(truth)
    ngt = int(g.max())
    npred = int(labels.max())
    intersections = np.bincount(
        (labels * (ngt + 1) + g).ravel(), minlength=(npred + 1) * (ngt + 1)
    ).reshape(npred + 1, ngt + 1)[1:, 1:]
    pa = np.bincount(labels.ravel(), minlength=npred + 1)[1:]
    ga = np.bincount(g.ravel(), minlength=ngt + 1)[1:]
    border = np.unique(np.r_[g[0], g[-1], g[:, 0], g[:, -1]])
    border = border[border > 0]
    return intersections, pa, ga, border


def region_counts(geometry, keep):
    inter, pa, ga, border = geometry
    inter = inter[keep]
    pa = pa[keep]
    npred, ngt = len(pa), len(ga)
    iou = inter / np.maximum(pa[:, None] + ga[None, :] - inter, 1)
    valid = iou >= 0.5
    pi, gi = linear_sum_assignment(-(valid * (min(npred, ngt) + 1) + iou * valid))
    matched = valid[pi, gi]
    tp = int(matched.sum())
    edge_tp = int(np.isin(gi[matched] + 1, border).sum())
    intersection = int(inter.sum())
    predicted = int(pa.sum())
    truth = int(ga.sum())
    return {
        "tp": tp,
        "fp": npred - tp,
        "fn": ngt - tp,
        "images": 1,
        "empty_images": int(ngt == 0),
        "intersection": intersection,
        "union": predicted + truth - intersection,
        "predicted_pixels": predicted,
        "truth_pixels": truth,
        "edge_gt": len(border),
        "edge_tp": edge_tp,
        "interior_gt": ngt - len(border),
        "interior_tp": tp - edge_tp,
    }
