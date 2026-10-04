import math
from typing import List, Optional, Tuple, Dict, Any

class DecisionTreeNode:
    def __init__(self,
                 feature_idx: Optional[int] = None,
                 threshold: Optional[float] = None,
                 left: Optional['DecisionTreeNode'] = None,
                 right: Optional['DecisionTreeNode'] = None,
                 value: Optional[float] = None,
                 samples: int = 0):
        self.feature_idx = feature_idx
        self.threshold = threshold
        self.left = left
        self.right = right
        self.value = value
        self.samples = samples

    @property
    def is_leaf(self) -> bool:
        return self.value is not None

class LightweightDecisionTree:

    def __init__(self, max_depth: int = 4, min_samples_split: int = 4):
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.root: Optional[DecisionTreeNode] = None
        self.feature_importances: List[float] = [0.0] * 5

    def fit(self, X: List[List[float]], y: List[float]):
        if not X or not y:
            return
        num_features = len(X[0])
        self.feature_importances = [0.0] * num_features
        self.root = self._build_tree(X, y, depth=0)

        total_imp = sum(self.feature_importances)
        if total_imp > 0:
            self.feature_importances = [imp / total_imp for imp in self.feature_importances]

    def _variance(self, y: List[float]) -> float:
        n = len(y)
        if n <= 1:
            return 0.0
        mean = sum(y) / n
        return sum((val - mean) ** 2 for val in y) / n

    def _build_tree(self, X: List[List[float]], y: List[float], depth: int) -> DecisionTreeNode:
        n_samples = len(y)
        current_mean = sum(y) / n_samples

        if depth >= self.max_depth or n_samples < self.min_samples_split:
            return DecisionTreeNode(value=current_mean, samples=n_samples)

        best_feature = None
        best_threshold = None
        best_mse = float('inf')
        best_left_idx = None
        best_right_idx = None

        current_var = self._variance(y)
        num_features = len(X[0])

        for f_idx in range(num_features):
            values = sorted(list(set(row[f_idx] for row in X)))
            if len(values) <= 1:
                continue

            for i in range(len(values) - 1):
                thresh = (values[i] + values[i + 1]) / 2.0
                left_idx = [idx for idx, row in enumerate(X) if row[f_idx] <= thresh]
                right_idx = [idx for idx, row in enumerate(X) if row[f_idx] > thresh]

                if not left_idx or not right_idx:
                    continue

                left_y = [y[idx] for idx in left_idx]
                right_y = [y[idx] for idx in right_idx]

                weighted_var = (len(left_y) * self._variance(left_y) + len(right_y) * self._variance(right_y)) / n_samples
                if weighted_var < best_mse:
                    best_mse = weighted_var
                    best_feature = f_idx
                    best_threshold = thresh
                    best_left_idx = left_idx
                    best_right_idx = right_idx

        if best_feature is None or best_mse >= current_var:
            return DecisionTreeNode(value=current_mean, samples=n_samples)

        reduction = (current_var - best_mse) * n_samples
        self.feature_importances[best_feature] += reduction

        left_child = self._build_tree([X[i] for i in best_left_idx], [y[i] for i in best_left_idx], depth + 1)
        right_child = self._build_tree([X[i] for i in best_right_idx], [y[i] for i in best_right_idx], depth + 1)

        return DecisionTreeNode(
            feature_idx=best_feature,
            threshold=best_threshold,
            left=left_child,
            right=right_child,
            samples=n_samples
        )

    def predict_one(self, x: List[float]) -> float:
        node = self.root
        if node is None:
            return 0.0
        while not node.is_leaf:
            if x[node.feature_idx] <= node.threshold:
                node = node.left
            else:
                node = node.right
        return node.value

    def explain_one(self, x: List[float], feature_names: List[str]) -> Tuple[float, List[str]]:

        node = self.root
        rules = []
        if node is None:
            return 0.0, rules

        while not node.is_leaf:
            fname = feature_names[node.feature_idx]
            val = x[node.feature_idx]
            thresh = node.threshold
            if val <= thresh:
                rules.append(f"{fname}={val:.1f} <= {thresh:.1f}")
                node = node.left
            else:
                rules.append(f"{fname}={val:.1f} > {thresh:.1f}")
                node = node.right

        return node.value, rules
