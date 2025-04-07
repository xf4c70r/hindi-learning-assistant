import json
from qa_engine.qa_model import qa_model
from typing import Dict, List, Optional, Union

class QAService:
    def __init__(self):
        self.qa_model = qa_model

    def generate_questions(self, text, question_type="novice"):
        """
        Generate questions from text
        Args:
            text (str): The text to generate questions from
            question_type (str): Type of questions to generate (novice/mcq/fill_blanks)
        Returns:
            list: List of question dictionaries
        """
        try:
            # Get raw response from model
            response = self.qa_model.generate_questions(text, question_type)
            
            # If response is already a list, return it
            if isinstance(response, list):
                return response
                
            # If response is a dict with qa_pairs, return the pairs
            if isinstance(response, dict) and 'qa_pairs' in response:
                return response['qa_pairs']
                
            # If we got here, something went wrong
            print("Unexpected response format:", response)
            return []
                
        except Exception as e:
            print(f"Error in QA service: {str(e)}")
            raise ValueError(f"Failed to generate questions: {str(e)}")

    def answer_question(self, context, question):
        """
        Answer a question based on the context
        Args:
            context (str): The context text
            question (str): The question to answer
        Returns:
            str: The answer to the question
        """
        try:
            return self.qa_model.answer_question(context, question)
        except Exception as e:
            raise ValueError(f"Failed to answer question: {str(e)}")

    @staticmethod
    def validate_question_type(question_type: str) -> bool:
        """
        Validate if the question type is supported
        
        Args:
            question_type (str): Type of questions to generate
            
        Returns:
            bool: True if valid, False otherwise
        """
        valid_types = ["novice", "mcq", "fill_blanks"]
        return question_type.lower() in valid_types

    @staticmethod
    def get_supported_question_types() -> List[str]:
        """
        Get list of supported question types
        
        Returns:
            List[str]: List of supported question types
        """
        return ["novice", "mcq", "fill_blanks"]

# Create a singleton instance
qa_service = QAService() 