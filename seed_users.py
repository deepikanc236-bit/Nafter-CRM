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
        
        # Always update password and staff status
        user.set_password(password)
        user.is_staff = True
        user.save()
        
        if created:
            print(f"Created user: {username}")
        else:
            print(f"Updated existing user: {username}")
        
        # Always ensure group membership
        group = Group.objects.get(name=group_name)
        user.groups.add(group)
        print(f"Ensured {username} is in group {group_name}")

if __name__ == '__main__':
    create_role_users()
