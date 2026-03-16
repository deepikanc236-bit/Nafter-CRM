import os
import django
import random
from datetime import timedelta
from django.utils import timezone
from unittest.mock import patch

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from leads.models import Lead, Feedback, LeadActivity
from django.contrib.auth.models import User

def seed_data():
    print("Seeding data...")
    
    # Ensure superuser
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
        print("Created superuser: admin/admin123")
    
    admin = User.objects.get(username='admin')
    
    # Create some leads
    lead_data = [
        {
            'first_name': 'John',
            'last_name': 'Doe',
            'work_email': 'john@enterprise.com',
            'company_name': 'Enterprise Corp',
            'country': 'US',
            'interest': 'GEN_AI',
            'project_details': 'Need a generative AI solution for our customer support. Budget is around $50k. urgent.',
            'status': 'New',
        },
        {
            'first_name': 'Anish',
            'last_name': 'Kumar',
            'work_email': 'anish@startup.in',
            'company_name': 'TechStartup',
            'country': 'IN',
            'interest': 'AI_AUTO',
            'project_details': 'Looking for workflow automation. Budget is 15 lakhs.',
            'status': 'Contacted',
        },
        {
            'first_name': 'Sarah',
            'last_name': 'Schmidt',
            'work_email': 'sarah@global.de',
            'company_name': 'Global Solutions',
            'country': 'DE',
            'interest': 'AGENT_ORCH',
            'project_details': 'Interested in autonomous agent orchestration. Timeline is 3 months.',
            'status': 'Negotiation',
        },
        {
            'first_name': 'James',
            'last_name': 'Smith',
            'work_email': 'james@personal.com',
            'company_name': '',
            'country': 'UK',
            'interest': 'FULL_STACK',
            'project_details': 'Need a full stack website for my portfolio.',
            'status': 'Closed',
        }
    ]
    
    for data in lead_data:
        # We'll use the contact form logic essentially
        from leads.views import extract_smart_budget
        from leads.nlp_utils import extract_lead_info
        from leads.sentiment import analyze_sentiment
        from leads.ml_utils import calculate_conversion_probability
        
        details = data['project_details']
        nlp_data = extract_lead_info(details)
        sentiment_score, sentiment_label = analyze_sentiment(details)
        
        with patch('leads.views.send_high_value_alerts'):
            lead, created = Lead.objects.get_or_create(
                work_email=data['work_email'],
                defaults={
                    'first_name': data['first_name'],
                    'last_name': data['last_name'],
                    'company_name': data['company_name'],
                    'country': data['country'],
                    'interest': data['interest'],
                    'service': nlp_data.get('service'),
                    'urgency': nlp_data.get('urgency'),
                    'budget': nlp_data.get('budget'),
                    'budget_inr_value': extract_smart_budget(details),
                    'timeline': nlp_data.get('timeline'),
                    'lead_score': nlp_data.get('lead_score', 0),
                    'project_details': details,
                    'priority': nlp_data.get('priority', 'Medium'),
                    'status': data['status'],
                    'assigned_user': admin if random.choice([True, False]) else None
                }
            )
            if created:
                lead.conversion_probability = calculate_conversion_probability(lead, sentiment_score)
                lead.save()
                print(f"Created lead ID: {lead.id}")
            
    # Create some feedback
    feedback_msgs = [
        ("Great service!", 0.8, "Positive"),
        ("I'm not happy with the progress.", -0.6, "Negative"),
        ("It's okay, could be better.", 0.1, "Neutral"),
        ("Absolutely amazing AI solutions!", 0.9, "Positive"),
    ]
    
    for msg, score, label in feedback_msgs:
        Feedback.objects.create(
            client_name="Test Client",
            message=msg,
            sentiment_score=score,
            sentiment_label=label
        )
    print("Feedback seeded.")
    print("Seeding complete.")

if __name__ == '__main__':
    seed_data()
