from rest_framework import serializers
from .models import BatchRun, SpecimenMetric, QcDecision


class BatchRunSerializer(serializers.ModelSerializer):
    class Meta:
        model = BatchRun
        fields = ["id", "run_id", "instrument", "run_group", "created_at"]


class SpecimenMetricSerializer(serializers.ModelSerializer):
    run = BatchRunSerializer(read_only=True)

    class Meta:
        model = SpecimenMetric
        fields = [
            "id", "run", "case_id", "specimen_name", "specimen_type",
            "source_filename", "ingested_at",
            "mapped_reads", "contamination", "mean_coverage",
            "created_at",
        ]


class QcDecisionSerializer(serializers.ModelSerializer):
    decided_by = serializers.CharField(source="decided_by.username", read_only=True)

    class Meta:
        model = QcDecision
        fields = ["id", "specimen", "decision", "comment", "decided_by", "decided_at"]

