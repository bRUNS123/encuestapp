
import os
import django
import sys

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from questions.models import Question

def check_peso():
    qs = Question.objects.filter(title__icontains="Peso")
    print(f"Found {qs.count()} questions matching 'Peso'")
    for q in qs:
        print(f"ID: {q.id}")
        print(f"Title: {q.title}")
        print(f"Type: {q.question_type}")
        print(f"Options Count: {q.options.count()}")
        print("Options: ", [o.title for o in q.options.all()])

if __name__ == "__main__":
    check_peso()
