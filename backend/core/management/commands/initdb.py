from django.core.management.base import BaseCommand
from django.core.management import call_command
from io import StringIO


class Command(BaseCommand):
    help = 'Initialize database with all necessary data (run after migrations)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('=' * 60))
        self.stdout.write(self.style.SUCCESS('🚀 Starting Database Initialization'))
        self.stdout.write(self.style.SUCCESS('=' * 60))
        
        # 1. Create admin user if needed
        self.stdout.write('\n📋 Step 1: Checking admin user...')
        try:
            out = StringIO()
            call_command('initadmin', stdout=out)
            self.stdout.write(out.getvalue())
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'⚠️  Admin initialization skipped: {e}'))
        
        # 2. Load personal questions
        self.stdout.write('\n📋 Step 2: Loading personal questions...')
        try:
            out = StringIO()
            call_command('load_personal_questions', stdout=out)
            self.stdout.write(out.getvalue())
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Failed to load personal questions: {e}'))
            # Don't fail the entire process
        
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('✅ Database initialization complete!'))
        self.stdout.write('=' * 60)
