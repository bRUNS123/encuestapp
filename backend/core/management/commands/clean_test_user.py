from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Deletes a specific user and their data'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, help='Email of the user to delete', required=True)

    def handle(self, *args, **options):
        User = get_user_model()
        email = options['email']

        try:
            user = User.objects.get(email=email)
            user.delete()
            self.stdout.write(self.style.SUCCESS(f'Successfully deleted user "{email}" and associated data'))
        except User.DoesNotExist:
            self.stdout.write(self.style.WARNING(f'User "{email}" does not exist'))
