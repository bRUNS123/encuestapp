from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from .models import ProposedQuestion, ProposalVote
from .serializers import ProposedQuestionSerializer, ProposedQuestionCreateSerializer


class ProposedQuestionViewSet(viewsets.ModelViewSet):
    queryset = ProposedQuestion.objects.all()
    serializer_class = ProposedQuestionSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        """Filter to show only pending proposals by default"""
        status_filter = self.request.query_params.get('status', 'pending')
        if status_filter:
            return ProposedQuestion.objects.filter(status=status_filter)
        return ProposedQuestion.objects.all()
    
    def get_serializer_class(self):
        if self.action == 'create':
            return ProposedQuestionCreateSerializer
        return ProposedQuestionSerializer
    
    def perform_create(self, serializer):
        """Set creator when creating proposal"""
        serializer.save(creator=self.request.user)
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def vote(self, request, pk=None):
        """
        Vote for a proposal
        """
        proposal = self.get_object()
        
        # Check if already voted
        if ProposalVote.objects.filter(proposal=proposal, voter=request.user).exists():
            return Response(
                {"error": "Ya has votado por esta propuesta"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if proposal is still pending
        if proposal.status != 'pending':
            return Response(
                {"error": "Esta propuesta ya fue procesada"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create vote
        ProposalVote.objects.create(proposal=proposal, voter=request.user)
        
        # Update vote count
        proposal.votes_count += 1
        proposal.save()
        
        # Check if should be auto-approved
        proposal.check_approval()
        proposal.refresh_from_db()
        
        serializer = self.get_serializer(proposal)
        return Response({
            "message": "Voto registrado exitosamente",
            "proposal": serializer.data,
            "auto_approved": proposal.status == 'approved'
        })
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get statistics about proposals
        """
        from profiles.models import Profile
        
        total_users = Profile.objects.count()
        threshold = max(20, int(total_users * 0.33))
        
        pending_count = ProposedQuestion.objects.filter(status='pending').count()
        approved_count = ProposedQuestion.objects.filter(status='approved').count()
        
        return Response({
            'total_users': total_users,
            'approval_threshold': threshold,
            'pending_proposals': pending_count,
            'approved_proposals': approved_count
        })
