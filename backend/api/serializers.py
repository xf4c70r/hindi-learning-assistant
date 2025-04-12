from rest_framework import serializers

class UserSerializer(serializers.Serializer):
    id = serializers.CharField()
    email = serializers.EmailField()
    first_name = serializers.CharField(allow_blank=True)
    last_name = serializers.CharField(allow_blank=True)
    date_joined = serializers.DateTimeField(read_only=True)
    last_login = serializers.DateTimeField(read_only=True)

class TranscriptSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    user_id = serializers.CharField(read_only=True)
    video_id = serializers.CharField()
    title = serializers.CharField(required=False)
    content = serializers.CharField()
    language = serializers.CharField()
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    is_favorite = serializers.BooleanField(default=False)
    questions = serializers.SerializerMethodField()

    def get_questions(self, obj):
        from api.services.mongo_service import mongo_service
        # Get questions from MongoDB
        questions = list(mongo_service.db.qa_pairs.find({'transcript_id': str(obj['id'])}))
        # Convert ObjectIds to strings
        for question in questions:
            question['_id'] = str(question['_id'])
        return questions

class QuestionSerializer(serializers.Serializer):
    id = serializers.CharField(read_only=True)
    transcript_id = serializers.CharField()
    video_id = serializers.CharField()
    video_title = serializers.CharField()
    question_text = serializers.CharField()
    answer = serializers.CharField()
    type = serializers.CharField()
    options = serializers.ListField(child=serializers.CharField(), required=False)
    created_at = serializers.DateTimeField(read_only=True)
    attempts = serializers.IntegerField(read_only=True)
    correct_attempts = serializers.IntegerField(read_only=True)
    is_favorite = serializers.BooleanField(default=False) 