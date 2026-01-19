from dataclasses import dataclass
from enum import Enum


class Decision(str, Enum):
    PASS = "PASS"
    FAIL = "FAIL"
    PENDING = "PENDING"
    NEEDS_REPEAT = "NEEDS_REPEAT"


@dataclass(frozen=True)
class Thresholds:
    min_mapped_reads: int
    max_contamination: float
    min_mean_coverage: float


DEFAULT_THRESHOLDS = {
    "NORMAL": Thresholds(min_mapped_reads=5_000_000, max_contamination=0.02, min_mean_coverage=80.0),
    "TUMOR": Thresholds(min_mapped_reads=8_000_000, max_contamination=0.05, min_mean_coverage=120.0),
    "CONTROL": Thresholds(min_mapped_reads=6_000_000, max_contamination=0.02, min_mean_coverage=100.0),
}


def evaluate_specimen(specimen_type: str, mapped_reads: int | None, contamination: float | None, mean_coverage: float | None):
    st = (specimen_type or "").upper().strip()
    thresholds = DEFAULT_THRESHOLDS.get(st)
    if thresholds is None:
        return (Decision.PENDING, [f"Unknown specimen_type '{specimen_type}'"])

    if mapped_reads is None or contamination is None or mean_coverage is None:
        missing = []
        if mapped_reads is None: missing.append("mapped_reads")
        if contamination is None: missing.append("contamination")
        if mean_coverage is None: missing.append("mean_coverage")
        return (Decision.PENDING, [f"Missing metrics: {', '.join(missing)}"])

    reasons = []
    if mapped_reads < thresholds.min_mapped_reads:
        reasons.append(f"Mapped reads below cutoff ({mapped_reads:,} < {thresholds.min_mapped_reads:,})")
    if contamination > thresholds.max_contamination:
        reasons.append(f"Contamination above cutoff ({contamination:.3f} > {thresholds.max_contamination:.3f})")
    if mean_coverage < thresholds.min_mean_coverage:
        reasons.append(f"Mean coverage below cutoff ({mean_coverage:.1f} < {thresholds.min_mean_coverage:.1f})")

    if reasons:
        if any("Mapped reads below cutoff" in r for r in reasons):
            return (Decision.NEEDS_REPEAT, reasons)
        return (Decision.FAIL, reasons)

    return (Decision.PASS, [])

