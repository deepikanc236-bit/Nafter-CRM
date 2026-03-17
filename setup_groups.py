import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import Group

def create_groups():
    groups = [
        'Sales Managers',
        'Senior Sales Executives',
        'Sales Executives'
    ]
    
    for name in groups:
        group, created = Group.objects.get_or_create(name=name)
        if created:
            print(f"Created group: {name}")
        else:
            print(f"Group already exists: {name}")

if __name__ == '__main__':
    create_groups()
