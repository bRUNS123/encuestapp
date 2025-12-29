
import os
import django
from django.urls import resolve, reverse

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from core.urls import router

print("Registered URLs in router:")
for url in router.urls:
    print(url)

print("\nChecking specific URL match:")
try:
    # Intenta resolver la URL que usa el frontend
    match = resolve('/api/profiles/compatibility-details/')
    print(f"FOUND: /api/profiles/compatibility-details/ -> {match.func_name}")
except Exception as e:
    print(f"NOT FOUND: /api/profiles/compatibility-details/ -> {e}")

try:
    match = resolve('/api/profiles/compatibility-details') # Sin slash
    print(f"FOUND: /api/profiles/compatibility-details -> {match.func_name}")
except Exception as e:
    print(f"NOT FOUND: /api/profiles/compatibility-details -> {e}")
