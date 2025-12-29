
import os
import django
import sys
from django.utils import timezone

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from questions.models import Question, Option
from categories.models import Category
from django.contrib.auth import get_user_model

User = get_user_model()

def create_question():
    try:
        cat = Category.objects.get(name="PERSONAL")
        # Get a user to be the author (e.g. first user or admin)
        author = User.objects.first()
        if not author:
            print("No users found to assign as author")
            return

        q = Question.objects.create(
            title="¿Cómo te sientes hoy?",
            description="Pregunta personal de prueba",
            category=cat,
            author=author,
            question_type="binary", # or scale
            creation_date=timezone.now(),
            expiration_date=timezone.now() + timezone.timedelta(days=7),
            is_active=True
        )
        Option.objects.create(question=q, title="Bien")
        Option.objects.create(question=q, title="Mal")
        
        print(f"Created question '{q.title}' in category '{cat.name}'")

    except Category.DoesNotExist:
        print("Category 'PERSONAL' not found")

if __name__ == "__main__":
    create_question()
