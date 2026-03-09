from django.test import TestCase
from django.urls import reverse
from .models import Lead

class DashboardTest(TestCase):
    def setUp(self):
        Lead.objects.create(
            name="Test User",
            email="test@example.com",
            sentiment_label="Positive",
            priority="High"
        )
        Lead.objects.create(
            name="Neutral User",
            email="neutral@example.com",
            sentiment_label="Neutral",
            priority="Medium"
        )

    def test_dashboard_view(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertIn('sentiment_counts', response.context)
        self.assertIn('priority_counts', response.context)
        
        # Check if counts are correct
        sentiment_context = {item['sentiment_label']: item['count'] for item in response.context['sentiment_counts']}
        self.assertEqual(sentiment_context.get('Positive'), 1)
        self.assertEqual(sentiment_context.get('Neutral'), 1)
        
        priority_context = {item['priority']: item['count'] for item in response.context['priority_counts']}
        self.assertEqual(priority_context.get('High'), 1)
        self.assertEqual(priority_context.get('Medium'), 1)
