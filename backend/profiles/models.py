from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
import random

class ProfileManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        
        # Generar nickname automático si no se proporciona
        if not extra_fields.get('nickname'):
            adjectives = ['Rápido', 'Sabio', 'Valiente', 'Astuto', 'Brillante', 'Genial', 'Noble', 'Audaz']
            nouns = ['Panda', 'León', 'Águila', 'Tigre', 'Delfín', 'Lobo', 'Halcón', 'Zorro']
            while True:
                nickname = f"{random.choice(adjectives)}{random.choice(nouns)}{random.randint(1, 999)}"
                if not self.model.objects.filter(nickname=nickname).exists():
                    extra_fields['nickname'] = nickname
                    break
        
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(email, password, **extra_fields)

class Profile(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    nickname = models.CharField(max_length=50, blank=True, null=True, unique=True)
    birth_year = models.IntegerField(null=True)
    gender = models.CharField(max_length=10, null=True)
    is_votes_visible = models.BooleanField(default=True)
    is_gender_public = models.BooleanField(default=True)
    is_birth_year_public = models.BooleanField(default=True)
    is_email_public = models.BooleanField(default=False)  # Email oculto por defecto

    # Nuevos campos de perfil (10 preguntas)

    employment_status = models.CharField(max_length=100, blank=True, null=True)
    is_employment_status_public = models.BooleanField(default=False)

    religion = models.CharField(max_length=50, blank=True, null=True)
    is_religion_public = models.BooleanField(default=False)

    political_tendency = models.CharField(max_length=100, blank=True, null=True)
    is_political_tendency_public = models.BooleanField(default=False)

    housing_type = models.CharField(max_length=50, blank=True, null=True)
    is_housing_type_public = models.BooleanField(default=False)

    health_insurance = models.CharField(max_length=50, blank=True, null=True)
    is_health_insurance_public = models.BooleanField(default=False)

    # Missing fields added for consistency with Serializer
    civil_status = models.CharField(max_length=50, blank=True, null=True)
    is_civil_status_public = models.BooleanField(default=False)

    nationality = models.CharField(max_length=50, blank=True, null=True)
    is_nationality_public = models.BooleanField(default=False)

    birth_date = models.DateField(null=True, blank=True)
    is_birth_date_public = models.BooleanField(default=False)

    profession = models.CharField(max_length=100, blank=True, null=True)
    is_profession_public = models.BooleanField(default=False)

    education_level = models.CharField(max_length=100, blank=True, null=True)
    is_education_level_public = models.BooleanField(default=False)

    # Password Reset fields
    reset_token = models.CharField(max_length=100, blank=True, null=True)
    reset_token_expire = models.DateTimeField(null=True, blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = ProfileManager()

    class Meta:
        ordering = ['email']

class Friendship(models.Model):
    sender = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='sent_requests')
    receiver = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='received_requests')
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)

    class Meta:
        unique_together = ('sender', 'receiver')