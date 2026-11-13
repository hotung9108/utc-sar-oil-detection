"""NumPy CART and linear squared-hinge SVM, with explicit convergence diagnostics."""

import json
from pathlib import Path

import numpy as np


class CART:
    def __init__(self, max_depth=5, min_leaf=5):
        self.max_depth = max_depth
        self.min_leaf = min_leaf

    def fit(self, X, y):
        X = np.asarray(X)
        y = np.asarray(y, dtype=int)
        if len(np.unique(y)) < 2:
            raise ValueError("Training requires both classes")

        def build(X, y, depth):
            n = len(y)
            positive = int(y.sum())
            node = {"score": positive / n}
            if depth >= self.max_depth or n < 2 * self.min_leaf or positive in (0, n):
                return node
            best_gain = 1e-12
            split = None
            impurity = 2 * positive * (n - positive) / n
            for f in range(X.shape[1]):
                order = np.argsort(X[:, f], kind="stable")
                v = X[order, f]
                ys = y[order]
                left = np.arange(1, n)
                lp = ys.cumsum()[:-1]
                right = n - left
                rp = positive - lp
                gain = impurity - 2 * lp * (left - lp) / left - 2 * rp * (right - rp) / right
                valid = (left >= self.min_leaf) & (right >= self.min_leaf) & (v[:-1] < v[1:])
                gain[~valid] = -np.inf
                j = int(np.argmax(gain))
                if gain[j] > best_gain:
                    best_gain = gain[j]
                    split = (f, float((v[j] + v[j + 1]) / 2))
            if split is None:
                return node
            f, t = split
            m = X[:, f] <= t
            node.update(
                feature=f,
                threshold=t,
                left=build(X[m], y[m], depth + 1),
                right=build(X[~m], y[~m], depth + 1),
            )
            return node

        self.tree = build(X, y, 0)
        self.converged = True
        return self

    def decision_function(self, X):
        def walk(row, node):
            while "feature" in node:
                node = node["left" if row[node["feature"]] <= node["threshold"] else "right"]
            return node["score"] - 0.5

        return np.array([walk(x, self.tree) for x in X])

    def predict(self, X):
        return (self.decision_function(X) > 0).astype(int)


class LinearSVM:
    def __init__(self, C=1.0, max_iter=10000, tol=1e-6):
        self.C = C
        self.max_iter = max_iter
        self.tol = tol

    def fit(self, X, y):
        if len(np.unique(y)) < 2:
            raise ValueError("Training requires both classes")
        X = np.asarray(X, float)
        target = 2 * np.asarray(y) - 1
        n = len(y)

        # Objective is sklearn's summed loss divided by n (same minimizer).
        def loss(w):
            z = np.maximum(1 - target * (X @ w), 0)
            return 0.5 * (w @ w) / n + self.C * (z @ z) / n

        w = np.zeros(X.shape[1])
        lipschitz = 1 / n + 2 * self.C * np.linalg.norm(X, ord=2) ** 2 / n
        step = 1 / lipschitz
        history = []
        self.converged = False
        # Accelerated gradient with restart and backtracking.
        z = w.copy()
        momentum = 1.0
        for iteration in range(self.max_iter):
            margin = np.maximum(1 - target * (X @ z), 0)
            grad = z / n - 2 * self.C * (X.T @ (target * margin)) / n
            base = loss(z)
            while True:
                next_w = z - step * grad
                delta = next_w - z
                current = loss(next_w)
                if current <= base + grad @ delta + (delta @ delta) / (2 * step) + 1e-14:
                    break
                step *= 0.5
            true_grad = (
                next_w / n
                - 2 * self.C * (X.T @ (target * np.maximum(1 - target * (X @ next_w), 0))) / n
            )
            if iteration % 50 == 0:
                history.append([iteration, float(current), float(np.max(np.abs(true_grad)))])
            if np.max(np.abs(true_grad)) <= self.tol:
                w = next_w
                self.converged = True
                break
            next_m = (1 + np.sqrt(1 + 4 * momentum * momentum)) / 2
            restart = (z - next_w) @ (next_w - w) > 0
            if restart:
                next_m = 1.0
            z = next_w if restart else next_w + (momentum - 1) / next_m * (next_w - w)
            w = next_w
            momentum = next_m
        self.w = w
        self.iterations = iteration + 1
        self.objective = float(loss(w))
        self.history = history
        self.gradient_max = float(np.max(np.abs(true_grad)))
        return self

    def decision_function(self, X):
        return np.asarray(X) @ self.w

    def predict(self, X):
        return (self.decision_function(X) > 0).astype(int)


class RegionModel:
    def __init__(self, kind="cart", columns=None, backend="numpy", **params):
        self.kind = kind
        self.columns = list(range(8)) if columns is None else list(columns)
        self.backend = backend
        self.params = params

    def transform(self, X):
        x = (np.asarray(X)[:, self.columns] - self.mean) / self.scale
        return np.column_stack([x, np.ones(len(x))]) if self.kind == "svm" else x

    def fit(self, X, y):
        if len(np.unique(y)) != 2 or not np.isin(y, [0, 1]).all():
            raise ValueError("Training requires binary labels 0 and 1")
        self.mean = np.mean(X[:, self.columns], axis=0)
        self.scale = np.std(X[:, self.columns], axis=0)
        self.scale[self.scale < 1e-12] = 1
        if self.backend == "reference":
            from sklearn.svm import LinearSVC
            from sklearn.tree import DecisionTreeClassifier

            self.estimator = (
                DecisionTreeClassifier(
                    max_depth=self.params["max_depth"],
                    min_samples_leaf=self.params["min_leaf"],
                    random_state=2026,
                )
                if self.kind == "cart"
                else LinearSVC(
                    C=self.params["C"],
                    loss="squared_hinge",
                    penalty="l2",
                    dual=False,
                    fit_intercept=False,
                    tol=1e-9,
                    max_iter=10000,
                )
            )
        else:
            self.estimator = (
                CART(**self.params) if self.kind == "cart" else LinearSVM(**self.params)
            )
        self.estimator.fit(self.transform(X), y)
        self.converged = getattr(self.estimator, "converged", True)
        return self

    def scores(self, X):
        if len(X) == 0:
            return np.empty(0)
        x = self.transform(X)
        if self.backend == "reference" and self.kind == "cart":
            return self.estimator.predict_proba(x)[:, 1] - 0.5
        return self.estimator.decision_function(x)

    def predict(self, X):
        return (self.scores(X) > 0).astype(int)

    def save(self, path):
        if self.backend != "numpy":
            raise ValueError("Only NumPy models have portable JSON serialization")
        state = {
            "kind": self.kind,
            "columns": self.columns,
            "params": self.params,
            "mean": self.mean.tolist(),
            "scale": self.scale.tolist(),
            "converged": self.converged,
        }
        state["tree" if self.kind == "cart" else "w"] = (
            self.estimator.tree if self.kind == "cart" else self.estimator.w.tolist()
        )
        Path(path).write_text(json.dumps(state, indent=2), encoding="utf-8")

    @classmethod
    def load(cls, path):
        state = json.loads(Path(path).read_text(encoding="utf-8"))
        obj = cls(state["kind"], state["columns"], **state["params"])
        obj.mean = np.array(state["mean"])
        obj.scale = np.array(state["scale"])
        obj.converged = state["converged"]
        obj.estimator = CART(**obj.params) if obj.kind == "cart" else LinearSVM(**obj.params)
        if obj.kind == "cart":
            obj.estimator.tree = state["tree"]
        else:
            obj.estimator.w = np.array(state["w"])
        return obj
