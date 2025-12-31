from rest_framework import viewsets, filters, status
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import IsAuthenticatedOrReadOnly, AllowAny
from django_filters.rest_framework import DjangoFilterBackend
from .serializers import QuestionSerializer, QuestionOptionSerializer
from .models import Question, QuestionOption, QuestionRating
from rest_framework.decorators import action
from rest_framework.response import Response
from answers.models import Answer
from django.db import models
from profiles.models import Profile

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 100

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter, filters.OrderingFilter, DjangoFilterBackend]
    search_fields = ['title', 'category__name']
    ordering_fields = ['creation_date', 'cantidad_votos', 'rating_average']
    filterset_fields = [] # Handled manually in get_queryset
    ordering = ['-creation_date']
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            from core.permissions import IsOwnerOrAdmin
            return [IsAuthenticatedOrReadOnly(), IsOwnerOrAdmin()]
        return [IsAuthenticatedOrReadOnly()]

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(owner=self.request.user)
        else:
            serializer.save()

    def get_queryset(self):
        # print(f"DEBUG: User: {self.request.user}, Is Auth: {self.request.user.is_authenticated}")
        queryset = Question.objects.all()
        print(f"🔍 Initial queryset count: {queryset.count()}")
        
        # Restriction for anonymous users
        # Restriction for anonymous users
        # if self.request.user.is_anonymous:
            # Case insensitive exclusion ensuring consistency
            # queryset = queryset.exclude(category__name__iexact='PERSONAL')

        # Case-insensitive category filtering
        category_name = self.request.query_params.get('category__name')
        print(f"🔍 Category filter requested: {category_name}")
        if category_name:
            queryset = queryset.filter(category__name__iexact=category_name)
            print(f"🔍 After category filter, count: {queryset.count()}")
            
        print(f"🔍 Final queryset count: {queryset.count()}")
        return queryset

    @action(detail=True, methods=['post'])
    def vote(self, request, pk=None):
        from django.db import transaction
        import traceback
        
        try:
            question = self.get_object()
            option_id = request.data.get('option_id')
            text_answer = request.data.get('text_answer')
            is_anonymous = request.data.get('is_anonymous', False)
            user_token = request.data.get('user_token', None)
            profile_id = request.data.get('profile_id', None)

            # Validation based on Question Type
            if question.question_type in ['open', 'slider']:
                if not text_answer:
                    return Response({"error": "Text answer is required for open/slider questions"}, status=status.HTTP_400_BAD_REQUEST)
                new_option = None
            else:
                if not option_id:
                    return Response({"error": "Option ID is required"}, status=status.HTTP_400_BAD_REQUEST)
                try:
                    new_option = QuestionOption.objects.get(id=option_id, question=question)
                except QuestionOption.DoesNotExist:
                    return Response({"error": "Option not found"}, status=status.HTTP_404_NOT_FOUND)

            if is_anonymous and not user_token:
                return Response({"error": "User token is required for anonymous voting"}, status=status.HTTP_400_BAD_REQUEST)

            profile = None
            if not is_anonymous:
                if request.user and request.user.is_authenticated:
                    profile = request.user
                else:
                    try:
                        profile = Profile.objects.get(id=profile_id)
                    except Profile.DoesNotExist:
                        return Response({"error": "Profile not found"}, status=status.HTTP_404_NOT_FOUND)

            # Check for existing answer
            existing_answer = None
            if is_anonymous:
                existing_answer = Answer.objects.filter(question=question, anonymous_token=user_token, is_anonymous=True).first()
            else:
                existing_answer = Answer.objects.filter(question=question, profile=profile).first()

            with transaction.atomic():
                if existing_answer:
                    # Logic for updating answer
                    if question.question_type in ['open', 'slider']:
                        existing_answer.text_answer = text_answer
                        existing_answer.save()
                        # No vote count changes for open/slider questions (unless we track value distribution later)
                    else:
                         if existing_answer.chosen_option.id == new_option.id:
                            # Already voted for this option
                            pass 
                         else:
                            # Cambio de voto
                            old_option = existing_answer.chosen_option
                            if old_option and old_option.votes > 0:
                                old_option.votes = models.F('votes') - 1
                                old_option.save()
                            
                            existing_answer.chosen_option = new_option
                            existing_answer.save()
                            
                            new_option.votes = models.F('votes') + 1
                            new_option.save()
                else:
                    # Create new answer
                    Answer.objects.create(
                        profile=profile,
                        question=question,
                        anonymous_token=user_token if is_anonymous else None,
                        chosen_option=new_option, # None for open
                        text_answer=text_answer if question.question_type in ['open', 'slider'] else None,
                        is_anonymous=is_anonymous
                    )
                    
                    # Increment question total votes
                    question.cantidad_votos = models.F('cantidad_votos') + 1
                    question.save()

                    if new_option:
                        new_option.votes = models.F('votes') + 1
                        new_option.save()

            question.refresh_from_db()
            response_data = {
                "question": QuestionSerializer(question, context={'request': request}).data,
            }
            if new_option:
                 new_option.refresh_from_db()
                 response_data["option"] = QuestionOptionSerializer(new_option).data
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            # Log the full traceback
            print("="*50)
            print("ERROR IN VOTE VIEW:")
            print(traceback.format_exc())
            print("="*50)
            return Response({
                "error": f"Internal server error: {str(e)}",
                "detail": traceback.format_exc()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            return Response({
                "error": f"Internal server error: {str(e)}",
                "detail": traceback.format_exc()
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'])
    def rate(self, request, pk=None):
        from django.db.models import Avg, Count
        
        question = self.get_object()
        score = request.data.get('score')
        
        if not request.user or not request.user.is_authenticated:
             return Response({"error": "Authentication required"}, status=status.HTTP_401_UNAUTHORIZED)
             
        try:
            score = int(score)
            if not 1 <= score <= 5:
                raise ValueError
        except (TypeError, ValueError):
            return Response({"error": "Score must be an integer between 1 and 5"}, status=status.HTTP_400_BAD_REQUEST)
            
        rating, created = QuestionRating.objects.update_or_create(
            question=question,
            user=request.user,
            defaults={'score': score}
        )
        
        # Efficient aggregation
        result = question.ratings.aggregate(avg=Avg('score'), count=Count('id'))
        question.rating_average = result['avg'] or 0.0
        question.rating_count = result['count'] or 0
        question.save(update_fields=['rating_average', 'rating_count'])
        
        return Response({
            "status": "success",
            "rating_average": question.rating_average,
            "rating_count": question.rating_count,
            "user_rating": score
        })

    @action(detail=False, methods=['get'])
    def statistics(self, request):
        from datetime import date, timedelta, datetime
        from django.db.models import Count, Avg
        from django.db.models.functions import TruncDate, ExtractWeekDay

        total_votes = Answer.objects.count()
        anonymous_votes = Answer.objects.filter(is_anonymous=True).count()
        registered_votes = Answer.objects.filter(is_anonymous=False).count()
        
        # Votos por categoría
        votes_by_category = Answer.objects.values('question__category__name').annotate(count=Count('id')).order_by('-count')
        
        # Preguntas por categoría
        questions_by_category = Question.objects.values('category__name').annotate(count=Count('id')).order_by('-count')
        
        # Edad promedio y distribución de género (Usuarios únicos)
        
        # Calcular edad promedio de usuarios
        current_year = date.today().year
        avg_birth_year = Profile.objects.aggregate(Avg('birth_year'))['birth_year__avg']
        average_age = (current_year - avg_birth_year) if avg_birth_year else 0
        
        # Distribución de género (Usuarios únicos)
        gender_distribution = Profile.objects.values('gender').annotate(count=Count('id')).order_by('-count')

        # Total de usuarios
        total_users = Profile.objects.count()
        
        # Top 5 Preguntas más votadas
        top_questions = Question.objects.order_by('-cantidad_votos')[:5].values('title', 'cantidad_votos')
        
        # Votos por día (últimos 7 días)
        last_week = datetime.now() - timedelta(days=7)
        votes_over_time = Answer.objects.filter(question__creation_date__gte=last_week) \
            .annotate(date=TruncDate('question__creation_date')) \
            .values('date') \
            .annotate(count=Count('id')) \
            .order_by('date')

        # Votos por día de la semana (1=Domingo, 7=Sábado en Django ExtractWeekDay)
        votes_by_day = Answer.objects.annotate(day=ExtractWeekDay('question__creation_date')) \
            .values('day') \
            .annotate(count=Count('id')) \
            .order_by('day')
        
        return Response({
            "total_votes": total_votes,
            "total_users": total_users,
            "anonymous_votes": anonymous_votes,
            "registered_votes": registered_votes,
            "votes_by_category": list(votes_by_category),
            "average_age": round(average_age, 1),
            "gender_distribution": list(gender_distribution),
            "top_questions": list(top_questions),
            "votes_over_time": list(votes_over_time),
            "votes_by_day": list(votes_by_day),
            "questions_by_category": list(questions_by_category)
        })

class QuestionOptionViewSet(viewsets.ModelViewSet):
    queryset = QuestionOption.objects.all()
    serializer_class = QuestionOptionSerializer
    pagination_class = StandardResultsSetPagination
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'question__title']
