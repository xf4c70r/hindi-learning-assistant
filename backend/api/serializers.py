from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Transcript, Question

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')

class QuestionSerializer(serializers.Serializer):
    id = serializers.CharField(source='_id', required=False)
    question_type = serializers.CharField(source='type', required=False)
    question_text = serializers.CharField()
    answer = serializers.CharField()
    options = serializers.ListField(child=serializers.CharField(), required=False)
    created_at = serializers.DateTimeField(required=False)
    is_favorite = serializers.BooleanField(required=False)
    attempts = serializers.IntegerField(required=False)
    correct_attempts = serializers.IntegerField(required=False)

class TranscriptSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    questions = QuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Transcript
        fields = ('id', 'user', 'video_id', 'title', 'content', 'language', 'created_at', 'updated_at', 'is_favorite', 'questions')
        read_only_fields = ('created_at', 'updated_at') 