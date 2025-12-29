#!/usr/bin/env python
"""Quick check script"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from profiles.models import Profile, Friendship
from answers.models import Answer

u = Profile.objects.get(email='amigo.test@example.com')
print('\n' + '='*50)
print('USUARIO DE PRUEBA CREADO')
print('='*50)
print(f'📧 Email: {u.email}')
print(f'👤 Nickname: {u.nickname}')
print(f'🔑 Password: testpass123')
print(f'📊 Votos totales: {Answer.objects.filter(profile=u).count()}')

f = Friendship.objects.filter(sender__email='bfrancosentis@gmail.com', receiver=u, accepted=True).first()
print(f'👥 Amigo de bfrancosentis: {'✓ SÍ' if f else '✗ NO'}')
if f:
    print(f'✅ Estado: Aceptado')
print('='*50 + '\n')
