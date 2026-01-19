from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from django.shortcuts import get_object_or_404

from .models import BatchRun, SpecimenMetric
from .serializers import BatchRunSerializer, SpecimenMetricSerializer, QcDecisionSerializer
from .services import compute_default_decisions, compute_run_status_control_only, apply_reviewer_decision
from .rules import Decision


class RunListAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        runs = BatchRun.objects.order_by("-created_at")[:100]
        return Response(BatchRunSerializer(runs, many=True).data)


class RunSpecimensAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, run_id: int):
        run = get_object_or_404(BatchRun, pk=run_id)
        specimens = run.specimens.all().order_by("case_id", "specimen_type")

        evaluated = compute_default_decisions(specimens)
        run_status = compute_run_status_control_only(specimens).value

        payload = {
            "run": BatchRunSerializer(run).data,
            "run_status": run_status,
            "specimens": [
                {
                    **SpecimenMetricSerializer(e.specimen).data,
                    "computed_decision": e.computed_decision.value,
                    "computed_reasons": e.reasons,
                }
                for e in evaluated
            ],
        }
        return Response(payload)


class SpecimenDetailAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk: int):
        specimen = get_object_or_404(SpecimenMetric.objects.select_related("run"), pk=pk)
        computed = compute_default_decisions([specimen])[0]
        latest = specimen.decisions.select_related("decided_by").first()

        payload = {
            "specimen": SpecimenMetricSerializer(specimen).data,
            "computed_decision": computed.computed_decision.value,
            "computed_reasons": computed.reasons,
            "latest_decision": QcDecisionSerializer(latest).data if latest else None,
        }
        return Response(payload)


class SpecimenDecisionsAPI(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk: int):
        specimen = get_object_or_404(SpecimenMetric, pk=pk)
        decisions = specimen.decisions.select_related("decided_by").all()[:50]
        return Response(QcDecisionSerializer(decisions, many=True).data)


class SubmitDecisionAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk: int):
        specimen = get_object_or_404(SpecimenMetric, pk=pk)

        decision_raw = (request.data.get("decision") or "").strip().upper()
        comment = (request.data.get("comment") or "").strip()

        try:
            decision = Decision(decision_raw)
        except Exception:
            return Response(
                {"error": "Invalid decision", "allowed": [d.value for d in Decision]},
                status=status.HTTP_400_BAD_REQUEST,
            )

        d = apply_reviewer_decision(specimen, request.user, decision, comment)
        return Response(QcDecisionSerializer(d).data, status=status.HTTP_201_CREATED)

