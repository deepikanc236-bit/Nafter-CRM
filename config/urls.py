# RELOAD_ID: 1772470200000
from django.contrib import admin
from django.urls import path, include

from leads import views as lead_views

urlpatterns = [
    path("admin/", admin.site.urls),
    path("dashboard/", include("leads.dashboard_urls")),
    path("check-roles/", lead_views.check_roles_debug, name='check_roles_debug_root'),
    path("", include("leads.urls")),
]
