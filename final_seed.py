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
from leads.models import Lead

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
    main_password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'Nafter2026!')
    
    users_to_create = [
        # (username, group_name, env_var_for_password)
        ('sales_manager', 'Sales Managers', 'sales_manager'),
        ('senior_sales_executives', 'Senior Sales Executives', 'senior_sales_executives'),
        ('sales_executives', 'Sales Executives', 'sales_executives'),
    ]
    
    for username, group_name, env_var in users_to_create:
        user, created = User.objects.get_or_create(username=username)
        
        # Determine the password: Use specific env var, fallback to main superuser password
        password = os.environ.get(env_var, main_password)
        
        # Only set password for NEWLY created users
        # This allows you to change passwords in Admin and have them persist!
        if created:
            user.set_password(password)
            user.is_staff = True
            user.save()
            print(f">>> [FINAL SEED] Created user: {username} (using {env_var} or fallback)")
        else:
            print(f">>> [FINAL SEED] Account already exists: {username} (Skipping password overwrite)")
        
        # Always ensure group assignment
        try:
            group = Group.objects.get(name=group_name)
            user.groups.add(group)
            print(f">>> [FINAL SEED] Verified {username} in {group_name}")
        except Group.DoesNotExist:
            print(f">>> [FINAL SEED] ERROR: Group {group_name} missing!")

    # 3. Setup Sample Leads (if none exist)
    if Lead.objects.count() == 0:
        print(">>> [FINAL SEED] Seeding sample leads for RBAC verification...")
        sample_leads = [
            {
                'first_name': 'Small', 'last_name': 'Project', 'work_email': 'small@test.com',
                'project_details': 'Simple website. Budget is ₹2,00,000.', 'status': 'New'
            },
            {
                'first_name': 'Medium', 'last_name': 'Project', 'work_email': 'med@test.com',
                'project_details': 'AI Chatbot. Budget is ₹7,50,000.', 'status': 'Contacted'
            },
            {
                'first_name': 'Enterprise', 'last_name': 'Project', 'work_email': 'big@test.com',
                'project_details': 'Custom ERP System. Budget is ₹25,00,000.', 'status': 'Negotiation'
            }
        ]
        
        from leads.views import extract_smart_budget
        from leads.nlp_utils import extract_lead_info
        
        for data in sample_leads:
            details = data['project_details']
            nlp_data = extract_lead_info(details)
            Lead.objects.create(
                first_name=data['first_name'],
                last_name=data['last_name'],
                work_email=data['work_email'],
                project_details=details,
                status=data['status'],
                budget_inr_value=extract_smart_budget(details),
                service=nlp_data.get('service'),
                priority=nlp_data.get('priority', 'Medium')
            )
        print(f">>> [FINAL SEED] Created {len(sample_leads)} sample leads.")
    else:
        print(">>> [FINAL SEED] Leads already exist, skipping sample seeding.")

    print(">>> [FINAL SEED] Seeding Complete.")

if __name__ == '__main__':
    run_seeding()
