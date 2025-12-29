
import os
import django
from rest_framework.test import APIRequestFactory, force_authenticate
from profiles.views import ProfileViewSet
from profiles.models import Profile

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

def test_details():
    try:
        user = Profile.objects.get(email='bfrancosentis@gmail.com')
        amigo = Profile.objects.get(email='amigo.test@example.com')
        
        factory = APIRequestFactory()
        # Create request
        request = factory.get(f'/profiles/compatibility-details/?target_id={amigo.id}&target_type=user')
        force_authenticate(request, user=user)
        
        view = ProfileViewSet.as_view({'get': 'compatibility_details'})
        response = view(request)
        
        print(f"Status: {response.status_code}")
        if response.status_code == 200:
            data = response.data
            print(f"Data count: {len(data)}")
            if len(data) > 0:
                print("Sample Item:", data[0])
            else:
                print("No matching details found.")
        else:
            print("Response error:", response.data)
            
    except Exception as e:
        print(f"Error: {e}")

if __name__ == '__main__':
    test_details()
