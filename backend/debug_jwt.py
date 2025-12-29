import os
import django
from django.conf import settings

# Setup Django if run standalone (though manage.py shell handles this usually)
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
# django.setup()

from profiles.models import Profile
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

def test_jwt():
    try:
        u = Profile.objects.first()
        if not u:
            print("No users found!")
            return

        print(f"Testing JWT for user: {u.email}")
        refresh = RefreshToken.for_user(u)
        access_str = str(refresh.access_token)
        print(f"Generated Access Token (first 20 chars): {access_str[:20]}...")

        # Verify
        try:
            token = AccessToken(access_str)
            print("Verifying token with AccessToken(token)... SUCCESS")
            print(f"Token payload: {token.payload}")
        except Exception as e:
            print(f"Verifying token FAILED: {e}")

    except Exception as e:
        print(f"General Error: {e}")

if __name__ == "__main__":
    test_jwt()
