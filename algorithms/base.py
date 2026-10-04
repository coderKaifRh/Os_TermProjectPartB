from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Tuple, Dict, Any

@dataclass
class PageAccessEvent:
    timestamp: int
    page: int
    hit: bool
    evicted_page: Optional[int]
    resident_pages: List[int]
    is_pre_shift: bool

@dataclass
class PhaseMetrics:
    total_accesses: int = 0
    hits: int = 0
    faults: int = 0

    @property
    def hit_ratio(self) -> float:
        return (self.hits / self.total_accesses) * 100.0 if self.total_accesses > 0 else 0.0

    @property
    def fault_ratio(self) -> float:
        return (self.faults / self.total_accesses) * 100.0 if self.total_accesses > 0 else 0.0

@dataclass
class SimulationResult:
    policy_name: str
    num_frames: int
    total_metrics: PhaseMetrics = field(default_factory=PhaseMetrics)
    pre_shift_metrics: PhaseMetrics = field(default_factory=PhaseMetrics)
    post_shift_metrics: PhaseMetrics = field(default_factory=PhaseMetrics)
    events: List[PageAccessEvent] = field(default_factory=list)
    hit_ratio_series: List[float] = field(default_factory=list)

    def record_access(self, page: int, timestamp: int, hit: bool, evicted: Optional[int],
                      resident: List[int], is_pre_shift: bool):

        self.total_metrics.total_accesses += 1
        if hit:
            self.total_metrics.hits += 1
        else:
            self.total_metrics.faults += 1

        target_phase = self.pre_shift_metrics if is_pre_shift else self.post_shift_metrics
        target_phase.total_accesses += 1
        if hit:
            target_phase.hits += 1
        else:
            target_phase.faults += 1

        event = PageAccessEvent(
            timestamp=timestamp,
            page=page,
            hit=hit,
            evicted_page=evicted,
            resident_pages=list(resident),
            is_pre_shift=is_pre_shift
        )
        self.events.append(event)
        self.hit_ratio_series.append(self.total_metrics.hit_ratio)

class BasePageReplacement(ABC):

    def __init__(self, num_frames: int, name: str):
        if num_frames <= 0:
            raise ValueError("Number of frames must be positive")
        self.num_frames = num_frames
        self.name = name
        self.frames: List[int] = []

    @abstractmethod
    def access(self, page: int, timestamp: int, is_pre_shift: bool = True) -> Tuple[bool, Optional[int]]:

        pass

    def reset(self):
        self.frames = []

    def get_resident_pages(self) -> List[int]:
        return list(self.frames)
