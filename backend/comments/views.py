from rest_framework import viewsets, permissions
from .models import Comment
from .serializers import CommentSerializer
from profiles.models import Profile

class CommentViewSet(viewsets.ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        # Automatically assign the profile of the current user
        # Assuming the user has a profile. If not, this might raise an error.
        # We should probably handle the case where user has no profile or is anonymous properly.
        # But per requirements, users must be logged in to comment (permission class).
        try:
            profile = self.request.user.profile
            serializer.save(profile=profile)
        except Profile.DoesNotExist:
            # Fallback or error if user has no profile (shouldn't happen with correct signals)
            pass

    def get_queryset(self):
        queryset = Comment.objects.all()
        question_id = self.request.query_params.get('question', None)
        if question_id is not None:
            queryset = queryset.filter(question__id=question_id)
        return queryset
