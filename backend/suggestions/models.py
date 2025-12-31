from django.db import models
from profiles.models import Profile

class Suggestion(models.Model):
    user = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='suggestions')
    content = models.TextField(max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)
    likes = models.ManyToManyField(Profile, related_name='liked_suggestions', blank=True)

    def __str__(self):
        return f"Suggestion by {self.user}: {self.content[:20]}"
