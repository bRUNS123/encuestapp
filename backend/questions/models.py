from django.db import models
from django.conf import settings
from categories.models import Category

class Question(models.Model):
    QUESTION_TYPE_CHOICES = [
        ('binary', 'Binaria (Sí/No)'),
        ('scale', 'Escala (1-5)'),
        ('dropdown', 'Lista desplegable'),
        ('open', 'Abierta (Texto)'),
        ('slider', 'Deslizador (Rango)'),
    ]
    
    title = models.CharField(max_length=500)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='questions')
    question_type = models.CharField(max_length=20, choices=QUESTION_TYPE_CHOICES, default='binary')
    creation_date = models.DateTimeField(auto_now_add=True)
    expiration_date = models.DateTimeField(null=True, blank=True)
    cantidad_votos = models.IntegerField(default=0)
    rating_average = models.FloatField(default=0.0)
    rating_count = models.IntegerField(default=0)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='created_questions', null=True, blank=True)
    
    class Meta:
        ordering = ['-creation_date']

    def __str__(self):
        return self.title

class QuestionRating(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='ratings')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    score = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('question', 'user')

class QuestionOption(models.Model):
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='options')
    title = models.CharField(max_length=255)
    votes = models.IntegerField(default=0)  # Asegúrate de tener este campo para los votos
    
    class Meta:
        ordering = ['id']

    def __str__(self):
        return self.title