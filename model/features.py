from collections import defaultdict, deque
from typing import List, Dict, Any

class PageFeatureTracker:

    def __init__(self, window_size: int = 50):
        self.window_size = window_size
        self.reset()

    def reset(self):
        self.current_time: int = 0
        self.last_access: Dict[int, int] = {}
        self.load_time: Dict[int, int] = {}
        self.access_counts: Dict[int, int] = defaultdict(int)
        self.access_history: Dict[int, List[int]] = defaultdict(list)
        self.sliding_window: deque = deque()

    def on_access(self, page: int, timestamp: int, is_new_load: bool = False):
        self.current_time = timestamp
        self.access_counts[page] += 1
        self.last_access[page] = timestamp
        self.access_history[page].append(timestamp)

        if is_new_load:
            self.load_time[page] = timestamp

        self.sliding_window.append(page)
        if len(self.sliding_window) > self.window_size:
            self.sliding_window.popleft()

    def extract_features(self, page: int) -> List[float]:

        recency = float(self.current_time - self.last_access.get(page, self.current_time))

        freq_window = float(sum(1 for p in self.sliding_window if p == page))

        freq_total = float(self.access_counts.get(page, 1))

        age = float(self.current_time - self.load_time.get(page, self.current_time))

        hist = self.access_history.get(page, [])
        if len(hist) >= 2:
            intervals = [hist[i] - hist[i - 1] for i in range(1, len(hist))]
            avg_interval = float(sum(intervals) / len(intervals))
        else:
            avg_interval = 100.0

        return [recency, freq_window, freq_total, age, avg_interval]

    @staticmethod
    def feature_names() -> List[str]:
        return ["recency", "freq_window", "freq_total", "resident_age", "avg_interval"]
