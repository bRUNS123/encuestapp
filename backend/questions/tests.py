from django.test import TestCase
from rest_framework.test import APIClient
from rest_framework import status
from .models import Question, QuestionOption
from categories.models import Category
from profiles.models import Profile

class QuestionVoteTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.category = Category.objects.create(name="Test Category")
        self.question = Question.objects.create(title="Test Question", category=self.category)
        self.option1 = QuestionOption.objects.create(question=self.question, title="Option 1")
        self.option2 = QuestionOption.objects.create(question=self.question, title="Option 2")
        self.user = Profile.objects.create_user(email="test@example.com", password="password")

    def test_vote_authenticated(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post(f'/questions/{self.question.id}/vote/', {
            'option_id': self.option1.id,
            'profile_id': self.user.id
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.option1.refresh_from_db()
        self.question.refresh_from_db()
        self.assertEqual(self.option1.votes, 1)
        self.assertEqual(self.question.cantidad_votos, 1)

    def test_change_vote(self):
        self.client.force_authenticate(user=self.user)
        # Vote for option 1
        self.client.post(f'/questions/{self.question.id}/vote/', {
            'option_id': self.option1.id,
            'profile_id': self.user.id
        }, format='json')
        
        # Change to option 2
        response = self.client.post(f'/questions/{self.question.id}/vote/', {
            'option_id': self.option2.id,
            'profile_id': self.user.id
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        self.option1.refresh_from_db()
        self.option2.refresh_from_db()
        self.question.refresh_from_db()
        
        self.assertEqual(self.option1.votes, 0)
        self.assertEqual(self.option2.votes, 1)
        self.assertEqual(self.question.cantidad_votos, 1) # Total votes should stay 1

    def test_vote_anonymous(self):
        token = "some-random-token"
        response = self.client.post(f'/questions/{self.question.id}/vote/', {
            'option_id': self.option1.id,
            'is_anonymous': True,
            'user_token': token
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.option1.refresh_from_db()
        self.assertEqual(self.option1.votes, 1)
