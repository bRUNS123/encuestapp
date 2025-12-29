from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
import os

class Command(BaseCommand):
    help = 'Creates an admin user if one does not exist'

    def handle(self, *args, **options):
        User = get_user_model()
        # Default to email since username is None in Profile model
        email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
        password = os.environ.get('DJANGO_SUPERUSER_PASSWORD', 'admin123')

        if not User.objects.filter(email=email).exists():
            User.objects.create_superuser(email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f'Successfully created superuser "{email}"'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Superuser "{email}" already exists'))
