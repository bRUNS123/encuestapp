
import os
import django
import sys

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from questions.models import Question
from categories.models import Category

def check_personal_questions():
    try:
        cat = Category.objects.get(name="PERSONAL")
        print(f"Category found: ID={cat.id}, Name='{cat.name}'")
        questions = Question.objects.filter(category=cat)
        print(f"Questions count for category '{cat.name}': {questions.count()}")
        for q in questions[:5]:
            print(f" - Q: {q.title}")
    except Category.DoesNotExist:
        print("Category 'PERSONAL' not found in DB")

if __name__ == "__main__":
    check_personal_questions()
