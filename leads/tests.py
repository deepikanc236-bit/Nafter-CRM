from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Lead, LeadActivity

class LeadActivityTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(username='admin', password='password', email='admin@test.com')

    def test_lead_creation_signals(self):
        """Test that creating a lead via ORM creates a LeadActivity record."""
        lead = Lead.objects.create(
            first_name="Test",
            last_name="User",
            work_email="test@example.com",
            priority="High"
        )
        
        # Verify LeadActivity was created
        # Expected 1: from signals.py log_lead_changes (action="Lead Created (Public Form)")
        activities = LeadActivity.objects.filter(lead=lead)
        self.assertTrue(activities.exists())
        self.assertEqual(activities.count(), 1)
        self.assertEqual(activities.first().action, "Lead Created (Public Form)")
        self.assertIsNone(activities.first().changed_by)

class DashboardTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_superuser(username='admin', password='password', email='admin@test.com')
        self.client.force_login(self.user)
        
        Lead.objects.create(
            first_name="Positive",
            last_name="User",
            work_email="pos@example.com",
            interest="AI_AUTO",
            priority="High"
        )
        Lead.objects.create(
            first_name="Neutral",
            last_name="User",
            work_email="neu@example.com",
            interest="GEN_AI",
            priority="Medium"
        )

    def test_dashboard_view(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        
        # Check if basic stats are in context
        self.assertEqual(response.context['total_leads'], 2)
        
        # Check if priority stats are present (based on views.py logic)
        priority_stats = {item['priority']: item['count'] for item in response.context['priority_stats']}
        self.assertEqual(priority_stats.get('High'), 1)
        self.assertEqual(priority_stats.get('Medium'), 1)
