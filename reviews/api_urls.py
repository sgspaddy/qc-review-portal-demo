from django.urls import path
from . import api_views

urlpatterns = [
    path("runs/", api_views.RunListAPI.as_view(), name="api_runs"),
    path("runs/<int:run_id>/specimens/", api_views.RunSpecimensAPI.as_view(), name="api_run_specimens"),
    path("specimens/<int:pk>/", api_views.SpecimenDetailAPI.as_view(), name="api_specimen_detail"),
    path("specimens/<int:pk>/decisions/", api_views.SpecimenDecisionsAPI.as_view(), name="api_specimen_decisions"),
    path("specimens/<int:pk>/decide/", api_views.SubmitDecisionAPI.as_view(), name="api_submit_decision"),
]

