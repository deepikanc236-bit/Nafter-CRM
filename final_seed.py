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

from django.contrib.auth.models import User, Group, Permission
from django.contrib.contenttypes.models import ContentType
from leads.models import Lead, Feedback, LeadActivity

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
            
        # Assign Permissions
        model_names = ['lead', 'feedback', 'leadactivity']
        actions = ['view', 'add', 'change', 'delete']
        
        for model_name in model_names:
            content_type = ContentType.objects.get(app_label='leads', model=model_name)
            
            # Managers get ALL actions
            if name == 'Sales Managers':
                perms = actions
            # Senior Executives get View/Add/Change
            elif name == 'Senior Sales Executives':
                perms = ['view', 'add', 'change']
            # Executives get View/Add
            else:
                perms = ['view', 'add']
                
            for action in perms:
                codename = f"{action}_{model_name}"
                try:
                    permission = Permission.objects.get(content_type=content_type, codename=codename)
                    group.permissions.add(permission)
                    print(f">>> [FINAL SEED] Assigned {codename} to {name}")
                except Permission.DoesNotExist:
                    print(f">>> [FINAL SEED] WARNING: Permission {codename} not found")

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
        user.set_password(password)
        user.is_staff = True
        user.save()
        if created:
            print(f">>> [FINAL SEED] Created user: {username}")
        else:
            print(f">>> [FINAL SEED] Updated password for existing user: {username}")
        
        # Always ensure group assignment
        try:
            group = Group.objects.get(name=group_name)
            user.groups.add(group)
            print(f">>> [FINAL SEED] Verified {username} in {group_name}")
        except Group.DoesNotExist:
            print(f">>> [FINAL SEED] ERROR: Group {group_name} missing!")

    # 3. Setup Sample Leads (if none exist)
    if not Lead.objects.filter(first_name='Small').exists():
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
        from leads.sentiment import analyze_sentiment
        from leads.ml_utils import calculate_conversion_probability
        
        for data in sample_leads:
            details = data['project_details']
            nlp_data = extract_lead_info(details)
            score, _ = analyze_sentiment(details)
            new_lead = Lead.objects.create(
                first_name=data['first_name'],
                last_name=data['last_name'],
                work_email=data['work_email'],
                project_details=details,
                status=data['status'],
                budget_inr_value=extract_smart_budget(details),
                service=nlp_data.get('service'),
                priority=nlp_data.get('priority', 'Medium'),
                lead_score=nlp_data.get('lead_score', 0)
            )
            new_lead.conversion_probability = calculate_conversion_probability(new_lead, score)
            new_lead.save()
        print(f">>> [FINAL SEED] Created {len(sample_leads)} sample leads.")
    else:
        print(">>> [FINAL SEED] Leads already exist, skipping sample seeding.")

    print(">>> [FINAL SEED] Seeding Complete.")

if __name__ == '__main__':
    run_seeding()
