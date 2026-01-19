from django.urls import path
from . import views

urlpatterns = [
    path("", views.dashboard, name="dashboard"),
    path("run/<int:pk>/", views.run_detail, name="run_detail"),
    path("specimen/<int:pk>/", views.specimen_detail, name="specimen_detail"),
    path("specimen/<int:pk>/decide/", views.submit_decision, name="submit_decision"),
    path("seed-demo/", views.seed_demo, name="seed_demo"),
]

