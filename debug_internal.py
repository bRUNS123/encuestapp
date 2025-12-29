
import os
import sys
import django

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from questions.serializers import QuestionSerializer
from answers.models import Answer
from profiles.models import Profile
from django.test import RequestFactory

try:
    # Get a target user
    target = Profile.objects.get(nickname='PROPIETARIO')
    friend = Profile.objects.get(email='bfrancosentis@gmail.com')
    print(f"Target: {target}")
    print(f"Viewing as: {friend}")
    
    # Get answers - Add order_by which is present in views.py
    answers = Answer.objects.filter(profile=target).select_related('question', 'chosen_option').order_by('-timestamp')
    print(f"Answers count: {answers.count()}")
    
    factory = RequestFactory()
    request = factory.get('/')
    request.user = friend # Mock user as friend
    
    print("Testing serialization...")
    for ans in answers[:5]: # Test first 5
        try:
            print(f"Serializing question {ans.question.id}")
            s = QuestionSerializer(ans.question, context={'request': request})
            # Accessing .data triggers serialization
            d = s.data
            print("Success")
        except Exception:
            import traceback
            traceback.print_exc()
            break
            
except Exception as e:
    print(f"Setup Error: {e}")
