from rest_framework import serializers
from .models import Transcript, Question

class UserSerializer(serializers.Serializer):
    id = serializers.CharField()
    email = serializers.EmailField()
    first_name = serializers.CharField(allow_blank=True)
    last_name = serializers.CharField(allow_blank=True)
    date_joined = serializers.DateTimeField(read_only=True)
    last_login = serializers.DateTimeField(read_only=True)

class TranscriptSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    questions = serializers.SerializerMethodField()

    class Meta:
        model = Transcript
        fields = ('id', 'user', 'video_id', 'title', 'content', 'language', 'created_at', 'updated_at', 'is_favorite', 'questions')
        read_only_fields = ('created_at', 'updated_at')

    def get_questions(self, obj):
        from api.services.mongo_service import mongo_service
        # Get questions from MongoDB
        questions = list(mongo_service.db.qa_pairs.find({'transcript_id': str(obj.id)}))
        # Convert ObjectIds to strings
        for question in questions:
            question['_id'] = str(question['_id'])
        return questions

class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'
        read_only_fields = ('created_at',) 