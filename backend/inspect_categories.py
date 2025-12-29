
import os
import django
import sys

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from categories.models import Category

def list_categories():
    categories = Category.objects.all()
    with open("debug_categories.txt", "w", encoding="utf-8") as f:
        f.write(f"Found {categories.count()} categories:\n")
        for cat in categories:
            f.write(f"ID: {cat.id}, Name: '{cat.name}'\n")
    print("Exported to debug_categories.txt")


if __name__ == "__main__":
    list_categories()
