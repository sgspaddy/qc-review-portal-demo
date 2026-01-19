from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    path("admin/", admin.site.urls),

    # Auth
    path("login/", auth_views.LoginView.as_view(template_name="reviews/login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),

    # UI
    path("", include("reviews.urls")),

    # API (versioned)
    path("api/v1/", include("reviews.api_urls")),
]

