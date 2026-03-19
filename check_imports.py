import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
try:
    django.setup()
    print("Django Setup: OK")
    from leads import views
    print("Leads Views Import: OK")
except Exception as e:
    print(f"CRASH: {e}")
    import traceback
    traceback.print_exc()
