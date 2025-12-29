
import os
import sys
import django

sys.path.append('backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from answers.models import Answer
from profiles.models import Profile

with open('votes_log.txt', 'w', encoding='utf-8') as f:
    f.write("--- Vote Inspection ---\n")
    current_users = Profile.objects.all()
    f.write(f"Total Profiles: {current_users.count()}\n")

    for user in current_users:
        count = Answer.objects.filter(profile=user).count()
        f.write(f"User: {user.email} (ID: {user.id}) - Votes: {count}\n")
        
    f.write("-" * 30 + "\n")
    anon_count = Answer.objects.filter(is_anonymous=True).count()
    f.write(f"Anonymous Votes: {anon_count}\n")
    f.write("-" * 30 + "\n")
    registered_votes_without_profile = Answer.objects.filter(is_anonymous=False, profile__isnull=True).count()
    f.write(f"Registered Votes (is_anonymous=False) but profile is NULL: {registered_votes_without_profile}\n")
