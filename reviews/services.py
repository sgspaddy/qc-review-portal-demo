from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone

from .models import QcDecision, SpecimenMetric, BatchRun
from .rules import evaluate_specimen, Decision


@dataclass(frozen=True)
class EvaluatedSpecimen:
    specimen: SpecimenMetric
    computed_decision: Decision
    reasons: list[str]


def compute_default_decisions(specimens: Iterable[SpecimenMetric]) -> list[EvaluatedSpecimen]:
    out: list[EvaluatedSpecimen] = []
    for s in specimens:
        d, reasons = evaluate_specimen(s.specimen_type, s.mapped_reads, s.contamination, s.mean_coverage)
        out.append(EvaluatedSpecimen(specimen=s, computed_decision=d, reasons=reasons))
    return out


def compute_run_status_control_only(specimens: Iterable[SpecimenMetric]) -> Decision:
    controls = [s for s in specimens if (s.specimen_type or "").upper() == "CONTROL"]
    if not controls:
        return Decision.PENDING

    eval_controls = compute_default_decisions(controls)
    if all(e.computed_decision == Decision.PASS for e in eval_controls):
        return Decision.PASS
    return Decision.FAIL


@transaction.atomic
def apply_reviewer_decision(specimen: SpecimenMetric, reviewer: User, decision: Decision, comment: str = "") -> QcDecision:
    return QcDecision.objects.create(
        specimen=specimen,
        decision=decision.value,
        comment=(comment or "").strip(),
        decided_by=reviewer,
        decided_at=timezone.now(),
    )


@transaction.atomic
def seed_demo_data() -> BatchRun:
    run = BatchRun.objects.create(run_id="DEMO-RUN-API-001", instrument="NextSeq 2000", run_group="InterviewDemo")

    SpecimenMetric.objects.create(
        run=run, case_id="CTRL-001", specimen_name="CTRL-001", specimen_type="CONTROL",
        source_filename="control_metrics.json", ingested_at=timezone.now(),
        mapped_reads=6_800_000, contamination=0.010, mean_coverage=110.0,
    )

    SpecimenMetric.objects.create(
        run=run, case_id="CASE-2001", specimen_name="N-CASE-2001", specimen_type="NORMAL",
        source_filename="case_2001_normal.json", ingested_at=timezone.now(),
        mapped_reads=6_100_000, contamination=0.012, mean_coverage=92.0,
    )
    SpecimenMetric.objects.create(
        run=run, case_id="CASE-2001", specimen_name="T-CASE-2001", specimen_type="TUMOR",
        source_filename="case_2001_tumor.json", ingested_at=timezone.now(),
        mapped_reads=3_000_000, contamination=0.020, mean_coverage=135.0,
    )

    return run

