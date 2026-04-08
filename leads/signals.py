from django.db.models.signals import post_save, post_init
from django.dispatch import receiver
from .models import Lead, LeadActivity

@receiver(post_init, sender=Lead)
def store_initial_status(sender, instance, **kwargs):
    """
    Stores the initial status when a Lead object is loaded from the database.
    """
    instance._old_status = instance.status

@receiver(post_save, sender=Lead)
def log_lead_changes(sender, instance, created, **kwargs):
    """
    Feature 1: Automatically logs changes to Lead Status or Assigned User.
    Also triggers automated feedback emails when a lead is moved to 'Closed'.
    """
    from .models import LeadActivity
    
    if created:
        # Check if an activity for "Lead Created" already exists (to avoid duplicates from Admin save_model)
        if not LeadActivity.objects.filter(lead=instance, action__icontains="Created").exists():
            LeadActivity.objects.create(
                lead=instance,
                action="Lead Created (Public Form)",
                changed_by=None
            )
            
        # Feature 3: High-Value Notifications (> 10 Lakhs)
        if instance.budget_inr_value and instance.budget_inr_value > 1000000:
            from .alerts import send_high_value_alerts
            send_high_value_alerts(instance)
            
    else:
        # Automated Feedback when Closed
        # Using the status stored during post_init to detect changes reliably
        old_status = getattr(instance, '_old_status', None)
        
        if old_status != 'Closed' and instance.status == 'Closed' and not getattr(instance, '_feedback_sent', False):
            from .alerts import send_feedback_email
            send_feedback_email(instance)
        
        # Update the stored status in case the object is saved again in the same instance
        instance._old_status = instance.status
