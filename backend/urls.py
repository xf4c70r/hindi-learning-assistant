"""
URL configuration for backend project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.http import HttpResponse
from api import views
from rest_framework.routers import DefaultRouter

@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    return Response({
        'status': 'API is running',
        'endpoints': {
            'admin': '/admin/',
            'api': '/api/',
            'auth': {
                'signup': '/api/auth/signup/',
                'login': '/api/auth/login/'
            },
            'transcripts': '/api/transcripts/',
            'favorites': '/api/favorites/',
            'qa': '/api/qa/generate/',
            "vocabulary": {
            "query": "/api/vocabulary/query/",
                "words": "/api/vocabulary/words/",
                "trending": "/api/trending-words/"
        }
        }
    })

def healthz(request):
    return HttpResponse("OK", status=200)

router = DefaultRouter()
router.register(r'transcripts', views.TranscriptViewSet, basename='transcript')
router.register(r'questions', views.QuestionViewSet, basename='question')

urlpatterns = [
    path('', api_root, name='api-root'),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('healthz/', healthz, name='healthz'),
    path('api/vocabulary/words/', views.get_user_words, name='user-words'),
    path('api/vocabulary/query/', views.query_word, name='query-word'),
    path('api/words/<str:word_id>/toggle_favorite/', views.toggle_word_favorite, name='toggle-word-favorite'),
    path('api/words/<str:word_id>/update_notes/', views.update_word_notes, name='update-word-notes'),
    path('api/trending-words/', views.get_trending_words, name='trending-words'),
]
