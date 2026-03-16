import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from leads.models import Lead

print("--- USERS ---")
for u in User.objects.all():
    groups = [g.name for g in u.groups.all()]
    print(f"ID: {u.id}, Username: {u.username}, Super: {u.is_superuser}, Groups: {groups}")

print("\n--- LEAD 10 ---")
try:
    l = Lead.objects.get(id=10)
    print(f"ID: {l.id}, Name: {l.first_name}, Budget: {l.budget_inr_value}, Assigned ID: {l.assigned_user_id}")
    
    # Check if lead 10 would be visible to different roles
    # Senior Sales: 5L - 10L
    # Sales Exec: < 5L
    if l.budget_inr_value > 1000000:
        print("NOTE: Lead 10 budget (> 10L) EXCEEDS Senior Sales Executive cap.")
    if l.budget_inr_value >= 500000:
        print("NOTE: Lead 10 budget (>= 5L) EXCEEDS Sales Executive cap.")

except Lead.DoesNotExist:
    print("Lead 10 DOES NOT EXIST.")
except Exception as e:
    print(f"Error checking lead 10: {e}")
