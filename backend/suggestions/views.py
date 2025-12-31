from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Suggestion
from .serializers import SuggestionSerializer
from django.db.models import Count

class SuggestionViewSet(viewsets.ModelViewSet):
    # Sort by creation date descending by default, preventing issues with aggregation
    queryset = Suggestion.objects.all().order_by('-created_at')
    serializer_class = SuggestionSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def get_queryset(self):
        queryset = super().get_queryset()
        ordering = self.request.query_params.get('ordering', '-created_at')
        if ordering == 'likes':
             return queryset.annotate(count_likes=Count('likes')).order_by('-count_likes', '-created_at')
        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def toggle_like(self, request, pk=None):
        suggestion = self.get_object()
        user = request.user
        if suggestion.likes.filter(id=user.id).exists():
            suggestion.likes.remove(user)
            liked = False
        else:
            suggestion.likes.add(user)
            liked = True
        return Response({'liked': liked, 'likes_count': suggestion.likes.count()})
