from django.urls import path, include, re_path
from rest_framework import routers
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

from profiles.views import ProfileViewSet
from questions.views import QuestionViewSet, QuestionOptionViewSet
from answers.views import AnswerViewSet
from categories.views import CategoryViewSet
from comments.views import CommentViewSet
from proposals.views import ProposedQuestionViewSet
from profiles.views import ProfileViewSet, PasswordResetViewSet, GoogleLogin, FacebookLogin

router = routers.DefaultRouter()
router.register(r'profiles', ProfileViewSet)
router.register(r'questions', QuestionViewSet)
router.register(r'question-options', QuestionOptionViewSet)
router.register(r'answers', AnswerViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'comments', CommentViewSet)
router.register(r'proposals', ProposedQuestionViewSet)
router.register(r'password-reset', PasswordResetViewSet, basename='password-reset')

urlpatterns = [
    # API Routes prefixed with /api/
    path('api/', include(router.urls)),
    path('api/auth/', include('dj_rest_auth.urls')),
    path('api/auth/registration/', include('dj_rest_auth.registration.urls')),
    path('api/accounts/', include('allauth.urls')),
    path('api/auth/google/', GoogleLogin.as_view(), name='google_login'),
    path('api/auth/facebook/', FacebookLogin.as_view(), name='facebook_login'),
    path('api/suggestions/', include('suggestions.urls')),
]

# Serve static files manual configuration for debug
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])

# Catch-all MUST BE LAST
urlpatterns += [
    re_path(r'^.*$', TemplateView.as_view(template_name='index.html')),
]
