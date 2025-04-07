import os
import sys
from qa_engine.qa_model import qa_model
import json

def test_qa_model():
    """Test the QA model with a sample transcript"""
    try:
        # Sample transcript text in Hindi
        transcript_text = """
        नमस्ते, मैं आज आपको भारत के बारे में कुछ महत्वपूर्ण जानकारी देना चाहता हूं।
        भारत दुनिया का सबसे बड़ा लोकतंत्र है। यहाँ की आबादी लगभग 140 करोड़ है।
        भारत में 28 राज्य और 8 केंद्र शासित प्रदेश हैं।
        भारत की राजधानी नई दिल्ली है।
        """
        
        print("Testing QA model with sample transcript...")
        print("\nGenerating novice questions...")
        questions = qa_model.generate_questions(transcript_text, "novice")
        print("\nGenerated Questions:")
        print(json.dumps(questions, indent=2, ensure_ascii=False))
        
        print("\nGenerating MCQ questions...")
        mcq_questions = qa_model.generate_questions(transcript_text, "mcq")
        print("\nGenerated MCQ Questions:")
        print(json.dumps(mcq_questions, indent=2, ensure_ascii=False))
        
        print("\nTest completed successfully!")
        
    except Exception as e:
        print(f"\nError testing QA model: {str(e)}")
        import traceback
        print(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    test_qa_model() 