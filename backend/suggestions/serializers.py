from rest_framework import serializers
from .models import Suggestion

class SuggestionSerializer(serializers.ModelSerializer):
    user_nickname = serializers.CharField(source='user.nickname', read_only=True)
    user_avatar = serializers.URLField(source='user.photo_url', read_only=True)
    likes_count = serializers.IntegerField(source='likes.count', read_only=True)
    is_liked_by_user = serializers.SerializerMethodField()

    class Meta:
        model = Suggestion
        fields = ['id', 'user', 'user_nickname', 'user_avatar', 'content', 'created_at', 'likes_count', 'is_liked_by_user']
        read_only_fields = ['user']

    def get_is_liked_by_user(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(id=request.user.id).exists()
        return False
