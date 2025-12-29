
import os
import django
from django.urls import resolve

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

def check(path):
    try:
        match = resolve(path)
        print(f"✅ MATCH: {path}")
    except Exception as e:
        print(f"❌ FAIL: {path} -> {e}")

print("Checking URLs...")
check('/api/profiles/compatibility-details/')
