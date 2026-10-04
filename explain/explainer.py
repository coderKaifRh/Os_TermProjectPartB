import math
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional

@dataclass
class ExplanationRecord:
    timestamp: int
    incoming_page: int
    evicted_page: int
    oracle_best_page: int
    is_correct: bool
    confidence: float
    explanation: str
    phase: str

class EvictionExplainer:

    def __init__(self):
        self.records: List[ExplanationRecord] = []

    def explain_decision(self, decision_info: Dict, oracle_best_page: int) -> ExplanationRecord:
        timestamp = decision_info["timestamp"]
        incoming = decision_info["incoming_page"]
        evicted = decision_info["evicted_page"]
        candidates = decision_info["candidates"]
        is_pre_shift = decision_info["is_pre_shift"]
        phase_str = "Pre-Shift (Locality)" if is_pre_shift else "Post-Shift (Random/Bursty)"

        sorted_cands = sorted(candidates, key=lambda c: c["score"], reverse=True)
        top_cand = sorted_cands[0]
        runner_up_score = sorted_cands[1]["score"] if len(sorted_cands) > 1 else 0.0

        score_diff = max(0.0, top_cand["score"] - runner_up_score)
        confidence = 1.0 / (1.0 + math.exp(-score_diff / 15.0))
        confidence = max(0.52, min(0.96, confidence))

        is_correct = (evicted == oracle_best_page)

        feats = top_cand["features"]
        recency, freq_w, freq_tot, age, avg_interval = feats
        rules = top_cand["rules"]

        if freq_w == 0 and recency > 15:
            reason = (f"Evicted Page {evicted} (Recency={recency:.0f}, WindowFreq=0). "
                      f"Rationale: Page has been idle for {recency:.0f} cycles with zero accesses in the current "
                      f"window; identified as an inactive page. "
                      f"Active Rule: [{'; '.join(rules[:2]) if rules else 'High recency threshold'}].")
        elif recency > age * 0.6:
            reason = (f"Evicted Page {evicted} (Recency={recency:.0f}, Age={age:.0f}). "
                      f"Rationale: Page idle time consumes majority of its residency age ({recency/max(1,age)*100:.0f}%); "
                      f"predicted low reuse probability. "
                      f"Active Rule: [{rules[0] if rules else 'Age ratio'}]")
        else:
            reason = (f"Evicted Page {evicted} (Predicted Reuse Distance={top_cand['score']:.1f}). "
                      f"Rationale: Evaluated across {len(candidates)} resident pages; model predicted Page {evicted} "
                      f"has the longest time until next required reference.")

        record = ExplanationRecord(
            timestamp=timestamp,
            incoming_page=incoming,
            evicted_page=evicted,
            oracle_best_page=oracle_best_page,
            is_correct=is_correct,
            confidence=round(confidence, 3),
            explanation=reason,
            phase=phase_str
        )
        self.records.append(record)
        return record

    def compute_calibration(self) -> Dict[str, Dict[str, float]]:
        bins = {
            "Low Confidence [0.50 - 0.65)": {"total": 0, "correct": 0},
            "Medium Confidence [0.65 - 0.80)": {"total": 0, "correct": 0},
            "High Confidence [0.80 - 1.00]": {"total": 0, "correct": 0},
        }

        for rec in self.records:
            if rec.confidence < 0.65:
                b = "Low Confidence [0.50 - 0.65)"
            elif rec.confidence < 0.80:
                b = "Medium Confidence [0.65 - 0.80)"
            else:
                b = "High Confidence [0.80 - 1.00]"

            bins[b]["total"] += 1
            if rec.is_correct:
                bins[b]["correct"] += 1

        results = {}
        for b_name, data in bins.items():
            tot = data["total"]
            corr = data["correct"]
            acc = (corr / tot * 100.0) if tot > 0 else 0.0
            results[b_name] = {
                "total_decisions": tot,
                "correct_decisions": corr,
                "empirical_accuracy": acc
            }
        return results
