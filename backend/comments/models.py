from django.db import models
from profiles.models import Profile
from questions.models import Question

class Comment(models.Model):
    profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='comments')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='comments')
    text = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f'{self.profile.user.username} - {self.question.title[:20]}'

    class Meta:
        ordering = ['-created_at']
