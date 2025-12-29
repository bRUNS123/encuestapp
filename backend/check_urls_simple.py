
import os
import django
from django.urls import resolve

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

def check(path):
    print(f"Checking {path}...")
    try:
        match = resolve(path)
        print(f"✅ MATCH: {match.view_name}")
    except Exception as e:
        print(f"❌ FAIL: {e}")

print("--- URL CHECK ---")
check('/api/profiles/compatibility-details/')
check('/api/profiles/compatibility/')
print("-----------------")
