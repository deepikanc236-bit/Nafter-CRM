from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Lead, LeadActivity

@receiver(post_save, sender=Lead)
def log_lead_changes(sender, instance, created, **kwargs):
    """
    Feature 1: Automatically logs changes to Lead Status or Assigned User.
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
        # Field change tracking
        # ... existing logic ...
        
        # Automated Feedback when Closed
        if hasattr(instance, '_old_status') and instance._old_status != 'Closed' and instance.status == 'Closed':
            from .alerts import send_feedback_email
            send_feedback_email(instance)

def remember_status(sender, instance, **kwargs):
    instance._old_status = instance.status

from django.db.models.signals import pre_save
@receiver(pre_save, sender=Lead)
def store_old_status(sender, instance, **kwargs):
    if instance.pk:
        try:
            old_obj = Lead.objects.get(pk=instance.pk)
            instance._old_status = old_obj.status
        except Lead.DoesNotExist:
            instance._old_status = None
    else:
        instance._old_status = None
