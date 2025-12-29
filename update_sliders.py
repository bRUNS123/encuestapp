import os
import django
import sys

# Setup Django environment
sys.path.append(r'd:\PROGRAMACION\decidelibre-gravity\backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'encuestapp.settings')
django.setup()

from questions.models import Question, QuestionOption

def set_slider(qid, min_val, max_val, step_val):
    try:
        q = Question.objects.get(id=qid)
        print(f"Found Question {qid}: {q.title}")
        
        # Verify it is the target question text before nuking options if unsure
        # But for 1220 we know. For 1219 we suspect.
        
        q.question_type = 'slider'
        q.save()
        
        # Clear existing options
        q.options.all().delete()
        
        # Create new options in order: Min, Max, Step
        QuestionOption.objects.create(question=q, title=str(min_val), votes=0)
        QuestionOption.objects.create(question=q, title=str(max_val), votes=0)
        QuestionOption.objects.create(question=q, title=str(step_val), votes=0)
        
        print(f"SUCCESS: Updated {q.title} to slider [{min_val}, {max_val}, {step_val}]")
    except Question.DoesNotExist:
        print(f"Question {qid} not found")
    except Exception as e:
        print(f"Error updating {qid}: {e}")

print("Updating Estatura (1220)...")
set_slider(1220, 50, 300, 1)

print("\nUpdating Peso (checking 1219)...")
# Check if 1219 is indeed Peso-related
try:
    q1219 = Question.objects.get(id=1219)
    if "peso" in q1219.title.lower() or "kg" in q1219.title.lower():
         set_slider(1219, 10, 600, 1)
    else:
         print(f"Skipping 1219, title '{q1219.title}' does not look like Weight.")
         # Search for Peso if not 1219?
         peso_q = Question.objects.filter(title__icontains="Peso").first()
         if peso_q:
             print(f"Found alternative 'Peso' question ID: {peso_q.id}")
             set_slider(peso_q.id, 10, 600, 1)
except Question.DoesNotExist:
    print("Question 1219 not found.")
