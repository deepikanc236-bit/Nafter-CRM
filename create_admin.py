import os
import django
from django.contrib.auth import get_user_model

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

def create_admin_user():
    User = get_user_model()
    username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
    password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
    email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')

    print(f"DEBUG: DJANGO_SUPERUSER_USERNAME is {'SET' if username else 'NOT SET'}")
    print(f"DEBUG: DJANGO_SUPERUSER_PASSWORD is {'SET' if password else 'NOT SET'}")
    print(f"DEBUG: DJANGO_SUPERUSER_EMAIL is {'SET' if email else 'NOT SET'}")

    if not username or not password:
        print("Skipping admin creation: DJANGO_SUPERUSER_USERNAME or DJANGO_SUPERUSER_PASSWORD not set.")
        return

    if not User.objects.filter(username=username).exists():
        print(f"Creating superuser: {username}")
        User.objects.create_superuser(username=username, email=email, password=password)
        print("Superuser created successfully!")
    else:
        print(f"Superuser '{username}' already exists.")

if __name__ == '__main__':
    create_admin_user()
