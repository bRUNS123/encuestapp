
import os
import sys
import django

# Add the project root to the python path
sys.path.append(os.getcwd())
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'decidelibre.settings')
django.setup()

from categories.models import Category

def rename_category():
    try:
        # Try to find 'Mundial' (case insensitive)
        cats = Category.objects.filter(name__iexact='Mundial')
        if not cats.exists():
             print("Category 'Mundial' not found.")
             
             # Check if Internacional already exists
             if Category.objects.filter(name__iexact='Internacional').exists():
                 print("Category 'Internacional' already exists.")
             return

        for cat in cats:
            print(f"Renaming category {cat.name} to Internacional")
            cat.name = 'Internacional'
            cat.save()

    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    rename_category()
