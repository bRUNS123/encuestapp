
import os
import sys
import django

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from rest_framework.test import APIClient
from profiles.models import Profile, Friendship
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

try:
    friend_email = 'bfrancosentis@gmail.com'
    target_nickname = 'PROPIETARIO'
    
    # Get profiles
    try:
        friend_profile = Profile.objects.get(email=friend_email)
        target_profile = Profile.objects.get(nickname=target_nickname)
    except Profile.DoesNotExist:
        print("Profile not found by email/nickname. Trying users.")
        # Fallback if email logic differs
        pass

    # Ensure friendship
    is_friend = Friendship.objects.filter(
            (Q(sender=friend_profile, receiver=target_profile) | Q(sender=target_profile, receiver=friend_profile)) & Q(accepted=True)
    ).exists()
    print(f"Is friend? {is_friend}")

    user_obj = friend_profile
    
    client = APIClient()
    client.force_authenticate(user=user_obj)
    
    url = f'/api/profiles/{target_profile.id}/friend-votes/'
    print(f"Requesting {url}")
    
    response = client.get(url)
    
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Data length: {len(data)}")
        if len(data) > 0:
             first_item = data[0]
             print("First item keys:", first_item.keys())
             print(f"Voted At: {first_item.get('voted_at')}")
    else:
        print("Error:", response.data)

except Exception as e:
    import traceback
    traceback.print_exc()
