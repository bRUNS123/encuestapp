from rest_framework import serializers
from .models import Question, QuestionOption
from answers.models import Answer
from categories.models import Category
from datetime import datetime

class QuestionOptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = QuestionOption
        fields = ['id', 'title', 'votes']

class QuestionSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    category = serializers.CharField()
    creation_date = serializers.DateTimeField(required=False)
    expiration_date = serializers.DateTimeField(required=False)
    options = serializers.SerializerMethodField()
    user_has_voted = serializers.SerializerMethodField()
    user_vote_is_public = serializers.SerializerMethodField()
    user_rating = serializers.SerializerMethodField()
    current_user_answer = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ['id', 'title', 'category', 'question_type', 'creation_date', 'expiration_date', 'options', 'cantidad_votos', 'user_has_voted', 'user_vote_is_public', 'rating_average', 'rating_count', 'user_rating', 'current_user_answer']

    def get_options(self, obj):
        # Enforce ordering by ID to ensure consistency in frontend
        return QuestionOptionSerializer(obj.options.all().order_by('id'), many=True).data

    def get_user_has_voted(self, obj):
        request = self.context.get('request')
        if not request:
            return False
        
        # Check if user is authenticated and request.user is not None
        if hasattr(request, 'user') and request.user and hasattr(request.user, 'is_authenticated'):
            if request.user.is_authenticated:
                # Utiliza directamente request.user en lugar de request.user.profile
                return Answer.objects.filter(question=obj, profile=request.user).exists()
        
        return False

    def get_user_vote_is_public(self, obj):
        request = self.context.get('request')
        if not request:
            return True # Default public? No, irrelevant if not logged in.
        
        if hasattr(request, 'user') and request.user and hasattr(request.user, 'is_authenticated') and request.user.is_authenticated:
             answer = Answer.objects.filter(question=obj, profile=request.user).first()
             if answer:
                 return answer.is_public
        return True

    def get_user_rating(self, obj):
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            # Use specific filter to avoid N+1 if not prefetched, or just simple filter
            rating = obj.ratings.filter(user=request.user).first()
            return rating.score if rating else None
        return None

    def get_current_user_answer(self, obj):
        request = self.context.get('request')
        if not request:
            return None
        
        if hasattr(request, 'user') and request.user and hasattr(request.user, 'is_authenticated') and request.user.is_authenticated:
             answer = Answer.objects.filter(question=obj, profile=request.user).first()
             if answer:
                 return {
                     "option_id": answer.chosen_option.id if answer.chosen_option else None,
                     "text_answer": answer.text_answer
                 }
        return None

    def validate_category(self, value):
        if not Category.objects.filter(name=value).exists():
            raise serializers.ValidationError("La categoría no existe.")
        return value

    def create(self, validated_data):
        category_title = validated_data.pop('category')
        options_data = validated_data.pop('options', [])
        
        category, created = Category.objects.get_or_create(name=category_title)
        
        creation_date = validated_data.get('creation_date', datetime.now())
        question = Question.objects.create(category=category, creation_date=creation_date, **validated_data)
        
        for option_data in options_data:
            QuestionOption.objects.create(question=question, **option_data)
        
        return question

    def update(self, instance, validated_data):
        category_title = validated_data.pop('category', None)
        options_data = validated_data.pop('options', [])
        
        if category_title:
            category, created = Category.objects.get_or_create(name=category_title)
            instance.category = category
        
        instance.title = validated_data.get('title', instance.title)
        instance.creation_date = validated_data.get('creation_date', instance.creation_date)
        instance.cantidad_votos = validated_data.get('cantidad_votos', instance.cantidad_votos)
        instance.save()
        
        for option_data in options_data:
            option_id = option_data.get('id', None)
            if option_id:
                option = QuestionOption.objects.get(id=option_id, question=instance)
                option.title = option_data.get('title', option.title)
                option.votes = option_data.get('votes', option.votes)
                option.save()
            else:
                QuestionOption.objects.create(question=instance, **option_data)
        
        return instance
