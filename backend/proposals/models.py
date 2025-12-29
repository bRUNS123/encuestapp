from django.db import models
from profiles.models import Profile
from categories.models import Category

class ProposedQuestion(models.Model):
    """
    Model for community-proposed questions that need approval
    """
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    creator = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='proposed_questions')
    title = models.CharField(max_length=500)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    option1_text = models.CharField(max_length=200)
    option2_text = models.CharField(max_length=200)
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    votes_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.title} by {self.creator.email} - {self.status}"
    
    def check_approval(self):
        """
        Check if proposal should be auto-approved
        Requires 33% of total users OR minimum 20 votes
        """
        from profiles.models import Profile
        total_users = Profile.objects.count()
        threshold = max(20, int(total_users * 0.33))
        
        if self.votes_count >= threshold and self.status == 'pending':
            self.approve_and_create_question()
            
    def approve_and_create_question(self):
        """
        Approve proposal and create actual Question
        """
        from questions.models import Question, QuestionOption
        from datetime import datetime, timedelta
        
        # Create the approved question
        question = Question.objects.create(
            title=self.title,
            category=self.category,
            creation_date=datetime.now(),
            expiration_date=datetime.now() + timedelta(days=30),
            cantidad_votos=0
        )
        
        # Create options
        QuestionOption.objects.create(
            question=question,
            title=self.option1_text,
            votes=0
        )
        QuestionOption.objects.create(
            question=question,
            title=self.option2_text,
            votes=0
        )
        
        # Update proposal status
        self.status = 'approved'
        self.approved_at = datetime.now()
        self.save()


class ProposalVote(models.Model):
    """
    Track who voted for which proposal
    """
    proposal = models.ForeignKey(ProposedQuestion, on_delete=models.CASCADE, related_name='votes')
    voter = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='proposal_votes')
    voted_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['proposal', 'voter']
        
    def __str__(self):
        return f"{self.voter.email} voted for '{self.proposal.title}'"
