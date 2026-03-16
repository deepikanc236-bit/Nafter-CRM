from django.urls import path
from . import views

urlpatterns = [
    path('leads/', views.LeadListView.as_view(), name='lead_list'),
    path('leads/<int:pk>/', views.LeadDetailView.as_view(), name='lead_detail'),
    path('leads/<int:lead_id>/assign/', views.assign_lead, name='assign_lead'),
    path('ranking/', views.lead_ranking, name='lead_ranking'),
    path('export-csv/', views.export_leads_csv, name='export_leads_csv'),
    path('', views.dashboard, name='dashboard'),
]
