#!/usr/bin/env python
"""Script to create a test user with many votes and friendship with bfrancosentis@gmail.com"""
import os
import django
import random

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from profiles.models import Profile, Friendship
from questions.models import Question
from answers.models import Answer

def create_test_user_with_votes():
    """Create a test user with many votes and friendship"""
    
    # Find bfrancosentis
    try:
        bruno = Profile.objects.get(email='bfrancosentis@gmail.com')
        print(f"✓ Found user: {bruno.email}")
    except Profile.DoesNotExist:
        print("✗ Error: bfrancosentis@gmail.com not found!")
        return
    
    # Create test user
    test_email = 'amigo.test@example.com'
    
    # Delete if exists
    Profile.objects.filter(email=test_email).delete()
    
    test_user = Profile.objects.create_user(
        email=test_email,
        password='testpass123',
        nickname='AmigoTester',
        birth_year=1995,
        gender='Masculino'
    )
    print(f"✓ Created user: {test_user.email} (nickname: {test_user.nickname})")
    
    # Get all questions
    questions = list(Question.objects.all())
    print(f"✓ Found {len(questions)} questions")
    
    # Create votes for random questions (let's vote on 30-40 questions)
    num_votes = min(random.randint(30, 40), len(questions))
    voted_questions = random.sample(questions, num_votes)
    
    votes_created = 0
    for question in voted_questions:
        options = list(question.options.all())
        if len(options) >= 2:
            chosen_option = random.choice(options)
            
            # Create vote
            Answer.objects.create(
                profile=test_user,
                question=question,
                chosen_option=chosen_option,
                is_anonymous=False,
                is_public=True
            )
            
            # Update vote counts
            chosen_option.votes += 1
            chosen_option.save()
            question.cantidad_votos += 1
            question.save()
            
            votes_created += 1
    
    print(f"✓ Created {votes_created} votes for test user")
    
    # Create friendship (bidirectional)
    # Delete existing friendships if any
    Friendship.objects.filter(sender=bruno, receiver=test_user).delete()
    Friendship.objects.filter(sender=test_user, receiver=bruno).delete()
    
    # Create friendship from bruno to test_user
    friendship = Friendship.objects.create(
        sender=bruno,
        receiver=test_user,
        accepted=True
    )
    print(f"✓ Created friendship: {bruno.email} <-> {test_user.email}")
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY:")
    print("="*60)
    print(f"Test User Email: {test_user.email}")
    print(f"Test User Nickname: {test_user.nickname}")
    print(f"Password: testpass123")
    print(f"Total Votes: {votes_created}")
    print(f"Friend of: {bruno.email}")
    print(f"Friendship Status: Accepted ✓")
    print("="*60)
    print("\n✅ You can now login with this user to test compatibility!")

if __name__ == '__main__':
    create_test_user_with_votes()
