from django.shortcuts import render
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from api.services.mongo_service import mongo_service
from api.services.user_service import user_service
from bson import ObjectId
from datetime import datetime
from django.http import Http404

from .models import Transcript, Question
from .serializers import TranscriptSerializer, QuestionSerializer
from .youtube_utils import get_transcript, format_transcript, extract_video_id
from api.services.qa_service import qa_service

# Create your views here.

@api_view(['POST'])
@permission_classes([AllowAny])
def signup(request):
    email = request.data.get('email')
    password = request.data.get('password')
    first_name = request.data.get('first_name', '')
    last_name = request.data.get('last_name', '')

    # Validate required fields
    if not email or not password:
        return Response(
            {'error': 'Email and password are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    # Validate email format
    try:
        validate_email(email)
    except ValidationError:
        return Response(
            {'error': 'Invalid email format'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    # Check if email already exists
    if user_service.user_exists(email):
        return Response(
            {'error': 'Email already registered'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Create user in MongoDB
        user = user_service.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        
        # Create JWT tokens
        refresh = RefreshToken()
        refresh['user_id'] = user['id']
        refresh['email'] = user['email']
        
        return Response({
            'message': 'User created successfully',
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'email': user['email'],
                'first_name': user['first_name'],
                'last_name': user['last_name']
            }
        }, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    email = request.data.get('email')
    password = request.data.get('password')

    if not email or not password:
        return Response(
            {'error': 'Email and password are required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Get user by email
        user = user_service.get_user_by_email(email)
        if not user:
            return Response(
                {'error': 'Invalid credentials'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Verify password
        if user_service.verify_password(user, password):
            # Update last login
            user_service.update_last_login(user['id'])
            
            # Create JWT tokens
            refresh = RefreshToken()
            refresh['user_id'] = user['id']
            refresh['email'] = user['email']
            
            return Response({
                'message': 'Login successful',
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'user': {
                    'email': user['email'],
                    'first_name': user['first_name'],
                    'last_name': user['last_name']
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': 'Invalid credentials'}, 
                status=status.HTTP_401_UNAUTHORIZED
            )
    except Exception as e:
        return Response(
            {'error': str(e)}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        refresh_token = request.data.get('refresh')
        if not refresh_token:
            return Response({'error': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)
            
        token = RefreshToken(refresh_token)
        token.blacklist()
        
        return Response({'message': 'Successfully logged out'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class TranscriptViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Get transcripts from MongoDB instead of Django DB
        return mongo_service.get_transcripts(user_id=str(self.request.user_id))

    @action(detail=False, methods=['post'], url_path='create-from-video')
    def create_from_video(self, request):
        video_url = request.data.get('video_id')  # We're actually receiving the full URL here
        if not video_url:
            return Response({'error': 'Video URL is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Extract video ID from URL
            video_id = extract_video_id(video_url)
            if not video_id:
                return Response({'error': 'Invalid YouTube URL'}, status=status.HTTP_400_BAD_REQUEST)

            # Check if transcript already exists for this user and video in MongoDB
            existing_transcript = mongo_service.get_transcript_by_user_and_video(
                user_id=str(request.user_id),
                video_id=video_id
            )

            if existing_transcript:
                return Response(
                    {
                        'error': 'A transcript for this video already exists',
                        'transcript': existing_transcript
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Get transcript from YouTube
            transcript_data, language = get_transcript(video_id)
            formatted_transcript = format_transcript(transcript_data)
            
            # Save transcript to MongoDB only
            result = mongo_service.save_transcript(
                user_id=str(request.user_id),
                video_id=video_id,
                content=formatted_transcript,
                language=language
            )
            
            # Return the saved transcript data
            saved_transcript = {
                'id': str(result.inserted_id),
                'video_id': video_id,
                'title': request.data.get('title', 'Untitled'),
                'content': formatted_transcript,
                'language': language,
                'user_id': str(request.user_id)
            }
            
            return Response(saved_transcript, status=status.HTTP_201_CREATED)
            
        except ValueError as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            import traceback
            print(f"Error processing transcript: {str(e)}")
            print(traceback.format_exc())
            return Response(
                {
                    'error': 'An error occurred while processing the transcript',
                    'detail': str(e)
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def toggle_favorite(self, request, pk=None):
        try:
            # Toggle favorite in MongoDB
            result = mongo_service.toggle_transcript_favorite(
                transcript_id=pk,
                user_id=str(request.user_id)
            )
            if result:
                return Response(result)
            return Response(
                {'error': 'Transcript not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to toggle favorite status: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

class QuestionViewSet(viewsets.ModelViewSet):
    serializer_class = QuestionSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        transcript_id = self.kwargs.get('transcript_pk')
        # Fetch questions from MongoDB
        questions = list(mongo_service.db.qa_pairs.find({
            'transcript_id': transcript_id
        }))
        # Convert ObjectIds to strings
        for question in questions:
            question['_id'] = str(question['_id'])
        return questions

    def get_object(self):
        """
        Override get_object to handle both MongoDB and Django model questions
        """
        question_id = self.kwargs.get('pk')
        transcript_id = self.kwargs.get('transcript_pk')
        
        # Get from MongoDB
        mongo_question = mongo_service.db.qa_pairs.find_one({
            '_id': ObjectId(question_id),
            'transcript_id': transcript_id
        })
        
        if mongo_question:
            # Convert ObjectId to string
            mongo_question['_id'] = str(mongo_question['_id'])
            return mongo_question
            
        # If not found in MongoDB, try Django model
        try:
            return Question.objects.get(
                id=question_id,
                transcript_id=transcript_id,
                transcript__user_id=str(self.request.user_id)
            )
        except Question.DoesNotExist:
            raise Http404("Question not found")

    @action(detail=False, methods=['post'])
    def generate(self, request, transcript_pk=None):
        try:
            # Log request data
            print(f"Generating questions for transcript {transcript_pk}")
            print(f"Request data: {request.data}")
            
            # Validate transcript exists and belongs to user
            transcript = Transcript.objects.get(
                id=transcript_pk,
                user_id=str(self.request.user_id)
            )
            
            # Get and validate question type
            question_type = request.data.get('question_type', 'novice')
            if not qa_service.validate_question_type(question_type):
                return Response(
                    {'error': f'Invalid question type. Supported types: {qa_service.get_supported_question_types()}'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )

            print(f"Generating {question_type} questions for transcript content: {transcript.content[:100]}...")
            
            # Generate questions using QA service
            response = qa_service.generate_questions(
                text=transcript.content,
                question_type=question_type
            )
            
            # Handle both list and dict responses
            questions = response.get('qa_pairs', []) if isinstance(response, dict) else response
            print(f"Generated {len(questions)} questions")

            # Create Question objects
            created_questions = []
            for q in questions:
                try:
                    question = Question.objects.create(
                        transcript=transcript,
                        question_type=question_type,
                        question_text=q.get('question', ''),
                        answer=q.get('answer', ''),
                        options=q.get('options', [])
                    )
                    created_questions.append(question)
                except Exception as e:
                    print(f"Error creating question: {str(e)}")
                    print(f"Question data: {q}")
                    continue

            if not created_questions:
                return Response(
                    {'error': 'Failed to generate any valid questions'}, 
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            serializer = self.get_serializer(created_questions, many=True)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        except Transcript.DoesNotExist:
            return Response(
                {'error': 'Transcript not found or access denied'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            import traceback
            print(f"Error generating questions: {str(e)}")
            print(traceback.format_exc())
            return Response(
                {'error': f'Failed to generate questions: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def toggle_favorite(self, request, transcript_pk=None, pk=None):
        try:
            question = self.get_object()
            question.is_favorite = not question.is_favorite
            question.save()
            serializer = self.get_serializer(question)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': f'Failed to toggle favorite status: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'], url_path='answer')
    def submit_answer(self, request, transcript_pk=None, pk=None):
        try:
            question = self.get_object()
            submitted_answer = request.data.get('answer', '').strip()

            if not submitted_answer:
                return Response(
                    {'error': 'Answer cannot be empty'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Handle MongoDB question
            if isinstance(question, dict):
                correct_answer = question.get('answer', '').strip()
                is_correct = submitted_answer.lower() == correct_answer.lower()
                
                # Update MongoDB document with attempt information
                mongo_service.db.qa_pairs.update_one(
                    {'_id': ObjectId(question['_id'])},
                    {
                        '$inc': {
                            'attempts': 1,
                            'correct_attempts': 1 if is_correct else 0
                        }
                    }
                )
                
                # Get updated question data
                updated_question = mongo_service.db.qa_pairs.find_one({'_id': ObjectId(question['_id'])})
                
                return Response({
                    'is_correct': is_correct,
                    'correct_answer': correct_answer if not is_correct else None,
                    'feedback': 'Correct!' if is_correct else 'Incorrect. Try again!',
                    'attempts': updated_question.get('attempts', 1),
                    'correct_attempts': updated_question.get('correct_attempts', 1 if is_correct else 0)
                })

            # Handle Django model question
            else:
                correct_answer = question.answer.strip()
                is_correct = submitted_answer.lower() == correct_answer.lower()

                question.attempts = question.attempts + 1
                if is_correct:
                    question.correct_attempts = question.correct_attempts + 1
                question.save()

                return Response({
                    'is_correct': is_correct,
                    'correct_answer': correct_answer if not is_correct else None,
                    'feedback': 'Correct!' if is_correct else 'Incorrect. Try again!',
                    'attempts': question.attempts,
                    'correct_attempts': question.correct_attempts
                })

        except Exception as e:
            return Response(
                {'error': f'Failed to process answer: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_practice_sets(request):
    """Get available practice sets grouped by video and type"""
    try:
        # Aggregate practice sets from MongoDB
        practice_sets = list(mongo_service.db.qa_pairs.aggregate([
            {
                '$group': {
                    '_id': {
                        'video_id': '$video_id',
                        'type': '$type'
                    },
                    'questionCount': {'$sum': 1},
                    'title': {'$first': '$video_title'},
                    'created_at': {'$first': '$created_at'}
                }
            },
            {
                '$lookup': {
                    'from': 'user_progress',
                    'let': {
                        'video_id': '$_id.video_id',
                        'type': '$_id.type'
                    },
                    'pipeline': [
                        {
                            '$match': {
                                '$expr': {
                                    '$and': [
                                        {'$eq': ['$user_id', str(request.user_id)]},
                                        {'$eq': ['$video_id', '$$video_id']},
                                        {'$eq': ['$type', '$$type']}
                                    ]
                                }
                            }
                        }
                    ],
                    'as': 'progress'
                }
            },
            {
                '$project': {
                    'video_id': '$_id.video_id',
                    'type': '$_id.type',
                    'questionCount': 1,
                    'title': 1,
                    'created_at': 1,
                    'progress': {
                        '$cond': {
                            'if': {'$gt': [{'$size': '$progress'}, 0]},
                            'then': {'$arrayElemAt': ['$progress.progress', 0]},
                            'else': 0
                        }
                    }
                }
            },
            {'$sort': {'created_at': -1}}
        ]))
        
        return Response(practice_sets)
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_practice_questions(request, video_id, question_type):
    """Get questions for a specific practice set"""
    try:
        questions = list(mongo_service.db.qa_pairs.find({
            'video_id': video_id,
            'type': question_type
        }))
        
        # Get user's progress for these questions
        progress = mongo_service.db.user_progress.find_one({
            'user_id': str(request.user_id),
            'video_id': video_id,
            'type': question_type
        })
        
        # Get transcript content
        transcript = Transcript.objects.filter(video_id=video_id, user_id=str(request.user_id)).first()
        transcript_content = transcript.content if transcript else None
        
        # Convert ObjectId to string for JSON serialization
        for question in questions:
            question['_id'] = str(question['_id'])
            if 'transcript_id' in question:
                question['transcript_id'] = str(question['transcript_id'])
        
        return Response({
            'questions': questions,
            'progress': progress['answers'] if progress else {},
            'transcript': transcript_content
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_answer(request, question_id):
    """Submit an answer for a practice question"""
    try:
        answer = request.data.get('answer')
        is_correct = request.data.get('is_correct')
        video_id = request.data.get('video_id')
        question_type = request.data.get('type')
        
        if not all([answer, video_id, question_type]):
            return Response(
                {'error': 'Missing required fields'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Update or create user progress
        result = mongo_service.db.user_progress.update_one(
            {
                'user_id': str(request.user_id),
                'video_id': video_id,
                'type': question_type
            },
            {
                '$set': {
                    f'answers.{question_id}': {
                        'answer': answer,
                        'is_correct': is_correct,
                        'submitted_at': datetime.utcnow()
                    }
                },
                '$inc': {
                    'total_attempts': 1,
                    'correct_attempts': 1 if is_correct else 0
                },
                '$setOnInsert': {
                    'started_at': datetime.utcnow()
                }
            },
            upsert=True
        )
        
        # Calculate and update progress percentage
        progress_doc = mongo_service.db.user_progress.find_one({
            'user_id': str(request.user_id),
            'video_id': video_id,
            'type': question_type
        })
        
        total_questions = mongo_service.db.qa_pairs.count_documents({
            'video_id': video_id,
            'type': question_type
        })
        
        answered_questions = len(progress_doc.get('answers', {}))
        progress_percentage = (answered_questions / total_questions) * 100 if total_questions > 0 else 0
        
        mongo_service.db.user_progress.update_one(
            {'_id': progress_doc['_id']},
            {'$set': {'progress': progress_percentage}}
        )
        
        return Response({
            'success': True,
            'progress': progress_percentage
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_transcript_by_video(request, video_id):
    """Get transcript content for a specific video ID"""
    try:
        # Get transcript content
        transcript = Transcript.objects.filter(video_id=video_id, user_id=str(request.user_id)).first()
        
        if not transcript:
            return Response(
                {'error': 'Transcript not found for this video'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        return Response({
            'content': transcript.content,
            'title': transcript.title,
            'video_id': transcript.video_id
        })
        
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def generate_questions(request, transcript_id):
    try:
        transcript = Transcript.objects.get(id=transcript_id, user_id=str(request.user_id))
        # ... rest of the function remains the same ...
    except Transcript.DoesNotExist:
        return Response({'error': 'Transcript not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_favorite_transcript(request, transcript_id):
    try:
        transcript = Transcript.objects.get(id=transcript_id, user_id=str(request.user_id))
        transcript.is_favorite = not transcript.is_favorite
        transcript.save()
        return Response({'is_favorite': transcript.is_favorite})
    except Transcript.DoesNotExist:
        return Response({'error': 'Transcript not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_favorite_question(request, question_id):
    try:
        question = Question.objects.get(id=question_id, transcript__user_id=str(request.user_id))
        question.is_favorite = not question.is_favorite
        question.save()
        return Response({'is_favorite': question.is_favorite})
    except Question.DoesNotExist:
        return Response({'error': 'Question not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_question_stats(request, question_id):
    try:
        question = Question.objects.get(id=question_id, transcript__user_id=str(request.user_id))
        is_correct = request.data.get('is_correct', False)
        
        question.attempts += 1
        if is_correct:
            question.correct_attempts += 1
        question.save()
        
        return Response({
            'attempts': question.attempts,
            'correct_attempts': question.correct_attempts
        })
    except Question.DoesNotExist:
        return Response({'error': 'Question not found'}, status=status.HTTP_404_NOT_FOUND)
