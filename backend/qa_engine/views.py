from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Transcript, Question
from .serializers import TranscriptSerializer, QuestionSerializer
from .qa_model import qa_model
from .services import mongo_service
import logging

# Use the correct logger name that matches our settings
logger = logging.getLogger('qa_engine')

class TranscriptViewSet(viewsets.ModelViewSet):
    queryset = Transcript.objects.all()
    serializer_class = TranscriptSerializer
    
    @action(detail=True, methods=['post'])
    def translate(self, request, pk=None):
        transcript = self.get_object()
        try:
            # Get the transcript content from MongoDB
            mongo_transcript = mongo_service.get_transcript(transcript._id)
            if not mongo_transcript or 'content' not in mongo_transcript:
                return Response({'error': 'Transcript content not found'}, status=status.HTTP_404_NOT_FOUND)
                
            translation = qa_model.translate_text(mongo_transcript['content'])
            mongo_service.update_transcript(transcript._id, {'translation': translation})
            return Response({'translation': translation})
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
            
    @action(detail=True, methods=['post'])
    def generate_glossary(self, request, pk=None):
        try:
            # Get the transcript directly from MongoDB
            transcript_id = pk
            logger.info(f"Looking up transcript with ID: {transcript_id}")
            
            mongo_transcript = mongo_service.get_transcript(transcript_id)
            logger.info(f"MongoDB transcript: {mongo_transcript}")
            logger.info(f"MongoDB transcript keys: {list(mongo_transcript.keys()) if mongo_transcript else 'None'}")
            
            if not mongo_transcript:
                logger.error(f"Transcript not found in MongoDB for ID: {transcript_id}")
                return Response({'error': 'Transcript not found in MongoDB'}, status=status.HTTP_404_NOT_FOUND)
            
            # Get the content field directly
            content = mongo_transcript.get('content')
            logger.info(f"Content from MongoDB: {content[:100] if content else 'None'}")
            
            if not content:
                logger.error(f"Transcript content not found. Available fields: {list(mongo_transcript.keys())}")
                return Response({'error': 'Transcript content not found'}, status=status.HTTP_404_NOT_FOUND)
            
            # Generate glossary using the content
            glossary_data = qa_model.generate_glossary(content)
            logger.info(f"Generated glossary data: {glossary_data}")
            
            # Extract the glossary array from the response
            if not isinstance(glossary_data, dict) or 'glossary' not in glossary_data:
                logger.error(f"Invalid glossary format received: {glossary_data}")
                return Response({'error': 'Invalid glossary format'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            # Structure the glossary according to MongoDB schema
            glossary = {
                'glossary': glossary_data['glossary']
            }
            
            # Update the transcript in MongoDB with the new glossary
            mongo_service.update_transcript(transcript_id, {'glossary': glossary})
            
            # Return the glossary in the expected format
            return Response(glossary)
        except Exception as e:
            logger.error(f"Error in glossary generation: {str(e)}")
            logger.error(f"Error type: {type(e)}")
            logger.error(f"Error details: {str(e.__class__.__name__)}: {str(e)}")
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.all()
    serializer_class = QuestionSerializer 