from collections import deque
from typing import Tuple, Optional
from algorithms.base import BasePageReplacement

class FIFOPageReplacement(BasePageReplacement):
    def __init__(self, num_frames: int):
        super().__init__(num_frames, name="FIFO")
        self.queue = deque()
        self.resident_set = set()

    def reset(self):
        super().reset()
        self.queue.clear()
        self.resident_set.clear()

    def access(self, page: int, timestamp: int, is_pre_shift: bool = True) -> Tuple[bool, Optional[int]]:
        if page in self.resident_set:

            return True, None

        evicted = None
        if len(self.frames) >= self.num_frames:

            evicted = self.queue.popleft()
            self.resident_set.remove(evicted)
            self.frames.remove(evicted)

        self.frames.append(page)
        self.queue.append(page)
        self.resident_set.add(page)
        return False, evicted
