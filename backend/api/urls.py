from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from rest_framework_nested import routers
from .views import (
    signup, login, logout,
    TranscriptViewSet,
    QuestionViewSet,
    get_practice_sets,
    get_practice_questions,
    submit_answer,
    get_transcript_by_video
)

# Create main router
router = DefaultRouter()
router.register(r'transcripts', TranscriptViewSet, basename='transcript')

# Create nested router for questions
questions_router = routers.NestedSimpleRouter(router, r'transcripts', lookup='transcript')
questions_router.register(r'questions', QuestionViewSet, basename='transcript-question')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(questions_router.urls)),
    path('auth/signup/', signup, name='signup'),
    path('auth/login/', login, name='login'),
    path('auth/logout/', logout, name='logout'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Practice endpoints
    path('practice/sets/', get_practice_sets, name='practice-sets'),
    path('practice/questions/<str:video_id>/<str:question_type>/', get_practice_questions, name='practice-questions'),
    path('practice/submit/<str:question_id>/', submit_answer, name='submit-answer'),
    
    # Direct transcript access
    path('transcripts/<str:video_id>/', get_transcript_by_video, name='get-transcript-by-video'),
] 