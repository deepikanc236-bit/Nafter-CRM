import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User, Group

def create_role_users():
    # Use the password provided in the Render environment or a default one
    password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'Nafter2026!')
    
    users_to_create = [
        ('sales_manager', 'Sales Managers'),
        ('senior_sales_executives', 'Senior Sales Executives'),
        ('sales_executives', 'Sales Executives'),
    ]
    
    for username, group_name in users_to_create:
        # Create user if not exists
        user, created = User.objects.get_or_create(username=username)
        if created:
            user.set_password(password)
            user.is_staff = True  # Must be staff to see dashboard
            user.save()
            print(f"Created user: {username}")
        else:
            print(f"User already exists: {username}")
        
        # Assign to group
        group = Group.objects.get(name=group_name)
        user.groups.add(group)
        print(f"Assigned {username} to {group_name}")

if __name__ == '__main__':
    create_role_users()
