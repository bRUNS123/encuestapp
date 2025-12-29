import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = "Creates an admin user non-interactively if it doesn't exist"

    def handle(self, *args, **options):
        User = get_user_model()
        email = os.environ.get('ADMIN_EMAIL')
        password = os.environ.get('ADMIN_PASSWORD')

        if not email or not password:
            self.stdout.write(self.style.WARNING('ADMIN_EMAIL or ADMIN_PASSWORD not set in environment. Skipping admin creation.'))
            return

        user_exists = User.objects.filter(email=email).exists()

        if user_exists:
            self.stdout.write(self.style.SUCCESS(f'User "{email}" already exists. Ensuring admin privileges and updating password...'))
            user = User.objects.get(email=email)
            user.set_password(password)
            user.is_staff = True
            user.is_superuser = True
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Successfully updated "{email}" to admin with new password.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Creating new superuser "{email}"...'))
            User.objects.create_superuser(email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f'Successfully created superuser "{email}".'))
