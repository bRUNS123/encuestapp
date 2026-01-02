from django.core.management.base import BaseCommand
from categories.models import Category
from questions.models import Question, QuestionOption
from datetime import datetime, timedelta
import json
import os


class Command(BaseCommand):
    help = 'Load Personal questions from questions.json into database'

    def handle(self, *args, **options):
        self.stdout.write('🚀 Loading Personal questions...')
        
        # Path to questions.json
        json_path = os.path.join(os.path.dirname(__file__), '../../../..', 'questions.json')
        
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Get the personal section
        sections = data.get('sections', [])
        personal_section = None
        for section in sections:
            if section.get('id', '').lower() == 'personal':
                personal_section = section
                break
        
        if not personal_section:
            self.stdout.write(self.style.ERROR('❌ Personal section not found in questions.json'))
            return
        
        # Create or get PERSONAL category
        category, created = Category.objects.get_or_create(
            name='PERSONAL',
            defaults={'description': personal_section.get('title', 'PERSONAL')}
        )
        
        if created:
            self.stdout.write(self.style.SUCCESS(f'✅ Created category: {category.name}'))
        else:
            self.stdout.write(f'📁 Using existing category: {category.name}')
        
        # Delete existing questions in this category
        deleted_count = Question.objects.filter(category=category).delete()[0]
        if deleted_count > 0:
            self.stdout.write(f'🗑️ Deleted {deleted_count} existing questions')
        
        # Load questions
        questions_data = personal_section.get('questions', [])
        created_questions = 0
        
        for q_data in questions_data:
            # Determine question type
            q_type = q_data.get('question_type', 'binary')
            options = q_data.get('options', [])
            
            # Map unsupported types to supported ones
            type_mapping = {
                'time': 'open',
                'datetime': 'open',
            }
            
            # Apply type mapping if type is unsupported
            if q_type in type_mapping:
                q_type = type_mapping[q_type]
            
            if not q_data.get('question_type'):
                if len(options) == 0:
                    q_type = 'open'
                elif len(options) == 2:
                    q_type = 'binary'
                elif any('min' in str(opt).lower() or 'max' in str(opt).lower() for opt in options):
                    q_type = 'slider'
                else:
                    q_type = 'dropdown'
            
            # Create question
            question = Question.objects.create(
                title=q_data['title'],
                category=category,
                question_type=q_type,
                creation_date=datetime.now(),
                expiration_date=datetime.now() + timedelta(days=365),  # 1 year expiry
                cantidad_votos=0
            )
            
            # Create options if present
            if options and q_type != 'open':
                for idx, option_data in enumerate(options):
                    if isinstance(option_data, dict):
                        option_title = option_data.get('title', f'Option {idx+1}')
                    else:
                        option_title = str(option_data)
                    
                    QuestionOption.objects.create(
                        question=question,
                        title=option_title,
                        votes=0
                    )
            
            created_questions += 1
        
        self.stdout.write(self.style.SUCCESS(f'✅ Successfully loaded {created_questions} Personal questions'))
        self.stdout.write(f'📊 Total questions in database: {Question.objects.count()}')
