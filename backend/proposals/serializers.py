from rest_framework import serializers
from .models import ProposedQuestion, ProposalVote
from categories.models import Category


class ProposedQuestionSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    creator_username = serializers.CharField(source='creator.nickname', read_only=True)
    user_has_voted = serializers.SerializerMethodField()
    approval_threshold = serializers.SerializerMethodField()
    total_users = serializers.SerializerMethodField()
    
    class Meta:
        model = ProposedQuestion
        fields = [
            'id', 'title', 'category', 'category_name', 'option1_text', 'option2_text',
            'status', 'votes_count', 'created_at', 'approved_at',
            'creator_username', 'user_has_voted', 'approval_threshold', 'total_users'
        ]
        read_only_fields = ['id', 'status', 'votes_count', 'created_at', 'approved_at']
    
    def get_user_has_voted(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return ProposalVote.objects.filter(proposal=obj, voter=request.user).exists()
        return False
    
    def get_approval_threshold(self, obj):
        from profiles.models import Profile
        total_users = Profile.objects.count()
        return max(20, int(total_users * 0.33))
    
    def get_total_users(self, obj):
        from profiles.models import Profile
        return Profile.objects.count()


class ProposedQuestionCreateSerializer(serializers.ModelSerializer):
    category = serializers.CharField()
    
    class Meta:
        model = ProposedQuestion
        fields = ['title', 'category', 'option1_text', 'option2_text']
    
    def validate_category(self, value):
        try:
            category = Category.objects.get(name=value)
            return category
        except Category.DoesNotExist:
            raise serializers.ValidationError("La categoría no existe.")
    
    def create(self, validated_data):
        request = self.context.get('request')
        validated_data['creator'] = request.user
        return super().create(validated_data)
