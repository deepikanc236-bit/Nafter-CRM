import threading
import os
from django.core.mail import send_mail
from django.conf import settings

def send_email_background(subject, message, recipient_list, from_email=None):
    """
    Helper to send email in a background thread to avoid blocking the UI.
    """
    from_email = from_email or getattr(settings, 'DEFAULT_FROM_EMAIL', 'support@nafterweb.com')
    
    def _send():
        try:
            send_mail(subject, message, from_email, recipient_list, fail_silently=False)
        except Exception as e:
            print(f">>> [ALERTS] Email error: {e}")

    threading.Thread(target=_send).start()

def send_high_value_alerts(lead):
    """
    Sends email and WhatsApp alerts for high-value leads in the background.
    """
    # 1. Admin Alert Email
    subject = f"🚨 HIGH VALUE LEAD: {lead.first_name} {lead.last_name}"
    message = f"Details:\nName: {lead.first_name} {lead.last_name}\nBudget: {lead.budget}\nINR Value: ₹{lead.budget_inr_value}\nService: {lead.interest}\nText: {lead.project_details}"
    send_email_background(subject, message, ['admin@nafterweb.com'], 'alerts@nafterweb.com')

    # 2. WhatsApp Alert (Twilio) - Backgrounded
    def _send_whatsapp():
        try:
            from twilio.rest import Client
            account_sid = os.getenv('TWILIO_SID')
            auth_token = os.getenv('TWILIO_AUTH_TOKEN')
            if not account_sid or not auth_token or account_sid == 'YOUR_TWILIO_SID':
                print(">>> [ALERTS] Twilio credentials missing, skipping WhatsApp.")
                return

            client = Client(account_sid, auth_token)
            client.messages.create(
                from_='whatsapp:+14155238886',
                body=f"🚨 *HIGH VALUE LEAD ALERT*\n\n*Name:* {lead.first_name} {lead.last_name}\n*Budget:* {lead.budget}\n*INR Value:* ₹{lead.budget_inr_value}",
                to=f"whatsapp:{os.getenv('MANAGER_WHATSAPP', '+91YOUR_NUMBER')}"
            )
        except Exception as e:
            print(f">>> [ALERTS] Twilio error: {e}")

    threading.Thread(target=_send_whatsapp).start()

    # 3. Management Email
    manager_email = getattr(settings, 'MANAGEMENT_EMAIL', 'admin@nafterweb.com')
    email_subject = f"🔥 MASSIVE LEAD: {lead.first_name} at {lead.company_name or 'Personal'}"
    email_body = f"""
    URGENT: A high-value lead has been submitted.
    
    Lead Details:
    - Name: {lead.first_name} {lead.last_name}
    - Email: {lead.work_email}
    - Website/Company: {lead.company_name}
    - Budget: ₹{lead.budget_inr_value}
    - Service: {lead.interest}
    - Engagement Score: {lead.engagement_score}
    - Conversion Prob: {lead.conversion_probability}%
    
    Dashboard Link: {getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')}/admin/leads/lead/{lead.id}/change/
    """
    send_email_background(email_subject, email_body, [manager_email])

def send_feedback_email(lead):
    """
    Sends an automated feedback request email in the background.
    """
    site_url = getattr(settings, 'SITE_URL', 'http://127.0.0.1:8000')
    feedback_url = f"{site_url}/feedback/"
    from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', 'support@nafterweb.com')
    
    subject = f"We'd love your feedback, {lead.first_name}!"
    message = f"""
Hi {lead.first_name},

Thank you for choosing Nafter AI for your project! Now that we've closed this phase, we'd love to hear about your experience.

Please take a moment to share your thoughts here: {feedback_url}

Best regards,
The Nafter AI Team
    """
    def _send():
        try:
            send_mail(subject, message, from_email, [lead.work_email], fail_silently=False)
            # Log the activity
            from .models import LeadActivity
            LeadActivity.objects.create(
                lead=lead,
                action_type='system_update',
                action=f"Automated feedback email sent to {lead.work_email}"
            )
        except Exception as e:
            print(f">>> [ALERTS] Feedback email error: {e}")

    threading.Thread(target=_send).start()
