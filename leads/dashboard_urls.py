from django.urls import path
from . import views

urlpatterns = [
    path('leads/', views.LeadListView.as_view(), name='lead_list'),
    path('leads/<int:pk>/', views.LeadDetailView.as_view(), name='lead_detail'),
    path('', views.dashboard, name='dashboard'),
]
