from django.contrib import admin
from .models import BatchRun, SpecimenMetric, QcDecision


@admin.register(BatchRun)
class BatchRunAdmin(admin.ModelAdmin):
    list_display = ("run_id", "instrument", "run_group", "created_at")
    search_fields = ("run_id", "instrument", "run_group")


@admin.register(SpecimenMetric)
class SpecimenMetricAdmin(admin.ModelAdmin):
    list_display = ("case_id", "specimen_name", "specimen_type", "run", "mapped_reads", "contamination", "mean_coverage", "created_at")
    list_filter = ("specimen_type", "run__run_group")
    search_fields = ("case_id", "specimen_name", "run__run_id")


@admin.register(QcDecision)
class QcDecisionAdmin(admin.ModelAdmin):
    list_display = ("specimen", "decision", "decided_by", "decided_at")
    list_filter = ("decision", "decided_by")
    search_fields = ("specimen__case_id", "specimen__specimen_name", "specimen__run__run_id")

