import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()
print(f"User model: {User}")
try:
    print(f"Count: {User.objects.count()}")
    admin_exists = User.objects.filter(username='admin').exists()
    print(f"Admin exists: {admin_exists}")
except Exception as e:
    print(f"Error: {e}")
