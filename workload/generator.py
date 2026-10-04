import random
from typing import List, Tuple, Dict

class WorkloadGenerator:

    def __init__(self,
                 num_pages: int = 40,
                 total_accesses: int = 2000,
                 shift_ratio: float = 0.5,
                 seed: int = 42):
        self.num_pages = num_pages
        self.total_accesses = total_accesses
        self.shift_point = int(total_accesses * shift_ratio)
        self.seed = seed

    def generate_trace(self) -> Tuple[List[int], int]:

        rng = random.Random(self.seed)
        trace: List[int] = []

        hot_pages = list(range(0, min(8, self.num_pages)))
        cold_pages = list(range(len(hot_pages), self.num_pages))
        sequential_blocks = [
            list(range(8, min(14, self.num_pages))),
            list(range(14, min(20, self.num_pages)))
        ]

        i = 0
        while i < self.shift_point:
            pattern_type = rng.random()

            if pattern_type < 0.70:

                trace.append(rng.choice(hot_pages))
                i += 1
            elif pattern_type < 0.90:

                seq_block = rng.choice(sequential_blocks) if sequential_blocks else hot_pages
                loop_repeats = rng.randint(2, 4)
                for _ in range(loop_repeats):
                    for p in seq_block:
                        if i < self.shift_point:
                            trace.append(p)
                            i += 1
            else:

                if cold_pages:
                    trace.append(rng.choice(cold_pages))
                else:
                    trace.append(rng.choice(hot_pages))
                i += 1

        while i < self.total_accesses:
            pattern_type = rng.random()

            if pattern_type < 0.60:

                trace.append(rng.randint(0, self.num_pages - 1))
                i += 1
            else:

                scan_start = rng.randint(0, max(0, self.num_pages - 10))
                scan_len = rng.randint(6, 12)
                for step in range(scan_len):
                    if i < self.total_accesses:
                        trace.append((scan_start + step) % self.num_pages)
                        i += 1

        return trace, self.shift_point
