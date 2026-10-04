from collections import OrderedDict
from typing import Tuple, Optional
from algorithms.base import BasePageReplacement

class LRUPageReplacement(BasePageReplacement):
    def __init__(self, num_frames: int):
        super().__init__(num_frames, name="LRU")

        self.page_order = OrderedDict()

    def reset(self):
        super().reset()
        self.page_order.clear()

    def access(self, page: int, timestamp: int, is_pre_shift: bool = True) -> Tuple[bool, Optional[int]]:
        if page in self.page_order:

            self.page_order.move_to_end(page)
            return True, None

        evicted = None
        if len(self.frames) >= self.num_frames:

            evicted, _ = self.page_order.popitem(last=False)
            self.frames.remove(evicted)

        self.page_order[page] = timestamp
        self.frames.append(page)
        return False, evicted
