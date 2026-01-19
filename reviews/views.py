from __future__ import annotations

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models import OuterRef, Subquery
from django.http import HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_GET, require_POST

from .forms import DecisionForm
from .models import BatchRun, SpecimenMetric, QcDecision
from .rules import Decision
from .services import (
    apply_reviewer_decision,
    compute_default_decisions,
    compute_run_status_control_only,
    seed_demo_data,
)


def _annotate_latest_decision(qs):
    latest = QcDecision.objects.filter(specimen=OuterRef("pk")).order_by("-decided_at")
    return qs.annotate(
        latest_decision=Subquery(latest.values("decision")[:1]),
        latest_decider=Subquery(latest.values("decided_by__username")[:1]),
        latest_decided_at=Subquery(latest.values("decided_at")[:1]),
    )


@require_GET
@login_required
def dashboard(request: HttpRequest) -> HttpResponse:
    q = (request.GET.get("q") or "").strip()
    run_id = (request.GET.get("run_id") or "").strip()
    specimen_type = (request.GET.get("specimen_type") or "").strip().upper()
    decision = (request.GET.get("decision") or "").strip().upper()

    qs = SpecimenMetric.objects.select_related("run")
    qs = _annotate_latest_decision(qs)

    if q:
        qs = qs.filter(case_id__icontains=q) | qs.filter(specimen_name__icontains=q) | qs.filter(run__run_id__icontains=q)

    if run_id:
        qs = qs.filter(run__run_id__icontains=run_id)
    if specimen_type:
        qs = qs.filter(specimen_type__iexact=specimen_type)
    if decision:
        qs = qs.filter(latest_decision__iexact=decision)

    qs = qs.order_by("-run__created_at", "case_id", "specimen_type")

    paginator = Paginator(qs, 25)
    page = paginator.get_page(request.GET.get("page") or 1)

    evaluated = compute_default_decisions(page.object_list)
    eval_by_id = {e.specimen.id: e for e in evaluated}

    run_ids = sorted({s.run_id for s in page.object_list})
    runs = BatchRun.objects.filter(id__in=run_ids)
    run_status_by_id = {r.id: compute_run_status_control_only(r.specimens.all()).value for r in runs}

    return render(
        request,
        "reviews/dashboard.html",
        {
            "page": page,
            "filters": {"q": q, "run_id": run_id, "specimen_type": specimen_type, "decision": decision},
            "eval_by_id": eval_by_id,
            "run_status_by_id": run_status_by_id,
            "DECISIONS": [d.value for d in Decision],
        },
    )


@require_GET
@login_required
def run_detail(request: HttpRequest, pk: int) -> HttpResponse:
    run = get_object_or_404(BatchRun, pk=pk)
    specimens = _annotate_latest_decision(run.specimens.select_related("run").all().order_by("case_id", "specimen_type"))

    evaluated = compute_default_decisions(specimens)
    eval_by_id = {e.specimen.id: e for e in evaluated}
    run_status = compute_run_status_control_only(specimens).value

    return render(
        request,
        "reviews/run_detail.html",
        {"run": run, "specimens": specimens, "eval_by_id": eval_by_id, "run_status": run_status},
    )


@require_GET
@login_required
def specimen_detail(request: HttpRequest, pk: int) -> HttpResponse:
    specimen = get_object_or_404(SpecimenMetric.objects.select_related("run"), pk=pk)
    computed = compute_default_decisions([specimen])[0]
    latest = specimen.decisions.select_related("decided_by").first()

    form = DecisionForm(initial={"decision": (latest.decision if latest else computed.computed_decision.value)})

    return render(
        request,
        "reviews/specimen_detail.html",
        {"specimen": specimen, "computed": computed, "latest": latest, "form": form},
    )


@require_POST
@login_required
def submit_decision(request: HttpRequest, pk: int) -> HttpResponse:
    specimen = get_object_or_404(SpecimenMetric, pk=pk)
    form = DecisionForm(request.POST)
    if not form.is_valid():
        messages.error(request, "Please correct the form errors.")
        return redirect("specimen_detail", pk=pk)

    decision = Decision(form.cleaned_data["decision"])
    comment = form.cleaned_data.get("comment", "")

    apply_reviewer_decision(specimen=specimen, reviewer=request.user, decision=decision, comment=comment)
    messages.success(request, f"Saved decision: {decision.value}")
    return redirect("specimen_detail", pk=pk)


@require_POST
@login_required
def seed_demo(request: HttpRequest) -> HttpResponse:
    if not SpecimenMetric.objects.exists():
        run = seed_demo_data()
        messages.success(request, f"Seeded demo data: {run.run_id}")
    else:
        messages.info(request, "Demo data already exists.")
    return redirect("dashboard")

