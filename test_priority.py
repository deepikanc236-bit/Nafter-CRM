import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from leads.models import Lead
from django.test import RequestFactory
from leads.views import contact
from django.contrib.auth.models import AnonymousUser

def simulate_contact_post(email, first_name, is_returning=False):
    factory = RequestFactory()
    data = {
        'first_name': first_name,
        'last_name': 'Test',
        'work_email': email,
        'company_name': 'Test Company',
        'country': 'US',
        'interest': 'AI_STRAT',
        'details': 'We need an AI strategy for our $10k budget.',
    }
    request = factory.post('/contact/', data)
    request.user = AnonymousUser()
    
    # Send request
    response = contact(request)
    
    # Retrieve the newly created lead
    lead = Lead.objects.filter(work_email=email).order_by('-created_at').first()
    return lead

def run_test():
    email = "test_regular_priority@example.com"
    
    # Clean up any existing leads with this email
    Lead.objects.filter(work_email=email).delete()
    
    print("Testing First Contact (New Customer)...")
    lead1 = simulate_contact_post(email, "NewUser")
    print(f"Lead 1 - Score: {lead1.lead_score}, Priority: {lead1.priority}, Is Returning: {lead1.is_returning}")
    
    print("\nTesting Second Contact (Regular Customer)...")
    lead2 = simulate_contact_post(email, "ReturningUser")
    print(f"Lead 2 - Score: {lead2.lead_score}, Priority: {lead2.priority}, Is Returning: {lead2.is_returning}")
    
    # Verify the bump
    if lead2.lead_score <= lead1.lead_score:
        print("❌ FAILED: Score was not boosted for the returning customer.")
    elif lead2.lead_score == lead1.lead_score + 20 or lead2.lead_score == 100:
        print(f"✅ PASSED: Score correctly boosted by +20 (from {lead1.lead_score} to {lead2.lead_score}).")
    else:
        print(f"⚠️ UNEXPECTED: Score boosted, but not by exactly 20. (from {lead1.lead_score} to {lead2.lead_score}).")


if __name__ == "__main__":
    try:
        run_test()
    except Exception as e:
        print(f"Error testing: {e}")
