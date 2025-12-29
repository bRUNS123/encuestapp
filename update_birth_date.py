import os
import sys
import django

sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from questions.models import Question, QuestionOption

def update_birth_date():
    try:
        # Find question by title match (case insensitive)
        q = Question.objects.filter(title__iexact="Fecha de Nacimiento").first()
        if not q:
            print("❌ Question 'Fecha de Nacimiento' not found in DB")
            return

        print(f"✅ Found Question ID: {q.id}, Type: {q.question_type}")
        
        # Update type
        q.question_type = 'date'
        q.save()
        print(f"🔄 Updated Question ID {q.id} type to 'date'")

        # Clear options
        count = q.options.count()
        q.options.all().delete()
        print(f"🗑️ Deleted {count} options (years)")

    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    update_birth_date()
