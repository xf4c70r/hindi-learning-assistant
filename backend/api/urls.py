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
    get_transcript_by_video,
    query_word,
    get_user_words,
    toggle_word_favorite,
    update_word_notes,
    get_curated_videos,
    get_curated_video_detail,
    get_curated_video_topics,
    get_learning_paths,
    get_learning_path_detail,
    get_recommended_learning_paths,
    save_user_progress,
    get_user_progress,
    get_user_learning_stats,
    update_video_completion,
)

# Create main router
router = DefaultRouter()
router.register(r'transcripts', TranscriptViewSet, basename='transcript')

# Create nested router for questions
questions_router = routers.NestedSimpleRouter(router, r'transcripts', lookup='transcript')
questions_router.register(r'questions', QuestionViewSet, basename='transcript-question')

from .guided_views import start_session as guided_start_session, submit_answer as guided_submit_answer

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

    # Vocabulary endpoints
    path('vocabulary/query/', query_word, name='query-word'),
    path('vocabulary/words/', get_user_words, name='user-words'),
    path('words/<str:word_id>/toggle_favorite/', toggle_word_favorite, name='toggle_word_favorite'),
    path('words/<str:word_id>/update_notes/', update_word_notes, name='update_word_notes'),
    
    # Agentic Workflow - Curated Videos endpoints
    path('curated/videos/', get_curated_videos, name='curated-videos'),
    path('curated/videos/<str:video_id>/', get_curated_video_detail, name='curated-video-detail'),
    path('curated/topics/', get_curated_video_topics, name='curated-video-topics'),
    
    # Agentic Workflow - Learning Paths endpoints
    path('learning-paths/', get_learning_paths, name='learning-paths'),
    path('learning-paths/<str:path_id>/', get_learning_path_detail, name='learning-path-detail'),
    path('learning-paths/recommended/', get_recommended_learning_paths, name='recommended-learning-paths'),
    
    # Agentic Workflow - User Progress endpoints
    path('progress/save/', save_user_progress, name='save-user-progress'),
    path('progress/', get_user_progress, name='get-user-progress'),
    path('progress/stats/', get_user_learning_stats, name='get-user-learning-stats'),
    path('progress/videos/<str:video_id>/complete/', update_video_completion, name='update-video-completion'),

    # Guided Learning endpoints
    path('guided/start-session/<str:video_id>/', guided_start_session, name='guided-start-session'),
    path('guided/answer/<str:session_id>/', guided_submit_answer, name='guided-submit-answer'),
] 