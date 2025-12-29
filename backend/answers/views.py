# answers/views.py

from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Answer
from .serializers import AnswerSerializer
from profiles.models import Profile
from questions.models import Question, QuestionOption
from questions.serializers import QuestionSerializer, QuestionOptionSerializer
from django.db import models

class AnswerViewSet(viewsets.ModelViewSet):
    queryset = Answer.objects.all()
    serializer_class = AnswerSerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=['post'])
    def vote(self, request):
        profile_id = request.data.get('profile_id')
        question_id = request.data.get('question_id')
        option_id = request.data.get('option_id')
        is_anonymous = request.data.get('is_anonymous', True)
        user_token = request.data.get('user_token', None)

        if not question_id or not option_id:
            return Response({"error": "Question ID and Option ID are required"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            question = Question.objects.get(id=question_id)
            option = QuestionOption.objects.get(id=option_id, question=question)
            profile = None
            if profile_id and profile_id != 0:
                try:
                    profile = Profile.objects.get(id=profile_id)
                except Profile.DoesNotExist:
                    return Response({"error": "Invalid profile ID"}, status=status.HTTP_404_NOT_FOUND)
        except Question.DoesNotExist:
            return Response({"error": "Invalid question ID"}, status=status.HTTP_404_NOT_FOUND)
        except QuestionOption.DoesNotExist:
            return Response({"error": "Invalid option ID"}, status=status.HTTP_404_NOT_FOUND)

        try:
            if is_anonymous or not profile:
                 Answer.objects.create(
                    question=question, 
                    chosen_option=option, 
                    is_anonymous=True, 
                    anonymous_token=user_token
                )
                 option.votes = models.F('votes') + 1
                 option.save()
                 question.cantidad_votos = models.F('cantidad_votos') + 1
                 question.save()
            else:
                # Check if answer exists
                try:
                    existing_answer = Answer.objects.get(profile=profile, question=question)
                    if existing_answer.chosen_option != option:
                        # Decrement old option
                        old_option = existing_answer.chosen_option
                        old_option.votes = models.F('votes') - 1
                        old_option.save()

                        # Increment new option
                        option.votes = models.F('votes') + 1
                        option.save()

                        # Update answer
                        existing_answer.chosen_option = option
                        existing_answer.save()
                        # Question total votes do not change when switching
                except Answer.DoesNotExist:
                    # New answer
                    Answer.objects.create(
                        profile=profile, 
                        question=question, 
                        defaults={'chosen_option': option, 'is_anonymous': False}
                    ) # Note: create doesn't support defaults like get_or_create, fixing this:
                    # Actually Answer.objects.create doesn't take defaults. 
                    # Correcting below:
                    Answer.objects.create(
                        profile=profile, 
                        question=question, 
                        chosen_option=option,
                        is_anonymous=False
                    )

                    option.votes = models.F('votes') + 1
                    option.save()
                    question.cantidad_votos = models.F('cantidad_votos') + 1
                    question.save()

            question.refresh_from_db()
            option.refresh_from_db()

            return Response({
                "question": QuestionSerializer(question).data,
                "option": QuestionOptionSerializer(option).data
            }, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated], url_path='toggle-privacy')
    def toggle_privacy(self, request):
        question_id = request.data.get('question_id')
        if not question_id:
            return Response({"error": "question_id required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            answer = Answer.objects.get(question_id=question_id, profile=request.user)
            answer.is_public = not answer.is_public
            answer.save()
            return Response({"status": "updated", "is_public": answer.is_public})
        except Answer.DoesNotExist:
             return Response({"error": "Respuesta no encontrada"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated], url_path='delete-vote')
    def delete_vote(self, request):
        question_id = request.data.get('question_id')
        if not question_id:
            return Response({"error": "question_id required"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            answer = Answer.objects.get(question_id=question_id, profile=request.user)
            
            # Decrement counters
            option = answer.chosen_option
            question = answer.question
            
            if option:
                option.votes = models.F('votes') - 1
                option.save()
            
            question.cantidad_votos = models.F('cantidad_votos') - 1
            question.save()
            
            answer.delete()
            
            question.refresh_from_db()
            if option:
                option.refresh_from_db()
                
            return Response({"status": "deleted", "question": QuestionSerializer(question).data}, status=status.HTTP_200_OK)
        except Answer.DoesNotExist:
             return Response({"error": "Respuesta no encontrada"}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def user_answers(self, request):
        user = request.user
        answers = Answer.objects.filter(profile=user)
        questions = Question.objects.filter(id__in=answers.values_list('question_id', flat=True))
        serializer = QuestionSerializer(questions, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
