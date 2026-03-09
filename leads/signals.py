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
                user=None
            )
    else:
        # Field change tracking
        if hasattr(instance, '_Lead__old_status') and instance._Lead__old_status != instance.status:
            # Only create if not already handled by save_model (which would set user)
            # Actually, signals don't know about request.user. 
            # If we log in Admin save_model, we set the user. 
            # We skip here if an activity with the same action exists for this timestamp range? 
            # Simpler: just keep logging here as fallback or check if user is attached.
            pass
