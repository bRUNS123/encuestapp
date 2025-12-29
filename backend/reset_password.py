#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from profiles.models import Profile


# Check for Typo Email first
typo_email = 'bfrancosentis@gmaill.com'
correct_email = 'bfrancosentis@gmail.com'
target_password = 'password123'

def reset_for_email(email):
    try:
        user = Profile.objects.get(email=email)
        print(f"Usuario encontrado: {user.email}")
        user.set_password(target_password)
        user.save()
        print(f"✅ Contraseña restablecida exitosamente a: {target_password}")
        return True
    except Profile.DoesNotExist:
        print(f"❌ El usuario {email} NO existe.")
        return False

print("--- Intentando con el email escrito (typo) ---")
if not reset_for_email(typo_email):
    print("\n--- Intentando con el email correcto (gmail.com) ---")
    reset_for_email(correct_email)

