from answers.models import Answer
from questions.models import Question, QuestionRating, QuestionOption

print("Starting vote reset...")

# 1. Delete all individual answers (Audit log of votes)
deleted_answers, _ = Answer.objects.all().delete()
print(f"Deleted {deleted_answers} answers.")

# 2. Delete all ratings
deleted_ratings, _ = QuestionRating.objects.all().delete()
print(f"Deleted {deleted_ratings} ratings.")

# 3. Reset option vote counts
updated_options = QuestionOption.objects.all().update(votes=0)
print(f"Reset votes for {updated_options} options.")

# 4. Reset question statistics
updated_questions = Question.objects.all().update(
    cantidad_votos=0,
    rating_average=0.0,
    rating_count=0
)
print(f"Reset stats for {updated_questions} questions.")

print("Vote reset complete!")
