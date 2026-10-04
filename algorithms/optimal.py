from typing import List, Tuple, Optional, Dict
from collections import defaultdict
from algorithms.base import BasePageReplacement

class OptimalPageReplacement(BasePageReplacement):

    def __init__(self, num_frames: int, full_trace: List[int]):
        super().__init__(num_frames, name="Optimal (Belady)")
        self.full_trace = full_trace
        self.resident_set = set()

        self.future_occurrences: Dict[int, List[int]] = defaultdict(list)
        for idx, page in enumerate(self.full_trace):
            self.future_occurrences[page].append(idx)

        self.curr_ptr: Dict[int, int] = defaultdict(int)

    def reset(self):
        super().reset()
        self.resident_set.clear()
        self.curr_ptr.clear()

    def _next_use(self, page: int, current_time: int) -> int:

        occ = self.future_occurrences[page]
        ptr = self.curr_ptr[page]
        while ptr < len(occ) and occ[ptr] <= current_time:
            ptr += 1
        self.curr_ptr[page] = ptr

        if ptr < len(occ):
            return occ[ptr]
        return float('inf')

    def access(self, page: int, timestamp: int, is_pre_shift: bool = True) -> Tuple[bool, Optional[int]]:

        self._next_use(page, timestamp)

        if page in self.resident_set:
            return True, None

        evicted = None
        if len(self.frames) >= self.num_frames:

            farthest_time = -1
            best_evict = None

            for resident_page in self.frames:
                next_time = self._next_use(resident_page, timestamp)
                if next_time > farthest_time:
                    farthest_time = next_time
                    best_evict = resident_page

                if farthest_time == float('inf'):
                    break

            evicted = best_evict
            self.resident_set.remove(evicted)
            self.frames.remove(evicted)

        self.frames.append(page)
        self.resident_set.add(page)
        return False, evicted
