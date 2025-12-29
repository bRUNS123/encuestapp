# profiles/views.py
from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import Profile, Friendship
from .serializers import ProfileSerializer, LoginSerializer, FriendshipSerializer
from rest_framework.permissions import AllowAny, IsAuthenticated
from questions.models import Question
from answers.models import Answer
from questions.serializers import QuestionSerializer
from django.db.models import Q, Count
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import TokenAuthentication

from django.utils import timezone
from datetime import timedelta
from django.contrib.auth.hashers import make_password
import uuid

from django.core.mail import send_mail
from django.conf import settings

class PasswordResetViewSet(viewsets.ViewSet):
    """
    ViewSet to handle password reset via Email (SMTP).
    """
    
    @action(detail=False, methods=['post'])
    def request_reset(self, request):
        email = request.data.get('email')
        try:
            profile = Profile.objects.get(email=email)
            # Generate 6 digit code
            token = str(uuid.uuid4().int)[:6]
            profile.reset_token = token
            profile.reset_token_expire = timezone.now() + timedelta(minutes=15)
            profile.save()
            
            # Print to console for verification/debugging
            print(f"==========================================")
            print(f" PASSWORD RESET REQUEST FOR: {email}")
            print(f" CODE: {token}")
            print(f"==========================================")

            # Send Real Email
            try:
                send_mail(
                    subject='Código de Recuperación de Contraseña - DecideLibre',
                    message=f'Hola {profile.nickname or "Usuario"},\n\nTu código de recuperación es: {token}\n\nEste código expira en 15 minutos.',
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=False,
                )
                return Response({'message': 'Código enviado a tu correo.'}, status=status.HTTP_200_OK)
            except Exception as e:
                print(f"SMTP Error: {e}")
                # Fallback message if email fails but code was generated
                return Response({'message': 'Código generado (Error al enviar correo: Revisa la consola o configuración SMTP) '}, status=status.HTTP_200_OK)

        except Profile.DoesNotExist:
            return Response({'error': 'Email no encontrado'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=False, methods=['post'])
    def confirm_reset(self, request):
        email = request.data.get('email')
        token = request.data.get('code')
        new_password = request.data.get('password')
        
        try:
            profile = Profile.objects.get(email=email)
            
            if not profile.reset_token or profile.reset_token != token:
                return Response({'error': 'Código inválido'}, status=status.HTTP_400_BAD_REQUEST)
                
            if profile.reset_token_expire < timezone.now():
                return Response({'error': 'Código expirado'}, status=status.HTTP_400_BAD_REQUEST)
                
            profile.set_password(new_password)
            profile.reset_token = None
            profile.reset_token_expire = None
            profile.save()
            
            return Response({'message': 'Contraseña actualizada correctamente'}, status=status.HTTP_200_OK)
            
        except Profile.DoesNotExist:
            return Response({'error': 'Usuario no encontrado'}, status=status.HTTP_404_NOT_FOUND)

class ProfileViewSet(viewsets.ModelViewSet):

    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer

    def get_permissions(self):
        if self.action in ['register', 'login', 'list']:
            self.permission_classes = [AllowAny]
        else:
            self.permission_classes = [IsAuthenticated]
        return super().get_permissions()

    @action(detail=False, methods=['post'], url_path='register')
    def register(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['post'], url_path='login')
    def login(self, request):
        print("Login request data:", request.data)  # Debugging input data
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            print("User authenticated:", user)  # Debugging authenticated user
            return Response({
                "user": ProfileSerializer(user, context={'request': request}).data,
                "token": serializer.data.get('token')
            })
        print("Login validation errors:", serializer.errors)  # Debugging validation errors
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['get'], url_path='me', permission_classes=[IsAuthenticated])
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['patch'], url_path='update-profile')
    def update_profile(self, request):
        user = self.request.user
        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='questions', permission_classes=[IsAuthenticated])
    def get_user_questions(self, request):
        user = request.user
        answers = Answer.objects.filter(profile=user)
        question_ids = answers.values_list('question_id', flat=True)
        questions = Question.objects.filter(id__in=question_ids)
        serializer = QuestionSerializer(questions, many=True, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    # --- Friendship Actions ---

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated], url_path='friend-request')
    def send_friend_request(self, request, pk=None):
        target_user = self.get_object()
        user = request.user

        if user == target_user:
            return Response({"error": "Cannot friend yourself"}, status=status.HTTP_400_BAD_REQUEST)

        existing = Friendship.objects.filter(
            Q(sender=user, receiver=target_user) | Q(sender=target_user, receiver=user)
        ).first()

        if existing:
            if existing.accepted:
                 return Response({"status": "already_friends", "message": "Ya sois amigos"})
            if existing.sender == user:
                 return Response({"status": "request_already_sent", "message": "Solicitud ya enviada"})
            return Response({"status": "request_pending_from_them", "message": "Este usuario ya te envió solicitud"})

        Friendship.objects.create(sender=user, receiver=target_user)
        return Response({"status": "request_sent", "message": "Solicitud enviada"})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated], url_path='accept-friend')
    def accept_friend_request(self, request, pk=None):
        target_user = self.get_object()
        user = request.user

        friendship = Friendship.objects.filter(sender=target_user, receiver=user, accepted=False).first()
        if not friendship:
            return Response({"error": "No pending request"}, status=status.HTTP_404_NOT_FOUND)
        
        friendship.accepted = True
        friendship.save()
        return Response({"status": "accepted", "message": "Solicitud aceptada"})

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated], url_path='reject-friend')
    def reject_friend_request(self, request, pk=None):
        target_user = self.get_object()
        user = request.user

        deleted, _ = Friendship.objects.filter(
            Q(sender=target_user, receiver=user) | Q(sender=user, receiver=target_user)
        ).delete()
        
        return Response({"status": "removed" if deleted else "not_found", "message": "Amistad/Solicitud eliminada"})

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def friends(self, request):
        user = request.user
        friendships = Friendship.objects.filter(
            (Q(sender=user) | Q(receiver=user)) & Q(accepted=True)
        )
        friend_ids = []
        for f in friendships:
            friend_ids.append(f.sender_id if f.receiver == user else f.receiver_id)
        
        friends = Profile.objects.filter(id__in=friend_ids)
        serializer = ProfileSerializer(friends, many=True, context={'request': request})
        return Response(serializer.data)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated], url_path='friend-votes')
    def friend_votes(self, request, pk=None):
        target_user = self.get_object()
        user = request.user

        is_friend = Friendship.objects.filter(
            (Q(sender=user, receiver=target_user) | Q(sender=target_user, receiver=user)) & Q(accepted=True)
        ).exists()

        if not is_friend and user != target_user:
            return Response({"error": "No sois amigos"}, status=status.HTTP_403_FORBIDDEN)

        if not target_user.is_votes_visible and user != target_user:
            return Response({"error": "Este usuario mantiene sus votos privados."}, status=status.HTTP_403_FORBIDDEN)

        if user == target_user:
            answers = Answer.objects.filter(profile=target_user).select_related('question', 'chosen_option').order_by('-timestamp')
        else:
            answers = Answer.objects.filter(profile=target_user, is_public=True).select_related('question', 'chosen_option').order_by('-timestamp')
        
        data = []
        for ans in answers:
             q_data = QuestionSerializer(ans.question, context={'request': request}).data
             data.append({
                 'question': q_data,
                 'friend_vote_id': ans.chosen_option.id if ans.chosen_option else None,
                 'voted_at': ans.timestamp
             })

        return Response(data)

    # --- End Friendship Actions ---

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def compatibility(self, request):
        current_user = request.user
        
        # 1. Get Friends IDs
        friendships = Friendship.objects.filter(
            (Q(sender=current_user) | Q(receiver=current_user)) & Q(accepted=True)
        )
        friend_ids = []
        for f in friendships:
            friend_ids.append(f.sender_id if f.receiver == current_user else f.receiver_id)

        if not friend_ids:
            return Response([])

        my_answers = Answer.objects.filter(profile=current_user).values('question_id', 'chosen_option_id')
        my_answers_dict = {a['question_id']: a['chosen_option_id'] for a in my_answers}
        
        if not my_answers_dict:
             return Response([])

        relevant_questions = my_answers_dict.keys()
        
        other_answers = Answer.objects.filter(
            question_id__in=relevant_questions,
            profile__id__in=friend_ids
        ).select_related('profile')
        
        grouped_matches = {} 
        
        for ans in other_answers:
            user_id = ans.profile.id
            if user_id == current_user.id: continue

            if user_id not in grouped_matches:
                grouped_matches[user_id] = {
                    'matches': 0, 
                    'total_common': 0, 
                    'email': ans.profile.email,
                    'nickname': ans.profile.nickname,
                    'user_id': user_id
                }
            
            grouped_matches[user_id]['total_common'] += 1
            if my_answers_dict[ans.question_id] == ans.chosen_option_id:
                grouped_matches[user_id]['matches'] += 1
                
        # Obtener conteo total de votos para dar contexto
        matched_user_ids = list(grouped_matches.keys())
        friend_votes_map = {}
        if matched_user_ids:
            # Contar votos totales de estos amigos
            votes_query = Answer.objects.filter(profile__id__in=matched_user_ids).values('profile_id').annotate(total=Count('id'))
            friend_votes_map = {v['profile_id']: v['total'] for v in votes_query}

        compatibility_scores = []
        for match_data in grouped_matches.values():
            if match_data['matches'] > 0:
                percentage = (match_data['matches'] / match_data['total_common']) * 100
                total_votes = friend_votes_map.get(match_data['user_id'], 0)

                compatibility_scores.append({
                    'id': match_data['user_id'],
                    'type': 'user',
                    'email': match_data['email'],
                    'nickname': match_data['nickname'] if match_data['nickname'] else 'Usuario',
                    'score': round(percentage, 0),
                    'matches': match_data['matches'],
                    'common_count': match_data['total_common'],
                    'friend_total_votes': total_votes # Dato extra
                })
        
        # Sort by matches count descending, then percentage
        compatibility_scores.sort(key=lambda x: (x['matches'], x['score']), reverse=True)
        
        return Response(compatibility_scores[:50])

    @action(detail=True, methods=['get'], 
            permission_classes=[IsAuthenticated], 
            authentication_classes=[JWTAuthentication, TokenAuthentication],
            url_path='compatibility-details')
    def compatibility_details(self, request, pk=None):
        current_user = request.user
        target_id = pk # pk viene de la URL /profiles/{id}/compatibility-details/
        target_type = request.query_params.get('target_type', 'user')
        # target_id is pk
        
        if not target_id: 
             return Response({"error": "Missing target_id"}, status=status.HTTP_400_BAD_REQUEST)

        # Fallback if target_type missing, assume user
        if not target_type:
             target_type = 'user'

        my_answers = Answer.objects.filter(profile=current_user).select_related('question', 'chosen_option')
        my_answers_dict = {a.question_id: a for a in my_answers}

        if target_type == 'user':
            their_answers = Answer.objects.filter(profile_id=target_id, question_id__in=my_answers_dict.keys()).select_related('chosen_option')
        else:
            their_answers = Answer.objects.filter(anonymous_token=target_id, question_id__in=my_answers_dict.keys()).select_related('chosen_option')

        matching_details = []
        # Optimización: Obtener todos los IDs necesarios primero para evitar N+1 queries si select_related falla
        # Aunque select_related debería funcionar, esto es más explícito
        
        print(f"DEBUG: Processing {len(their_answers)} shared answers")
        
        for their_ans in their_answers:
            my_ans = my_answers_dict.get(their_ans.question_id)
            
            if my_ans and my_ans.chosen_option_id == their_ans.chosen_option_id:
                # Acceso explícito a atributos para forzar carga
                q_title = my_ans.question.title
                o_title = my_ans.chosen_option.title
                c_name = "General"
                
                try:
                    if my_ans.question.category:
                        c_name = my_ans.question.category.name
                except Exception:
                    pass
                
                # Fallback si están vacíos
                if not q_title: q_title = "Pregunta sin título"
                if not o_title: o_title = "Opción sin título"
                
                item = {
                    'question': str(q_title), 
                    'option': str(o_title),
                    'category': str(c_name)
                }
                matching_details.append(item)
        
        return Response(matching_details)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated], url_path='compatibility')
    def calculate_compatibility(self, request):
        """Calculate compatibility with all other users based on shared votes"""
        current_user = request.user
        
        # Get current user's answers
        my_answers = Answer.objects.filter(profile=current_user).select_related('question', 'chosen_option')
        my_answers_dict = {ans.question_id: ans for ans in my_answers}
        
        if not my_answers_dict:
            return Response([])
        
        # Get only friends (bidirectional check)
        friends_as_sender = Friendship.objects.filter(sender=current_user, accepted=True).values_list('receiver_id', flat=True)
        friends_as_receiver = Friendship.objects.filter(receiver=current_user, accepted=True).values_list('sender_id', flat=True)
        friend_ids = set(list(friends_as_sender) + list(friends_as_receiver))
        
        if not friend_ids:
            return Response([])
        
        # Get only friend users who have voted
        friends = Profile.objects.filter(id__in=friend_ids, answer__isnull=False).distinct()
        
        compatibility_list = []
        
        for friend in friends:
            # Get their answers
            their_answers = Answer.objects.filter(profile=friend).select_related('question', 'chosen_option')
            
            # Calculate matches
            total_common_questions = 0
            matching_votes = 0
            
            for their_ans in their_answers:
                if their_ans.question_id in my_answers_dict:
                    total_common_questions += 1
                    my_ans = my_answers_dict[their_ans.question_id]
                    if my_ans.chosen_option_id == their_ans.chosen_option_id:
                        matching_votes += 1
            
            # Only include if they have common questions
            if total_common_questions > 0:
                compatibility_percentage = int((matching_votes / total_common_questions) * 100)
                compatibility_list.append({
                    'id': friend.id,
                    'email': friend.email if friend.is_email_public else None,
                    'nickname': friend.nickname,
                    'compatibility': compatibility_percentage,
                    'matching_votes': matching_votes,
                    'total_common': total_common_questions,
                    'type': 'user',
                    'is_friend': True
                })
        
        # Sort by compatibility descending
        compatibility_list.sort(key=lambda x: x['compatibility'], reverse=True)
        
        return Response(compatibility_list)

# Social Auth
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialLoginView

class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter
    callback_url = "http://localhost:5173"
    client_class = OAuth2Client

class FacebookLogin(SocialLoginView):
    adapter_class = FacebookOAuth2Adapter
    callback_url = "http://localhost:5176"
    client_class = OAuth2Client
