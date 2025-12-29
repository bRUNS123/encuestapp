from rest_framework import serializers
from .models import Comment

class CommentSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='profile.user.username', read_only=True)
    nickname = serializers.CharField(source='profile.nickname', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'profile', 'username', 'nickname', 'question', 'text', 'created_at']
        read_only_fields = ['profile', 'created_at']
