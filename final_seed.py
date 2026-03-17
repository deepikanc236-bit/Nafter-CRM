import os
import django
import sys

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
try:
    django.setup()
except Exception as e:
    print(f"FAILED TO SETUP DJANGO: {e}")
    sys.exit(1)

from django.contrib.auth.models import User, Group

def run_seeding():
    print(">>> [FINAL SEED] Starting...")
    
    # 1. Setup Groups
    groups = [
        'Sales Managers',
        'Senior Sales Executives',
        'Sales Executives'
    ]
    
    for name in groups:
        group, created = Group.objects.get_or_create(name=name)
        if created:
            print(f">>> [FINAL SEED] Created group: {name}")
        else:
            print(f">>> [FINAL SEED] Group exists: {name}")

    # 2. Setup Role Users
    password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'Nafter2026!')
    users_to_create = [
        ('sales_manager', 'Sales Managers'),
        ('senior_sales_executives', 'Senior Sales Executives'),
        ('sales_executives', 'Sales Executives'),
    ]
    
    for username, group_name in users_to_create:
        user, created = User.objects.get_or_create(username=username)
        
        # Always ensure permissions and password
        user.set_password(password)
        user.is_staff = True
        user.save()
        
        if created:
            print(f">>> [FINAL SEED] Created user: {username}")
        else:
            print(f">>> [FINAL SEED] Updated user: {username}")
        
        # Ensure group assignment
        try:
            group = Group.objects.get(name=group_name)
            user.groups.add(group)
            print(f">>> [FINAL SEED] Verified {username} in {group_name}")
        except Group.DoesNotExist:
            print(f">>> [FINAL SEED] ERROR: Group {group_name} missing!")

    print(">>> [FINAL SEED] Seeding Complete.")

if __name__ == '__main__':
    run_seeding()
