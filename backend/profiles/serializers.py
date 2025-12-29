# profiles/serializers.py
from rest_framework import serializers
from django.db.models import Q
from .models import Profile, Friendship
from rest_framework_simplejwt.tokens import RefreshToken

class ProfileSerializer(serializers.ModelSerializer):
    friendship_status = serializers.SerializerMethodField()
    votes_count = serializers.SerializerMethodField()
    friends_count = serializers.SerializerMethodField()

    photo_url = serializers.SerializerMethodField()
    is_staff = serializers.BooleanField(read_only=True)

    class Meta:
        model = Profile
        fields = '__all__'
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def get_photo_url(self, obj):
        if not obj.email:
            return None
        import hashlib
        # Normalize email and generate MD5
        email_hash = hashlib.md5(obj.email.lower().strip().encode('utf-8')).hexdigest()
        # Return Gravatar URL (d=mp for mystery person or identicon)
        return f"https://www.gravatar.com/avatar/{email_hash}?d=mp&s=200"

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        request = self.context.get('request')
        
        # If no request or viewing own profile, return everything
        if not request or (request.user.is_authenticated and request.user == instance):
            return ret

        # Hide private fields for others
        privacy_fields = [
            ('is_birth_year_public', 'birth_year'),
            ('is_gender_public', 'gender'),
            ('is_email_public', 'email'),
            ('is_civil_status_public', 'civil_status'),
            ('is_nationality_public', 'nationality'),
            ('is_birth_date_public', 'birth_date'),
            ('is_profession_public', 'profession'),
            ('is_education_level_public', 'education_level'),
            ('is_employment_status_public', 'employment_status'),
            ('is_religion_public', 'religion'),
            ('is_political_tendency_public', 'political_tendency'),
            ('is_housing_type_public', 'housing_type'),
            ('is_health_insurance_public', 'health_insurance'),
        ]

        # Requirement: "solo lo verán los miembros (logueados)"
        # If the requester is NOT authenticated, they see NONE of these fields.
        is_requester_authenticated = request and request.user and request.user.is_authenticated

        for public_flag, field_name in privacy_fields:
            # Visible if: (Requester is Authenticated AND Field is Public) OR (Requester is Staff)
            is_staff = request and request.user.is_staff
            if not (is_staff or (is_requester_authenticated and getattr(instance, public_flag))):
                 ret[field_name] = None

            
        return ret

    def get_votes_count(self, obj):
        return obj.answer_set.count()

    def get_friends_count(self, obj):
        return Friendship.objects.filter(
            (Q(sender=obj) | Q(receiver=obj)) & Q(accepted=True)
        ).count()

    def get_friendship_status(self, obj):
        request = self.context.get('request')
        if not request or not request.user.is_authenticated:
            return 'none'
        
        user = request.user
        if user == obj:
            return 'self'

        # Check friendship
        friendship = Friendship.objects.filter(
            Q(sender=user, receiver=obj) | Q(sender=obj, receiver=user)
        ).first()

        if not friendship:
            return 'none'
        
        if friendship.accepted:
            return 'friends'
        
        if friendship.sender == user:
            return 'pending_sent'
        
        return 'pending_received'

    def create(self, validated_data):
        user = Profile.objects.create_user(
            email=validated_data['email'],
            password=validated_data['password'],
            birth_year=validated_data['birth_year'],
            gender=validated_data['gender'],
            nickname=validated_data.get('nickname')
        )
        return user

class FriendshipSerializer(serializers.ModelSerializer):
    sender = ProfileSerializer(read_only=True)
    receiver = ProfileSerializer(read_only=True)

    class Meta:
        model = Friendship
        fields = '__all__'

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    token = serializers.SerializerMethodField()

    def get_token(self, obj):
        user = obj.get('user')
        if user:
            refresh = RefreshToken.for_user(user)
            return {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }
        return None

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        print("Validating login for email:", email)  # Debugging input email

        if email and password:
            user = Profile.objects.filter(email=email).first()
            print("User found:", user)  # Debugging user existence
            if user and user.check_password(password):
                print("Password is valid for user:", user)  # Debugging password validation
                data['user'] = user
                return data
            else:
                print("Invalid credentials for user:", email)  # Debugging invalid credentials
                raise serializers.ValidationError("Invalid credentials")
        else:
            raise serializers.ValidationError("Must include 'email' and 'password'")
