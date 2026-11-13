"""Inference accepts only an image; ground truth is never an input."""

import numpy as np

from . import core, reference


def candidates(image, config, backend="numpy"):
    alg = core if backend == "numpy" else reference
    filtered = alg.filter_image(image, **config["filter"])
    binary = alg.threshold(filtered, **config["threshold"])
    mask = alg.postprocess(binary, **config.get("morphology", {}))
    return filtered, alg.label(mask)


def predict(image, config, model=None, backend="numpy"):
    filtered, labels = candidates(image, config, backend)
    alg = core if backend == "numpy" else reference
    X, ids = alg.features(filtered, labels)
    scores = model.scores(X) if model is not None else np.ones(len(ids))
    keep = np.zeros(int(labels.max()) + 1, bool)
    keep[ids] = scores > 0
    regions = [
        {
            "id": i,
            "features": dict(zip(core.FEATURES, x.tolist())),
            "score": float(s),
            "oil": bool(s > 0),
        }
        for i, x, s in zip(ids, X, scores)
    ]
    return keep[labels], regions
