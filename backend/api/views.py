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
import logging
from django.core.cache import cache
from django.conf import settings
import json

from .serializers import TranscriptSerializer, QuestionSerializer
from .youtube_utils import get_transcript, format_transcript, extract_video_id, check_video_captions
from api.services.qa_service import qa_service
from qa_engine.qa_model import qa_model

from qa_engine.deepseek_utils import deepseek_query
from datetime import datetime

# Create your views here.

logger = logging.getLogger(__name__)

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
    serializer_class = TranscriptSerializer

    def get_queryset(self):
        user_id = getattr(self.request, 'user_id', None)
        if not user_id:
            return []
            
        # Check if we should filter favorites only
        favorites_only = self.request.query_params.get('favorite', '').lower() == 'true'
        
        # Get transcripts from MongoDB and convert ObjectIds to strings
        query = {'user_id': str(user_id)}
        if favorites_only:
            query['is_favorite'] = True
            
        transcripts = list(mongo_service.db.transcripts.find(query))
        for transcript in transcripts:
            transcript['id'] = str(transcript['_id'])
        return transcripts

    def get_object(self):
        pk = self.kwargs.get('pk')
        user_id = getattr(self.request, 'user_id', None)
        
        # Try to find transcript by video_id first
        transcript = mongo_service.db.transcripts.find_one({
            'video_id': pk,
            'user_id': str(user_id)
        })
        
        # If not found, try as ObjectId (for backwards compatibility)
        if not transcript:
            try:
                transcript = mongo_service.db.transcripts.find_one({
                    '_id': ObjectId(pk),
                    'user_id': str(user_id)
                })
            except:
                pass
                
        if not transcript:
            raise Http404("Transcript not found")
            
        transcript['id'] = str(transcript['_id'])
        return transcript

    def destroy(self, request, *args, **kwargs):
        """Delete a transcript and its associated questions"""
        try:
            user_id = getattr(request, 'user_id', None)
            if not user_id:
                return Response(
                    {'error': 'Authentication failed - no user ID found'},
                    status=status.HTTP_401_UNAUTHORIZED
                )

            transcript_id = kwargs.get('pk')
            success = mongo_service.delete_transcript(transcript_id, str(user_id))
            
            if not success:
                return Response(
                    {'error': 'Transcript not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
                
            return Response(status=status.HTTP_204_NO_CONTENT)
            
        except Exception as e:
            return Response(
                {'error': f'Failed to delete transcript: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=False, methods=['post'], url_path='create-from-video')
    def create_from_video(self, request):
        logger.info("Starting transcript creation process")
        
        # Check if user is authenticated and has user_id
        user_id = getattr(request, 'user_id', None)
        if not user_id:
            logger.error("No user_id found in request")
            return Response(
                {'error': 'Authentication failed - no user ID found'},
                status=status.HTTP_401_UNAUTHORIZED
            )
            
        video_url = request.data.get('video_id')  
        logger.info(f"Received video URL: {video_url}")
        
        if not video_url:
            logger.error("No video URL provided")
            return Response({'error': 'Video URL is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Extract video ID from URL
            logger.info("Attempting to extract video ID")
            video_id = extract_video_id(video_url)
            logger.info(f"Extracted video ID: {video_id}")
            
            if not video_id:
                logger.error("Failed to extract valid video ID from URL")
                return Response({'error': 'Invalid YouTube URL'}, status=status.HTTP_400_BAD_REQUEST)

            # Check if transcript already exists
            logger.info(f"Checking for existing transcript for user {user_id} and video {video_id}")
            existing_transcript = mongo_service.get_transcript_by_user_and_video(
                user_id=str(user_id),
                video_id=video_id
            )

            if existing_transcript:
                logger.info("Found existing transcript")
                return Response(
                    {
                        'error': 'A transcript for this video already exists',
                        'transcript': existing_transcript
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Check if video has captions before attempting to fetch
            logger.info("Checking if video has captions available")
            available_languages = check_video_captions(video_id)
            
            if not available_languages:
                logger.error("No captions available for this video")
                return Response(
                    {
                        'error': 'This video does not have any captions/transcripts available. Please try a different video with captions enabled.',
                        'video_id': video_id
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Try to get transcript from cache first
            cache_key = f'transcript_{video_id}'
            cached_data = cache.get(cache_key)
            
            if cached_data:
                logger.info("Found transcript in cache")
                transcript_data, language = cached_data
            else:
                # Get transcript from YouTube
                logger.info("Attempting to fetch transcript from YouTube")
                transcript_data, language = get_transcript(video_id)
                logger.info(f"Successfully fetched transcript in {language}")
                
                # Cache the transcript
                cache.set(cache_key, (transcript_data, language), settings.TRANSCRIPT_CACHE_TIMEOUT)
            
            formatted_transcript = format_transcript(transcript_data)
            logger.info(f"Formatted transcript length: {len(formatted_transcript)}")
            
            # Process transcript with DeepSeek
            logger.info("Processing transcript with DeepSeek")
            try:
                processed_data = qa_model.process_transcript(formatted_transcript)
                logger.info("Successfully processed transcript with DeepSeek")
                logger.debug(f"Processed data structure: {list(processed_data.keys())}")
            except Exception as e:
                logger.error(f"Failed to process transcript with DeepSeek: {str(e)}")
                logger.error(f"Formatted transcript preview: {formatted_transcript[:200]}...")
                raise ValueError("Failed to process transcript with DeepSeek")
            
            # Save processed transcript to MongoDB
            logger.info("Attempting to save processed transcript to MongoDB")
            try:
                result = mongo_service.save_transcript(
                    user_id=str(user_id),
                    video_id=video_id,
                    content=processed_data['punctuated_text'],
                    language=language
                )
                logger.info("Successfully saved processed transcript to MongoDB")
            except KeyError as ke:
                logger.error(f"Missing key in processed data: {str(ke)}")
                logger.error(f"Processed data keys: {list(processed_data.keys())}")
                raise ValueError(f"Invalid response format from DeepSeek: missing {str(ke)}")
            except Exception as e:
                logger.error(f"Failed to save transcript to MongoDB: {str(e)}")
                raise
            
            # Return the saved transcript data
            saved_transcript = {
                'id': str(result.inserted_id),
                'video_id': video_id,
                'title': request.data.get('title', 'Untitled'),
                'content': processed_data['punctuated_text'],
                'language': language,
                'user_id': str(user_id)
            }
            
            logger.info("Successfully completed transcript creation and processing")
            return Response(saved_transcript, status=status.HTTP_201_CREATED)
            
        except ValueError as e:
            logger.error(f"ValueError in transcript creation: {str(e)}")
            error_msg = str(e)
            
            # Provide more helpful error messages
            if "no element found" in error_msg.lower():
                return Response({
                    'error': 'Unable to fetch captions from this video. This might be due to:',
                    'details': [
                        'YouTube API temporary issues',
                        'Auto-generated captions parsing problems',
                        'Video-specific caption format issues'
                    ],
                    'suggestions': [
                        'Try a different video with manually created captions',
                        'Wait a few minutes and try again',
                        'Check if the video has proper captions enabled'
                    ],
                    'video_id': video_id
                }, status=status.HTTP_400_BAD_REQUEST)
            elif "No transcripts available" in error_msg:
                return Response({
                    'error': 'This video does not have any captions/transcripts available.',
                    'suggestions': [
                        'Try a video with captions enabled (look for the CC button)',
                        'Use a video with manually created captions rather than auto-generated ones'
                    ],
                    'video_id': video_id
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            logger.error(f"Unexpected error in transcript creation: {str(e)}")
            import traceback
            logger.error(f"Full traceback: {traceback.format_exc()}")
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
                return Response({
                    'id': str(result['_id']),
                    'is_favorite': result['is_favorite']
                })
            return Response(
                {'error': 'Transcript not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            return Response(
                {'error': f'Failed to toggle favorite status: {str(e)}'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(detail=True, methods=['post'], url_path='process')
    def process_transcript(self, request, pk=None):
        """Process transcript with DeepSeek for punctuation"""
        try:
            transcript = self.get_object()
            if not transcript:
                return Response(
                    {'error': 'Transcript not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Check if already processed
            if transcript.get('processed_content'):
                return Response(
                    {'error': 'Transcript already processed'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Prepare prompt for DeepSeek
            prompt = f"""Please process the following Hindi text by adding proper punctuation (।, ?, !, etc.).

            Return ONLY a JSON object with the following structure:
            {{
                "punctuated_text": "punctuated Hindi text"
            }}

            Hindi Text:
            {transcript['content']}"""

            # Call DeepSeek API
            response = deepseek_query(prompt)
            
            try:
                # Parse the response
                processed_data = json.loads(response)
                
                # Update transcript in MongoDB
                mongo_service.db.transcripts.update_one(
                    {'_id': ObjectId(pk)},
                    {
                        '$set': {
                            'processed_content': processed_data,
                            'updated_at': datetime.utcnow()
                        }
                    }
                )
                
                return Response(processed_data, status=status.HTTP_200_OK)
                
            except json.JSONDecodeError:
                return Response(
                    {'error': 'Failed to parse DeepSeek response'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
                
        except Exception as e:
            logger.error(f"Error processing transcript: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'], url_path='translate')
    def translate(self, request, pk=None):
        """Translate a transcript"""
        try:
            transcript = self.get_object()
            if not transcript:
                return Response(
                    {'error': 'Transcript not found'},
                    status=status.HTTP_404_NOT_FOUND
                )

            # Get the content to translate
            content = transcript.get('content', '')
            if not content:
                return Response(
                    {'error': 'No content to translate'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Translate the content
            try:
                translation_data = qa_model.translate_text(content)
                translation = translation_data['translation']
            except Exception as e:
                logger.error(f"Error in translation: {str(e)}")
                return Response(
                    {'error': f'Failed to translate text: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # Update the transcript with translation
            try:
                mongo_service.db.transcripts.update_one(
                    {'_id': ObjectId(pk)},
                    {
                        '$set': {
                            'translation': translation,
                            'updated_at': datetime.utcnow()
                        }
                    }
                )
            except Exception as e:
                logger.error(f"Error updating transcript with translation: {str(e)}")
                return Response(
                    {'error': f'Failed to save translation: {str(e)}'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            return Response({
                'translation': translation
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error in translate endpoint: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def create(self, request, *args, **kwargs):
        """Create a new transcript and process it"""
        try:
            # Get the text from the request
            text = request.data.get('text', '').strip()
            if not text:
                return Response(
                    {"error": "Text is required"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # First pass: Process the transcript for punctuation
            try:
                processed_data = qa_model.process_transcript(text)
                punctuated_text = processed_data['punctuated_text']
            except Exception as e:
                logger.error(f"Error in first pass (punctuation): {str(e)}")
                return Response(
                    {"error": f"Failed to process transcript: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # Second pass: Translate the punctuated text
            try:
                translation_data = qa_model.translate_text(punctuated_text)
                translation = translation_data['translation']
            except Exception as e:
                logger.error(f"Error in second pass (translation): {str(e)}")
                return Response(
                    {"error": f"Failed to translate text: {str(e)}"},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

            # Create the transcript with both punctuated text and translation
            transcript = Transcript.objects.create(
                text=text,
                punctuated_text=punctuated_text,
                translation=translation
            )

            # Return the processed data
            return Response({
                "id": str(transcript.id),
                "text": text,
                "punctuated_text": punctuated_text,
                "translation": translation
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            logger.error(f"Error in transcript creation: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @action(detail=True, methods=['post'])
    def glossary(self, request, pk=None):
        """Generate glossary entries for a transcript"""
        try:
            transcript = self.get_object()
            if not transcript['content']:
                return Response(
                    {"error": "Transcript content is empty"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Generate glossary using QA model
            glossary_data = qa_model.generate_glossary(transcript['content'])
            
            # Update the transcript document in MongoDB
            transcript_doc = mongo_service.db.transcripts.find_one({"_id": ObjectId(transcript['id'])})
            if transcript_doc:
                mongo_service.db.transcripts.update_one(
                    {"_id": ObjectId(transcript['id'])},
                    {"$set": {"glossary": glossary_data["glossary"]}}
                )
            
            return Response(glossary_data)
            
        except Exception as e:
            logger.error(f"Error in glossary generation: {str(e)}")
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
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
        for question in questions:
            question['_id'] = str(question['_id'])
        return questions

    def get_object(self):
        question_id = self.kwargs.get('pk')
        transcript_id = self.kwargs.get('transcript_pk')
        
        # Get question from MongoDB
        question = mongo_service.db.qa_pairs.find_one({
            '_id': ObjectId(question_id),
            'transcript_id': transcript_id
        })
        
        if not question:
            raise Http404("Question not found")
            
        question['_id'] = str(question['_id'])
        return question

    @action(detail=False, methods=['post'])
    def generate(self, request, transcript_pk=None):
        try:
            print(f"Generating questions for transcript {transcript_pk}")
            
            # Validate transcript exists and belongs to user
            transcript = mongo_service.db.transcripts.find_one({'_id': ObjectId(transcript_pk)})
            if not transcript:
                return Response(
                    {'error': 'Transcript not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Get question types from request or generate all types
            question_types = request.data.get('types', qa_service.get_supported_question_types())
            if not isinstance(question_types, list):
                question_types = [question_types]
            
            created_questions = []
            
            # Generate questions for each type
            for question_type in question_types:
                if not qa_service.validate_question_type(question_type):
                    continue  # Skip invalid types
                
                print(f"Generating {question_type} questions...")
                
                # Generate questions using QA service
                response = qa_service.generate_questions(
                    text=transcript['content'],
                    question_type=question_type
                )
                
                questions = response.get('qa_pairs', []) if isinstance(response, dict) else response
                print(f"Generated {len(questions)} {question_type} questions")
                
                # Create questions in MongoDB
                for q in questions:
                    question_data = {
                        'transcript_id': transcript_pk,
                        'video_id': transcript['video_id'],
                        'video_title': transcript.get('title', ''),
                        'question_text': q['question'],
                        'answer': q['answer'],
                        'type': question_type,
                        'options': q.get('options', []),
                        'created_at': datetime.utcnow(),
                        'attempts': 0,
                        'correct_attempts': 0
                    }
                    result = mongo_service.db.qa_pairs.insert_one(question_data)
                    question_data['_id'] = str(result.inserted_id)
                    created_questions.append(question_data)
            
            return Response(created_questions, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            print(f"Error generating questions: {str(e)}")
            return Response(
                {'error': str(e)},
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
    try:
        # Get all transcripts for the user from MongoDB
        transcripts = list(mongo_service.db.transcripts.find({
            'user_id': str(request.user_id)
        }))
        
        practice_sets = []
        for transcript in transcripts:
            transcript_id = str(transcript['_id'])
            # Get questions for this transcript
            questions = list(mongo_service.db.qa_pairs.find({
                'transcript_id': transcript_id
            }))
            
            if questions:
                # Group questions by type
                question_types = {}
                for q in questions:
                    q_type = q.get('type', 'novice')  # Default to novice if type not specified
                    if q_type not in question_types:
                        question_types[q_type] = []
                    question_types[q_type].append(q)
                
                # Create a practice set entry for each type
                for q_type, type_questions in question_types.items():
                    practice_sets.append({
                        'id': transcript_id,
                        'title': transcript.get('title', 'Untitled'),
                        'video_id': transcript['video_id'],
                        'type': q_type,
                        'question_count': len(type_questions)
                    })
        
        return Response(practice_sets)
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_practice_questions(request, video_id, question_type):
    try:
        # Get transcript from MongoDB
        transcript = mongo_service.db.transcripts.find_one({
            'video_id': video_id,
            'user_id': str(request.user_id)
        })
        
        if not transcript:
            return Response(
                {'error': 'Transcript not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get questions from MongoDB
        questions = list(mongo_service.db.qa_pairs.find({
            'video_id': video_id,
            'type': question_type
        }))
        
        # Format questions for frontend
        formatted_questions = []
        for question in questions:
            formatted_question = {
                '_id': str(question['_id']),
                'question_text': question.get('question_text', ''),
                'answer': question.get('answer', ''),
                'type': question.get('type', question_type),
                'options': question.get('options', []),
                'video_id': video_id,
                'video_title': question.get('video_title', transcript.get('title', 'Untitled')),
                'attempts': question.get('attempts', 0),
                'correct_attempts': question.get('correct_attempts', 0)
            }
            formatted_questions.append(formatted_question)
        
        response_data = {
            'questions': formatted_questions,
            'transcript': transcript.get('content', ''),
            'title': transcript.get('title', 'Untitled')
        }
        
        return Response(response_data)
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def submit_answer(request, question_id):
    try:
        # Get question from MongoDB
        question = mongo_service.db.qa_pairs.find_one({
            '_id': ObjectId(question_id)
        })
        
        if not question:
            return Response(
                {'error': 'Question not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        user_answer = request.data.get('answer', '').strip()
        correct_answer = question['answer'].strip()
        is_correct = user_answer.lower() == correct_answer.lower()
        
        # Update question stats in MongoDB
        mongo_service.db.qa_pairs.update_one(
            {'_id': ObjectId(question_id)},
            {
                '$inc': {
                    'attempts': 1,
                    'correct_attempts': 1 if is_correct else 0
                }
            }
        )
        
        updated_question = mongo_service.db.qa_pairs.find_one({
            '_id': ObjectId(question_id)
        })
        
        return Response({
            'is_correct': is_correct,
            'correct_answer': correct_answer,
            'attempts': updated_question['attempts'],
            'correct_attempts': updated_question['correct_attempts']
        })
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_transcript_by_video(request, video_id):
    try:
        # Get transcript from MongoDB
        transcript = mongo_service.db.transcripts.find_one({
            'video_id': video_id,
            'user_id': str(request.user_id)
        })
        
        if not transcript:
            return Response(
                {'error': 'Transcript not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        transcript['_id'] = str(transcript['_id'])
        return Response(transcript)
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_favorite_transcript(request, transcript_id):
    try:
        # Toggle favorite in MongoDB
        result = mongo_service.toggle_transcript_favorite(
            transcript_id=transcript_id,
            user_id=str(request.user_id)
        )
        
        if not result:
            return Response(
                {'error': 'Transcript not found'},
                status=status.HTTP_404_NOT_FOUND
            )
            
        return Response({'is_favorite': result['is_favorite']})
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_favorite_question(request, question_id):
    try:
        # Toggle favorite in MongoDB
        result = mongo_service.toggle_question_favorite(
            question_id=question_id,
            user_id=str(request.user_id)
        )
        
        if not result:
            return Response(
                {'error': 'Question not found'},
                status=status.HTTP_404_NOT_FOUND
            )
            
        return Response({'is_favorite': result['is_favorite']})
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_question_stats(request, question_id):
    try:
        # Update question stats in MongoDB
        result = mongo_service.update_question_stats(
            question_id=question_id,
            user_id=str(request.user_id),
            is_correct=request.data.get('is_correct', False)
        )
        
        if not result:
            return Response(
                {'error': 'Question not found'},
                status=status.HTTP_404_NOT_FOUND
            )
            
        return Response({
            'attempts': result['attempts'],
            'correct_attempts': result['correct_attempts']
        })
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def query_word(request):
    try:
        word = request.data.get('word')
        if not word:
            return Response(
                {'error': 'Word is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Normalize word by stripping whitespace
        word = word.strip()
        if not word:
            return Response(
                {'error': 'Word cannot be empty'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        db = mongo_service.db
        
        # Check global dictionary first with normalized word
        global_word = db.global_words.find_one({'word': word})
        
        if global_word:
            # Word exists, increment frequency
            try:
                db.global_words.update_one(
                    {'_id': global_word['_id']},
                    {'$inc': {'frequency': 1}}
                )
                meaning_data = global_word['meaning_data']
            except Exception as e:
                logger.error(f"Error updating word frequency: {str(e)}")
                # Continue with existing meaning data even if update fails
                meaning_data = global_word['meaning_data']
        else:
            try:
                # Check for similar words (case-insensitive and ignoring spaces)
                similar_word = db.global_words.find_one({
                    'word': {'$regex': f'^{word}\\s*$', '$options': 'i'}
                })
                
                if similar_word:
                    # Use existing word instead of creating a new one
                    global_word = similar_word
                    db.global_words.update_one(
                        {'_id': global_word['_id']},
                        {'$inc': {'frequency': 1}}
                    )
                    meaning_data = global_word['meaning_data']
                else:
                    # Use qa_service to get word meaning for new word
                    meaning_data = qa_service.query_word_meaning(word)
                    
                    # Save to global dictionary
                    global_word = db.global_words.insert_one({
                        'word': word,  # Save normalized word
                        'meaning_data': meaning_data,
                        'frequency': 1,
                        'created_at': datetime.now(),
                        'last_updated': datetime.now()
                    })
                    global_word = db.global_words.find_one({'_id': global_word.inserted_id})
            except ValueError as e:
                logger.error(f"Error querying word meaning: {str(e)}")
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            except Exception as e:
                logger.error(f"Unexpected error in word query: {str(e)}")
                return Response(
                    {'error': 'An unexpected error occurred while querying the word meaning'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )

        try:
            # Add to user's list
            db.user_words.update_one(
                {
                    'user_id': str(request.user_id),
                    'word_id': global_word['_id']
                },
                {
                    '$setOnInsert': {
                        'is_mastered': False,
                        'is_favorite': False,
                        'notes': '',
                        'created_at': datetime.now()
                    }
                },
                upsert=True
            )
        except Exception as e:
            logger.error(f"Error updating user words: {str(e)}")
            # Continue even if user words update fails
            pass

        return Response({
            'word': word,
            'data': meaning_data,
            'frequency': global_word.get('frequency', 1)
        })

    except Exception as e:
        logger.error(f"Error in query_word: {str(e)}")
        return Response(
            {'error': 'An unexpected error occurred while processing your request'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_word_favorite(request, word_id):
    try:
        db = mongo_service.db
        
        # Find the user's word entry
        user_word = db.user_words.find_one({
            'user_id': str(request.user_id),
            'word_id': ObjectId(word_id)
        })
        
        if not user_word:
            return Response(
                {'error': 'Word not found in user\'s list'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Toggle the is_favorite status
        new_status = not user_word.get('is_favorite', False)
        db.user_words.update_one(
            {
                'user_id': str(request.user_id),
                'word_id': ObjectId(word_id)
            },
            {
                '$set': {
                    'is_favorite': new_status,
                    'updated_at': datetime.now()
                }
            }
        )
        
        return Response({
            'word_id': str(word_id),
            'is_favorite': new_status
        })
        
    except Exception as e:
        logger.error(f"Error in toggle_word_favorite: {str(e)}")
        return Response(
            {'error': 'Failed to toggle favorite status'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_words(request):
    try:
        db = mongo_service.db
        
        # Get filter parameters
        favorites_only = request.query_params.get('favorites', '').lower() == 'true'
        
        # Base match condition
        match_condition = {
                    'user_id': str(request.user_id)
                }
        
        # Add favorites filter if requested
        if favorites_only:
            match_condition['is_favorite'] = True
        
        current_time = datetime.now()
        user_words = list(db.user_words.aggregate([
            {
                '$match': match_condition
            },
            {
                '$lookup': {
                    'from': 'global_words',
                    'localField': 'word_id',
                    'foreignField': '_id',
                    'as': 'word_details'
                }
            },
            {
                '$unwind': '$word_details'
            },
            {
                '$project': {
                    '_id': { '$toString': '$_id' },
                    'word_id': { '$toString': '$word_id' },
                    'word': '$word_details.word',
                    'meaning': {
                        'meaning': '$word_details.meaning_data.meaning',
                        'example': {
                            'hindi': '$word_details.meaning_data.example.hindi',
                            'english': '$word_details.meaning_data.example.english'
                        }
                    },
                    'frequency': { '$ifNull': ['$word_details.frequency', 1] },
                    'is_mastered': { '$ifNull': ['$is_mastered', False] },
                    'is_favorite': { '$ifNull': ['$is_favorite', False] },
                    'notes': { '$ifNull': ['$notes', ''] },
                    'created_at': { '$ifNull': ['$created_at', current_time] }
                }
            },
            {
                '$sort': {
                    'created_at': -1
                }
            }
        ]))

        return Response({
            'words': user_words,
            'count': len(user_words)
        })
    except Exception as e:
        logger.error(f"Error in get_user_words: {str(e)}")
        return Response(
            {'error': 'Failed to fetch user words. Please try again.'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_word_notes(request, word_id):
    try:
        db = mongo_service.db
        notes = request.data.get('notes', '').strip()
        
        # Find the user's word entry
        user_word = db.user_words.find_one({
            'user_id': str(request.user_id),
            'word_id': ObjectId(word_id)
        })
        
        if not user_word:
            return Response(
                {'error': 'Word not found in user\'s list'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Update the notes
        db.user_words.update_one(
            {
                'user_id': str(request.user_id),
                'word_id': ObjectId(word_id)
            },
            {
                '$set': {
                    'notes': notes,
                    'updated_at': datetime.now()
                }
            }
        )
        
        return Response({
            'word_id': str(word_id),
            'notes': notes
        })
        
    except Exception as e:
        logger.error(f"Error in update_word_notes: {str(e)}")
        return Response(
            {'error': 'Failed to update notes'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_trending_words(request):
    try:
        db = mongo_service.db
        # Get top 3 words by frequency
        trending_words = list(db.global_words.find(
            {},
            {'word': 1, 'meaning_data': 1, 'frequency': 1}
        ).sort('frequency', -1).limit(3))

        # Format the response
        formatted_words = [{
            'word': word['word'],
            'meaning': word['meaning_data']['meaning'],
            'frequency': word.get('frequency', 1)
        } for word in trending_words]

        return Response(formatted_words)
    except Exception as e:
        logger.error(f"Error fetching trending words: {str(e)}")
        return Response(
            {'error': 'Failed to fetch trending words'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

# ============================================================================
# AGENTIC WORKFLOW API ENDPOINTS
# ============================================================================

@api_view(['GET'])
@permission_classes([AllowAny])
def get_curated_videos(request):
    """
    Get curated videos with optional filtering by topic and difficulty
    """
    try:
        # Validate query parameters
        topic = request.GET.get('topic', '').strip()
        difficulty = request.GET.get('difficulty', '').strip()
        limit = request.GET.get('limit', 20)
        
        # Validate and convert limit to int
        try:
            limit = int(limit) if limit else None
            if limit is not None and (limit <= 0 or limit > 100):
                return Response(
                    {'error': 'Limit must be between 1 and 100'}, 
                    status=status.HTTP_400_BAD_REQUEST
                )
        except ValueError:
            return Response(
                {'error': 'Invalid limit parameter. Must be a number.'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Validate topic and difficulty if provided
        valid_topics = ['daily_life', 'business', 'travel', 'food', 'family', 'education', 'entertainment']
        valid_difficulties = ['beginner', 'intermediate', 'advanced']
        
        if topic and topic not in valid_topics:
            return Response(
                {'error': f'Invalid topic. Must be one of: {", ".join(valid_topics)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if difficulty and difficulty not in valid_difficulties:
            return Response(
                {'error': f'Invalid difficulty. Must be one of: {", ".join(valid_difficulties)}'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get videos from MongoDB
        try:
            videos = mongo_service.get_curated_videos(
                topic=topic if topic else None,
                difficulty=difficulty if difficulty else None,
                limit=limit
            )
        except Exception as db_error:
            logger.error(f"Database error in get_curated_videos: {str(db_error)}")
            return Response(
                {'error': 'Database connection error. Please try again later.'}, 
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        # Format response with error handling for each video
        formatted_videos = []
        for video in videos:
            try:
                # Generate description from cultural context if available
                cultural_context = video.get('metadata', {}).get('cultural_context', {})
                description = video.get('description') or f"Learn Hindi conversation in {cultural_context.get('setting', 'various')} settings. {cultural_context.get('cultural_notes', 'Perfect for improving your Hindi speaking skills.')}"
                
                # Generate YouTube thumbnail URL
                video_id = video.get('video_id')
                if not video_id:
                    logger.warning(f"Video missing video_id: {video.get('title', 'Unknown')}")
                    continue
                    
                thumbnail_url = f"https://img.youtube.com/vi/{video_id}/mqdefault.jpg"
                
                # Calculate vocabulary count
                vocabulary_count = len(video.get('metadata', {}).get('key_vocabulary', []))
                
                # Parse duration to seconds for filtering
                duration_seconds = 0
                duration_str = video.get('duration')
                if duration_str:
                    try:
                        if ':' in duration_str:
                            parts = duration_str.split(':')
                            if len(parts) == 2:
                                duration_seconds = int(parts[0]) * 60 + int(parts[1])
                            elif len(parts) == 3:
                                duration_seconds = int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
                        else:
                            duration_seconds = int(duration_str)
                    except (ValueError, TypeError):
                        logger.warning(f"Invalid duration format for video {video_id}: {duration_str}")
                        duration_seconds = 0
                
                formatted_video = {
                    'video_id': video_id,
                    'title': video.get('title', 'Untitled Video'),
                    'description': description,
                    'duration': duration_str or '0:00',
                    'duration_seconds': duration_seconds,
                    'topic': video.get('topic', 'general'),
                    'difficulty': video.get('difficulty', 'beginner'),
                    'thumbnail_url': thumbnail_url,
                    'vocabulary_count': vocabulary_count,
                    'rating': video.get('rating', 4.5),
                    'metadata': {
                        'key_vocabulary': video.get('metadata', {}).get('key_vocabulary', []),
                        'grammar_patterns': video.get('metadata', {}).get('grammar_patterns', []),
                        'cultural_context': video.get('metadata', {}).get('cultural_context', {}),
                        'learning_path': video.get('metadata', {}).get('learning_path', {}),
                        'technical_specs': video.get('metadata', {}).get('technical_specs', {})
                    }
                }
                formatted_videos.append(formatted_video)
                
            except Exception as video_error:
                logger.error(f"Error formatting video {video.get('video_id', 'unknown')}: {str(video_error)}")
                continue  # Skip this video and continue with others
        
        return Response({
            'videos': formatted_videos,
            'count': len(formatted_videos),
            'filters': {
                'topic': topic if topic else None,
                'difficulty': difficulty if difficulty else None,
                'limit': limit
            },
            'message': f'Successfully retrieved {len(formatted_videos)} videos'
        })
        
    except Exception as e:
        logger.error(f"Unexpected error in get_curated_videos: {str(e)}")
        return Response(
            {'error': 'An unexpected error occurred. Please try again later.'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_curated_video_detail(request, video_id):
    """
    Get detailed information about a specific curated video
    """
    try:
        # Get video from MongoDB
        video = mongo_service.get_curated_video_by_id(video_id)
        
        if not video:
            return Response(
                {'error': 'Video not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Generate description from cultural context if available
        cultural_context = video.get('metadata', {}).get('cultural_context', {})
        description = video.get('description') or f"Learn Hindi conversation in {cultural_context.get('setting', 'various')} settings. {cultural_context.get('cultural_notes', 'Perfect for improving your Hindi speaking skills.')}"
        
        # Generate YouTube thumbnail URL
        thumbnail_url = f"https://img.youtube.com/vi/{video.get('video_id')}/mqdefault.jpg"
        
        # Calculate vocabulary count
        vocabulary_count = len(video.get('metadata', {}).get('key_vocabulary', []))
        
        # Parse duration to seconds for filtering
        duration_seconds = 0
        if video.get('duration'):
            try:
                if ':' in video.get('duration'):
                    parts = video.get('duration').split(':')
                    if len(parts) == 2:
                        duration_seconds = int(parts[0]) * 60 + int(parts[1])
                    elif len(parts) == 3:
                        duration_seconds = int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
                else:
                    duration_seconds = int(video.get('duration'))
            except (ValueError, TypeError):
                duration_seconds = 0
        
        # Format response
        formatted_video = {
            'video_id': video.get('video_id'),
            'title': video.get('title'),
            'description': description,  # NEW: Add description
            'duration': video.get('duration'),
            'duration_seconds': duration_seconds,  # NEW: Add duration in seconds
            'topic': video.get('topic'),
            'difficulty': video.get('difficulty'),
            'thumbnail_url': thumbnail_url,  # NEW: Add YouTube thumbnail
            'vocabulary_count': vocabulary_count,  # NEW: Add vocabulary count
            'rating': video.get('rating', 4.5),  # NEW: Add rating (default 4.5)
            'metadata': {
                'key_vocabulary': video.get('metadata', {}).get('key_vocabulary', []),
                'grammar_patterns': video.get('metadata', {}).get('grammar_patterns', []),
                'cultural_context': video.get('metadata', {}).get('cultural_context', {}),
                'learning_path': video.get('metadata', {}).get('learning_path', {}),
                'technical_specs': video.get('metadata', {}).get('technical_specs', {})
            }
        }
        
        return Response(formatted_video)
        
    except Exception as e:
        logger.error(f"Error in get_curated_video_detail: {str(e)}")
        return Response(
            {'error': 'Failed to fetch video details'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_curated_video_topics(request):
    """
    Get available topics and their video counts
    """
    try:
        # Get all videos to analyze topics
        all_videos = mongo_service.get_curated_videos()
        
        # Count videos by topic
        topic_counts = {}
        for video in all_videos:
            topic = video.get('topic', 'unknown')
            topic_counts[topic] = topic_counts.get(topic, 0) + 1
        
        # Format response
        topics = [
            {
                'topic': topic,
                'count': count,
                'name': topic.replace('_', ' ').title()
            }
            for topic, count in topic_counts.items()
        ]
        
        # Sort by count (descending)
        topics.sort(key=lambda x: x['count'], reverse=True)
        
        return Response({
            'topics': topics,
            'total_videos': len(all_videos)
        })
        
    except Exception as e:
        logger.error(f"Error in get_curated_video_topics: {str(e)}")
        return Response(
            {'error': 'Failed to fetch video topics'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_learning_paths(request):
    """
    Get learning paths with optional filtering by user level and topic
    """
    try:
        # Get query parameters
        user_level = request.GET.get('user_level')
        topic = request.GET.get('topic')
        
        # Get learning paths from MongoDB
        learning_paths = mongo_service.get_learning_paths(
            user_level=user_level,
            topic=topic
        )
        
        # Format response
        formatted_paths = []
        for path in learning_paths:
            formatted_path = {
                'id': str(path.get('_id')),
                'name': path.get('name'),
                'description': path.get('description'),
                'target_level': path.get('target_level'),
                'topic': path.get('topic'),
                'videos': path.get('videos', []),
                'total_duration': path.get('total_duration'),
                'prerequisites': path.get('prerequisites', []),
                'learning_outcomes': path.get('learning_outcomes', [])
            }
            formatted_paths.append(formatted_path)
        
        return Response({
            'learning_paths': formatted_paths,
            'count': len(formatted_paths),
            'filters': {
                'user_level': user_level,
                'topic': topic
            }
        })
        
    except Exception as e:
        logger.error(f"Error in get_learning_paths: {str(e)}")
        return Response(
            {'error': 'Failed to fetch learning paths'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_learning_path_detail(request, path_id):
    """
    Get detailed information about a specific learning path
    """
    try:
        # Get learning path from MongoDB
        learning_path = mongo_service.get_learning_path_by_id(path_id)
        
        if not learning_path:
            return Response(
                {'error': 'Learning path not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get detailed video information for each video in the path
        detailed_videos = []
        for video_info in learning_path.get('videos', []):
            video_id = video_info.get('video_id')
            if video_id:
                video_detail = mongo_service.get_curated_video_by_id(video_id)
                if video_detail:
                    detailed_video = {
                        'video_id': video_id,
                        'title': video_detail.get('title'),
                        'duration': video_detail.get('duration'),
                        'topic': video_detail.get('topic'),
                        'difficulty': video_detail.get('difficulty'),
                        'order': video_info.get('order'),
                        'estimated_duration': video_info.get('estimated_duration'),
                        'learning_objectives': video_info.get('learning_objectives', []),
                        'metadata': {
                            'key_vocabulary': video_detail.get('metadata', {}).get('key_vocabulary', []),
                            'grammar_patterns': video_detail.get('metadata', {}).get('grammar_patterns', []),
                            'cultural_context': video_detail.get('metadata', {}).get('cultural_context', {})
                        }
                    }
                    detailed_videos.append(detailed_video)
        
        # Format response
        formatted_path = {
            'id': str(learning_path.get('_id')),
            'name': learning_path.get('name'),
            'description': learning_path.get('description'),
            'target_level': learning_path.get('target_level'),
            'topic': learning_path.get('topic'),
            'videos': detailed_videos,
            'total_duration': learning_path.get('total_duration'),
            'prerequisites': learning_path.get('prerequisites', []),
            'learning_outcomes': learning_path.get('learning_outcomes', [])
        }
        
        return Response(formatted_path)
        
    except Exception as e:
        logger.error(f"Error in get_learning_path_detail: {str(e)}")
        return Response(
            {'error': 'Failed to fetch learning path details'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([AllowAny])
def get_recommended_learning_paths(request):
    """
    Get recommended learning paths based on user preferences and progress
    """
    try:
        # Get query parameters
        user_level = request.GET.get('user_level', 'beginner')
        preferred_topic = request.GET.get('preferred_topic')
        max_duration = request.GET.get('max_duration')
        
        # Convert max_duration to int if provided
        try:
            max_duration = int(max_duration) if max_duration else None
        except ValueError:
            max_duration = None
        
        # Get all learning paths
        all_paths = mongo_service.get_learning_paths()
        
        # Filter and score paths based on preferences
        recommended_paths = []
        for path in all_paths:
            score = 0
            
            # Level matching
            if path.get('target_level') == user_level:
                score += 3
            elif path.get('target_level') == 'beginner' and user_level == 'intermediate':
                score += 1
            elif path.get('target_level') == 'intermediate' and user_level == 'beginner':
                score += 1
            
            # Topic matching
            if preferred_topic and path.get('topic') == preferred_topic:
                score += 2
            
            # Duration filtering
            if max_duration and path.get('total_duration', 0) > max_duration:
                continue
            
            # Add to recommendations if score > 0
            if score > 0:
                formatted_path = {
                    'id': str(path.get('_id')),
                    'name': path.get('name'),
                    'description': path.get('description'),
                    'target_level': path.get('target_level'),
                    'topic': path.get('topic'),
                    'total_duration': path.get('total_duration'),
                    'video_count': len(path.get('videos', [])),
                    'recommendation_score': score
                }
                recommended_paths.append(formatted_path)
        
        # Sort by recommendation score (descending)
        recommended_paths.sort(key=lambda x: x['recommendation_score'], reverse=True)
        
        # Limit to top 5 recommendations
        recommended_paths = recommended_paths[:5]
        
        return Response({
            'recommended_paths': recommended_paths,
            'count': len(recommended_paths),
            'preferences': {
                'user_level': user_level,
                'preferred_topic': preferred_topic,
                'max_duration': max_duration
            }
        })
        
    except Exception as e:
        logger.error(f"Error in get_recommended_learning_paths: {str(e)}")
        return Response(
            {'error': 'Failed to fetch recommended learning paths'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_user_progress(request):
    """
    Save or update user progress for a specific video
    """
    try:
        user_id = str(request.user_id)
        video_id = request.data.get('video_id')
        
        if not video_id:
            return Response(
                {'error': 'video_id is required'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Prepare progress data
        progress_data = {
            'user_id': user_id,
            'video_id': video_id,
            'completion_status': request.data.get('completion_status', 'in_progress'),
            'time_spent': request.data.get('time_spent', 0),
            'scores': request.data.get('scores', {}),
            'last_watched': datetime.utcnow(),
            'notes': request.data.get('notes', ''),
            'difficulty_rating': request.data.get('difficulty_rating'),
            'learning_path_id': request.data.get('learning_path_id')
        }
        
        # Save progress to MongoDB
        result = mongo_service.save_user_learning_progress(user_id, video_id, progress_data)
        
        return Response({
            'message': 'Progress saved successfully',
            'user_id': user_id,
            'video_id': video_id,
            'completion_status': progress_data['completion_status']
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error in save_user_progress: {str(e)}")
        return Response(
            {'error': 'Failed to save user progress'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_progress(request):
    """
    Get user progress for all videos or a specific video
    """
    try:
        user_id = str(request.user_id)
        video_id = request.GET.get('video_id')
        
        # Get progress from MongoDB
        progress_records = mongo_service.get_user_learning_progress(user_id, video_id)
        
        # Format response
        formatted_progress = []
        for record in progress_records:
            formatted_record = {
                'id': str(record.get('_id')),
                'video_id': record.get('video_id'),
                'completion_status': record.get('completion_status'),
                'time_spent': record.get('time_spent', 0),
                'scores': record.get('scores', {}),
                'last_watched': record.get('last_watched'),
                'notes': record.get('notes', ''),
                'difficulty_rating': record.get('difficulty_rating'),
                'learning_path_id': record.get('learning_path_id')
            }
            formatted_progress.append(formatted_record)
        
        return Response({
            'progress': formatted_progress,
            'count': len(formatted_progress)
        })
        
    except Exception as e:
        logger.error(f"Error in get_user_progress: {str(e)}")
        return Response(
            {'error': 'Failed to fetch user progress'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_learning_stats(request):
    """
    Get comprehensive learning statistics for the user
    """
    try:
        user_id = str(request.user_id)
        
        # Get learning statistics from MongoDB
        stats = mongo_service.get_user_learning_stats(user_id)
        
        # Format response
        formatted_stats = {
            'user_id': user_id,
            'total_videos_watched': stats.get('total_videos_watched', 0),
            'total_time_spent': stats.get('total_time_spent', 0),
            'completion_rate': stats.get('completion_rate', 0),
            'average_score': stats.get('average_score', 0),
            'videos_by_status': stats.get('videos_by_status', {}),
            'videos_by_topic': stats.get('videos_by_topic', {}),
            'videos_by_difficulty': stats.get('videos_by_difficulty', {}),
            'recent_activity': stats.get('recent_activity', []),
            'learning_streak': stats.get('learning_streak', 0),
            'total_learning_paths': stats.get('total_learning_paths', 0)
        }
        
        return Response(formatted_stats)
        
    except Exception as e:
        logger.error(f"Error in get_user_learning_stats: {str(e)}")
        return Response(
            {'error': 'Failed to fetch learning statistics'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_video_completion(request, video_id):
    """
    Update completion status for a specific video
    """
    try:
        user_id = str(request.user_id)
        completion_status = request.data.get('completion_status', 'completed')
        
        # Prepare update data
        update_data = {
            'completion_status': completion_status,
            'last_watched': datetime.utcnow()
        }
        
        # Add optional fields if provided
        if 'time_spent' in request.data:
            update_data['time_spent'] = request.data['time_spent']
        if 'scores' in request.data:
            update_data['scores'] = request.data['scores']
        if 'notes' in request.data:
            update_data['notes'] = request.data['notes']
        if 'difficulty_rating' in request.data:
            update_data['difficulty_rating'] = request.data['difficulty_rating']
        
        # Save progress to MongoDB
        result = mongo_service.save_user_learning_progress(user_id, video_id, update_data)
        
        return Response({
            'message': f'Video {video_id} marked as {completion_status}',
            'video_id': video_id,
            'completion_status': completion_status
        })
        
    except Exception as e:
        logger.error(f"Error in update_video_completion: {str(e)}")
        return Response(
            {'error': 'Failed to update video completion'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
