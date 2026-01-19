from django.db import models
from django.contrib.auth.models import User


class BatchRun(models.Model):
    run_id = models.CharField(max_length=80, unique=True)
    instrument = models.CharField(max_length=120, blank=True, default="")
    run_group = models.CharField(max_length=80, blank=True, default="")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return self.run_id


class SpecimenMetric(models.Model):
    SPECIMEN_TYPES = [
        ("NORMAL", "Normal"),
        ("TUMOR", "Tumor"),
        ("CONTROL", "Control"),
    ]

    run = models.ForeignKey(BatchRun, on_delete=models.CASCADE, related_name="specimens")

    case_id = models.CharField(max_length=80)
    specimen_name = models.CharField(max_length=120)
    specimen_type = models.CharField(max_length=20, choices=SPECIMEN_TYPES)

    source_filename = models.CharField(max_length=255, blank=True, default="")
    ingested_at = models.DateTimeField(null=True, blank=True)

    mapped_reads = models.IntegerField(null=True, blank=True)
    contamination = models.FloatField(null=True, blank=True)
    mean_coverage = models.FloatField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=["case_id"]),
            models.Index(fields=["specimen_type"]),
        ]

    def __str__(self) -> str:
        return f"{self.case_id} - {self.specimen_name} ({self.specimen_type})"


class QcDecision(models.Model):
    DECISIONS = [
        ("PASS", "PASS"),
        ("FAIL", "FAIL"),
        ("PENDING", "PENDING"),
        ("NEEDS_REPEAT", "NEEDS_REPEAT"),
    ]

    specimen = models.ForeignKey(SpecimenMetric, on_delete=models.CASCADE, related_name="decisions")
    decision = models.CharField(max_length=20, choices=DECISIONS)
    comment = models.TextField(blank=True, default="")
    decided_by = models.ForeignKey(User, on_delete=models.PROTECT, related_name="qc_decisions")
    decided_at = models.DateTimeField()

    class Meta:
        ordering = ["-decided_at"]
        indexes = [models.Index(fields=["decision", "decided_at"])]

    def __str__(self) -> str:
        return f"{self.specimen_id}: {self.decision} by {self.decided_by.username}"

