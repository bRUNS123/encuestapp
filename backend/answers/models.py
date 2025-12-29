from django.db import models
from profiles.models import Profile
from questions.models import Question, QuestionOption
from django.utils import timezone

class Answer(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, blank=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    chosen_option = models.ForeignKey(QuestionOption, on_delete=models.CASCADE, null=True, blank=True)
    text_answer = models.TextField(null=True, blank=True)
    is_anonymous = models.BooleanField(default=False)
    anonymous_token = models.CharField(max_length=255, null=True, blank=True)
    is_public = models.BooleanField(default=True)
    timestamp = models.DateTimeField(default=timezone.now)

    class Meta:
        # unique_together removido porque causaba conflictos con votos de usuarios registrados
        # La lógica de votos duplicados se maneja en la vista
        pass
