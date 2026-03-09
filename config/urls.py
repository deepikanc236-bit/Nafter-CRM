# RELOAD_ID: 1772470200000
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path("admin/", admin.site.urls),
    path("dashboard/", include("leads.dashboard_urls")),
    path("", include("leads.urls")),
]
