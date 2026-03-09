# RELOAD_ID: 1772470200000
from django.urls import path
from . import views

urlpatterns = [
    path('kanban/', views.kanban_board, name='kanban'),
    path('test-routing/', views.home, name='test_routing'),
    path('update-lead-status/', views.update_lead_status, name='update_lead_status'),
    path('feedback-dashboard/', views.feedback_dashboard, name='feedback_dashboard'),
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('portfolio/', views.portfolio, name='portfolio'),
    path('contact/', views.contact, name='contact'),
    path('feedback/', views.feedback, name='feedback'),
]
