#!/usr/bin/env python
"""Script to update expiration dates for all existing questions"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from questions.models import Question
from datetime import timedelta

def update_expiration_dates():
    """Update all questions to have expiration_date = creation_date + 7 days"""
    questions = Question.objects.all()
    total = questions.count()
    updated = 0
    
    print(f"Found {total} questions to update...")
    
    for question in questions:
        if not question.expiration_date:  # Only update if not already set
            question.expiration_date = question.creation_date + timedelta(days=7)
            question.save()
            updated += 1
            if updated % 10 == 0:
                print(f"Updated {updated}/{total}...")
    
    print(f"\n✅ Successfully updated {updated} questions!")
    print(f"All questions now have expiration date set to 1 week from creation.")
    
    # Verify
    with_expiration = Question.objects.filter(expiration_date__isnull=False).count()
    print(f"Verification: {with_expiration}/{total} questions have expiration dates")

if __name__ == '__main__':
    update_expiration_dates()
