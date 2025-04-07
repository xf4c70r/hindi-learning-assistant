# -*- coding: utf-8 -*-
import os
from openai import OpenAI
from dotenv import load_dotenv
from .prompts import system
import json

# Load environment variables from root directory
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
load_dotenv(os.path.join(root_dir, '.env'))

class DeepSeekQAModel:
    _instance = None
    _is_initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DeepSeekQAModel, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._is_initialized:
            self._is_initialized = True
            self.client = None

    def _ensure_initialized(self):
        """Lazy initialization of the API client"""
        if self.client is None:
            api_key = os.getenv("DEEPSEEK_API_KEY", "").strip()
            if not api_key:
                raise ValueError("DEEPSEEK_API_KEY not found in environment variables")
                
            if not api_key.startswith("sk-"):
                raise ValueError("Invalid API key format. DeepSeek API key should start with 'sk-'")
                
            print(f"Initializing DeepSeek QA model with API key: {api_key[:5]}...")
                
            self.client = OpenAI(
                api_key=api_key,
                base_url="https://api.deepseek.com/v1"
            )

    def _query_model(self, user_input):
        """Internal method to query the DeepSeek model"""
        self._ensure_initialized()
        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user_input}
        ]
        response = self.client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            stream=False
        )
        return response.choices[0].message.content

    def generate_questions(self, transcript_text, question_type="novice"):
        """
        Generate questions from transcript text
        Args:
            transcript_text (str): The transcript text to generate questions from
            question_type (str): Type of questions to generate (novice/mcq/fill_blanks)
        Returns:
            dict: JSON response containing generated questions
        """
        prompt_templates = {
            "novice": """Generate 3-5 Novice level questions in JSON format.
                Return questions in this format:
                {
                    "qa_pairs": [
                        {
                            "question": "question text here",
                            "answer": "answer text here",
                            "type": "novice"
                        }
                    ]
                }""",
            
            "mcq": """Generate 3-5 Multiple Choice Questions (MCQs) in JSON format.
                Return questions in this format:
                {
                    "qa_pairs": [
                        {
                            "question": "question text here",
                            "answer": "correct answer here",
                            "type": "mcq",
                            "options": ["correct answer", "wrong option 1", "wrong option 2", "wrong option 3"]
                        }
                    ]
                }""",
            
            "fill_blanks": """Generate 3-5 Fill in the Blanks questions in JSON format.
                For each question, take a sentence from the text and replace a key word or phrase with '____'.
                Return questions in this format:
                {
                    "qa_pairs": [
                        {
                            "question": "sentence with ____ for blank",
                            "answer": "word or phrase that goes in blank",
                            "type": "fill_blanks"
                        }
                    ]
                }"""
        }

        prompt = f"""Please generate questions based on the following transcript text.
        Return ONLY a JSON object with NO additional text or formatting.
        
        Instructions:
        1. {prompt_templates.get(question_type, prompt_templates['novice'])}
        2. Ensure all text is in Hindi
        3. Make questions progressively more challenging
        4. Return ONLY the JSON object, no other text
        5. Ensure the JSON is properly formatted and valid
        
        Transcript Text:
        {transcript_text}"""

        try:
            response = self._query_model(prompt)
            
            # If response is already a list or dict, process it directly
            if isinstance(response, (list, dict)):
                if isinstance(response, list):
                    return {'qa_pairs': response}
                if 'qa_pairs' in response:
                    return response['qa_pairs']
                return {'qa_pairs': [response]}
            
            # If response is a string, try to parse it as JSON
            try:
                # Try to find JSON in the response
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                
                if json_start >= 0 and json_end > json_start:
                    json_str = response[json_start:json_end]
                    questions = json.loads(json_str)
                    if isinstance(questions, dict) and 'qa_pairs' in questions:
                        return questions['qa_pairs']
                    return {'qa_pairs': questions}
                else:
                    print("No JSON found in response:", response)
                    return []
            except json.JSONDecodeError as e:
                print(f"Failed to parse JSON response: {response}")
                print(f"Error: {str(e)}")
                return []
                
        except Exception as e:
            print(f"Error in generate_questions: {str(e)}")
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
        prompt = f"""Answer this question based on the given context.
        
        Context: {context}
        Question: {question}"""

        try:
            response = self._query_model(prompt)
            return response
        except Exception as e:
            raise ValueError(f"Failed to answer question: {str(e)}")

# Create a singleton instance
qa_model = DeepSeekQAModel() 