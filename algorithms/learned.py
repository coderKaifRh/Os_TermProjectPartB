from typing import List, Tuple, Optional, Dict
from algorithms.base import BasePageReplacement
from model.features import PageFeatureTracker
from model.decision_tree import LightweightDecisionTree

class LearnedPageReplacement(BasePageReplacement):

    def __init__(self, num_frames: int, model: LightweightDecisionTree):
        super().__init__(num_frames, name="Learned (Decision Tree)")
        self.model = model
        self.tracker = PageFeatureTracker(window_size=50)
        self.resident_set = set()
        self.last_decision_info: Optional[Dict] = None

    def reset(self):
        super().reset()
        self.tracker.reset()
        self.resident_set.clear()
        self.last_decision_info = None

    def access(self, page: int, timestamp: int, is_pre_shift: bool = True) -> Tuple[bool, Optional[int]]:
        self.last_decision_info = None

        if page in self.resident_set:
            self.tracker.on_access(page, timestamp, is_new_load=False)
            return True, None

        evicted = None
        if len(self.frames) >= self.num_frames:
            best_evict = None
            max_score = -float('inf')
            candidates_info = []

            for cand in self.frames:
                feats = self.tracker.extract_features(cand)
                score, rules = self.model.explain_one(feats, PageFeatureTracker.feature_names())
                candidates_info.append({
                    "page": cand,
                    "features": feats,
                    "score": score,
                    "rules": rules
                })

                if score > max_score:
                    max_score = score
                    best_evict = cand

            evicted = best_evict
            self.resident_set.remove(evicted)
            self.frames.remove(evicted)

            self.last_decision_info = {
                "timestamp": timestamp,
                "incoming_page": page,
                "evicted_page": evicted,
                "candidates": candidates_info,
                "max_score": max_score,
                "is_pre_shift": is_pre_shift
            }

        self.frames.append(page)
        self.resident_set.add(page)
        self.tracker.on_access(page, timestamp, is_new_load=True)
        return False, evicted

    @staticmethod
    def train_from_oracle(training_trace: List[int], num_frames: int) -> LightweightDecisionTree:
        tracker = PageFeatureTracker(window_size=50)
        frames: List[int] = []
        resident_set = set()
        X: List[List[float]] = []
        y: List[float] = []

        next_indices: Dict[int, List[int]] = {}
        for idx, p in enumerate(training_trace):
            if p not in next_indices:
                next_indices[p] = []
            next_indices[p].append(idx)

        for t, page in enumerate(training_trace):
            if page in resident_set:
                tracker.on_access(page, t, is_new_load=False)
                continue

            if len(frames) >= num_frames:
                for cand in frames:
                    feats = tracker.extract_features(cand)
                    occ = next_indices.get(cand, [])
                    next_t = next((idx for idx in occ if idx > t), float('inf'))
                    reuse_dist = min(next_t - t, 150.0) if next_t != float('inf') else 150.0
                    X.append(feats)
                    y.append(reuse_dist)

                farthest_t = -1
                evict_page = None
                for cand in frames:
                    occ = next_indices.get(cand, [])
                    next_t = next((idx for idx in occ if idx > t), float('inf'))
                    if next_t > farthest_t:
                        farthest_t = next_t
                        evict_page = cand

                frames.remove(evict_page)
                resident_set.remove(evict_page)

            frames.append(page)
            resident_set.add(page)
            tracker.on_access(page, t, is_new_load=True)

        model = LightweightDecisionTree(max_depth=4, min_samples_split=6)
        model.fit(X, y)
        return model
