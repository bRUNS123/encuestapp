
import os
import django
from django.conf import settings

# Configure Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'decidelibre_gravity.settings')
django.setup()

from backend.models import Category

def list_categories():
    categories = Category.objects.all()
    print(f"Found {categories.count()} categories:")
    for cat in categories:
        print(f"ID: {cat.id}, Name: '{cat.name}'")

if __name__ == "__main__":
    list_categories()
