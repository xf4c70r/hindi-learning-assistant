# -*- coding: utf-8 -*-
import os
from openai import OpenAI
from dotenv import load_dotenv
from .prompts import system, transcript_system, translation_system, glossary_system
import json
import logging
import re
from typing import Dict

# Load environment variables from root directory
root_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
load_dotenv(os.path.join(root_dir, '.env'))

logger = logging.getLogger(__name__)

class DeepSeekQAModel:
    _instance = None
    _is_initialized = False

    # System prompts
    word_system_prompt = """You are a Hindi language teacher explaining words to beginners. Keep explanations clear and concise.
    Format your response as:

    {
        "meaning": "simple English meaning (1-2 words)",
        "example": {
            "hindi": "one simple example sentence",
            "english": "its English translation"
        }
    }"""

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

    def _query_model(self, user_input, system_prompt=None, temperature=None):
        """Internal method to query the DeepSeek model"""
        self._ensure_initialized()
        messages = [
            {"role": "system", "content": system_prompt or system},
            {"role": "user", "content": user_input}
        ]
        
        params = {
            "model": "deepseek-chat",
            "messages": messages,
            "stream": False
        }
        if temperature is not None:
            params["temperature"] = temperature
            
        response = self.client.chat.completions.create(**params)
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
            response = self._query_model(user_input=prompt)
            
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
                    logger.error("No JSON found in response:", response)
                    return []
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {response}")
                logger.error(f"Error: {str(e)}")
                return []
                
        except Exception as e:
            logger.error(f"Error in generate_questions: {str(e)}")
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

    def query_word_meaning(self, word: str):
        """Get meaning and example for a Hindi word"""
        prompt = f"""Explain the Hindi word '{word}' with:
        1. Basic meaning in simple English (keep it brief)
        2. One simple example sentence showing common usage
        Return ONLY the JSON object."""
        
        try:
            response = self._query_model(
                user_input=prompt,
                system_prompt=self.word_system_prompt
            )

            # Try to parse JSON from the response
            try:
                # Try to find JSON in the response
                json_start = response.find('{')
                json_end = response.rfind('}') + 1
                
                if json_start >= 0 and json_end > json_start:
                    json_str = response[json_start:json_end]
                    meaning_data = json.loads(json_str)
                    return meaning_data
                else:
                    raise ValueError("No valid JSON found in response")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse JSON response: {response}")
                raise ValueError(f"Invalid response format: {str(e)}")
                
        except Exception as e:
            logger.error(f"Error querying word meaning: {str(e)}")
            raise ValueError(f"Failed to get word meaning: {str(e)}")

    def process_transcript(self, transcript_text: str) -> dict:
        """
        Process Hindi transcript text to add punctuation.
        Returns a dictionary with punctuated text.
        """
        if not transcript_text or not transcript_text.strip():
            raise ValueError("Empty transcript text provided")

        # Log the input
        logger.info(f"Processing transcript of length: {len(transcript_text)}")
        
        # Clean the input text
        transcript_text = transcript_text.strip()
        transcript_text = re.sub(r'\s+', ' ', transcript_text)  # Normalize whitespace
        
        # Construct the user message with STRICT formatting requirements
        user_message = f"""Process this Hindi text and return ONLY a valid JSON object with the following structure:
{{
    "punctuated_text": "Hindi text with proper punctuation"
}}

CRITICAL REQUIREMENTS:
1. DO NOT use any markdown code blocks (```)
2. DO NOT add any text before or after the JSON
3. The response must start with {{ and end with }}
4. Return the raw JSON only
5. Keep responses focused and concise
6. Only add proper punctuation (।, ?, !, etc.) to the text
7. Do not translate or add vocabulary explanations

Here is the text to process:

{transcript_text}"""
        
        # Get response from DeepSeek with very low temperature for consistency
        response = self._query_model(
            user_input=user_message,
            system_prompt=transcript_system,
            temperature=0.1
        )
        
        # Log the raw response
        print("\n=== RAW RESPONSE FROM DEEPSEEK ===")
        print(response)
        print("=== END RAW RESPONSE ===\n")
        
        processed_data = None
        response_text = response.strip()
        
        def clean_markdown(text):
            """Remove markdown code block markers"""
            if text.startswith('```json'):
                text = text[7:].strip()
            elif text.startswith('```'):
                text = text[3:].strip()
            if text.endswith('```'):
                text = text[:-3].strip()
            return text
        
        def extract_json(text):
            """Extract JSON from text"""
            json_start = text.find('{')
            json_end = text.rfind('}') + 1
            if json_start >= 0 and json_end > json_start:
                return text[json_start:json_end]
            return text
        
        # First try to parse the response directly after removing markdown
        try:
            response_text = clean_markdown(response_text)
            processed_data = json.loads(response_text)
            logger.info("Successfully parsed JSON directly from response")
            return self._validate_processed_data(processed_data)
        except json.JSONDecodeError:
            logger.info("Could not parse response directly as JSON, attempting cleanup")
        except Exception as e:
            logger.error(f"Unexpected error during initial JSON parsing: {str(e)}")
        
        # If direct parsing failed, try more aggressive cleaning
        try:
            # Check if response is incomplete
            if response_text.count('{') != response_text.count('}'):
                logger.warning("Response appears to be incomplete (unmatched braces)")
                stack = []
                start_idx = response_text.find('{')
                if start_idx == -1:
                    raise ValueError("No JSON object found in response")
                
                for i, char in enumerate(response_text[start_idx:], start=start_idx):
                    if char == '{':
                        stack.append(i)
                    elif char == '}':
                        if stack:
                            start = stack.pop()
                            if not stack:  # We found a complete object
                                response_text = response_text[start:i+1]
                                break
                
                if stack:  # Still incomplete
                    raise ValueError("Could not find complete JSON object in response")
            
            # Extract JSON and remove any remaining markdown
            response_text = extract_json(clean_markdown(response_text))
            
            print("\n=== CLEANED JSON ===")
            print(response_text)
            print("=== END CLEANED JSON ===\n")
            
            try:
                processed_data = json.loads(response_text)
                logger.info("Successfully parsed JSON after cleaning")
            except json.JSONDecodeError as e:
                logger.error(f"JSON Parse Error: {str(e)}")
                logger.error(f"Failed JSON text: {response_text}")
                # Try to fix common JSON issues
                fixed_text = response_text.replace('\n', ' ').replace('\r', '')
                fixed_text = re.sub(r'\s+', ' ', fixed_text)
                try:
                    processed_data = json.loads(fixed_text)
                    logger.info("Successfully parsed JSON after fixing formatting")
                except json.JSONDecodeError as e:
                    raise ValueError(f"Could not parse response as valid JSON even after cleanup: {str(e)}")
            
            if processed_data is None:
                raise ValueError("Failed to parse JSON from response")
            
            return self._validate_processed_data(processed_data)
            
        except Exception as e:
            logger.error(f"Error in process_transcript: {str(e)}")
            logger.error(f"Original transcript preview: {transcript_text[:200]}")
            raise ValueError(f"Failed to process transcript: {str(e)}")

    def _validate_processed_data(self, processed_data: dict) -> dict:
        """Validate the processed data structure and content"""
        # Validate the structure
        if 'punctuated_text' not in processed_data:
            raise ValueError("Missing required field 'punctuated_text' in response")
        
        # Validate content
        if not processed_data['punctuated_text'].strip():
            raise ValueError("Punctuated text is empty")
        
        return processed_data

    def translate_text(self, hindi_text: str) -> dict:
        """
        Translate Hindi text to English.
        Returns a dictionary with the translation.
        """
        if not hindi_text or not hindi_text.strip():
            raise ValueError("Empty text provided for translation")

        # Log the input
        logger.info(f"Translating text of length: {len(hindi_text)}")
        logger.info(f"Input text: {hindi_text[:100]}...")  # Log first 100 chars
        
        # Clean the input text
        hindi_text = hindi_text.strip()
        
        # Construct the user message with STRICT formatting requirements
        user_message = f"""Translate this Hindi text to English and return ONLY a valid JSON object with the following structure:
{{
    "translation": "English translation of the text"
}}

CRITICAL REQUIREMENTS:
1. DO NOT use any markdown code blocks (```)
2. DO NOT add any text before or after the JSON
3. The response must start with {{ and end with }}
4. Return the raw JSON only
5. Translate based on context, not word-for-word
6. Maintain natural and fluent English
7. Preserve cultural context and idioms
8. Keep the same level of formality as the original

Here is the text to translate:

{hindi_text}"""
        
        try:
            # Get response from DeepSeek with very low temperature for consistency
            response = self._query_model(
                user_input=user_message,
                system_prompt=translation_system,
                temperature=0.1
            )
            
            # Log the raw response
            logger.info(f"Raw translation response: {response}")
            
            if not response or not response.strip():
                raise ValueError("Empty response received from translation model")
            
            # Clean the response
            response = response.strip()
            
            # Remove any markdown code blocks if present
            if response.startswith('```json'):
                response = response[7:].strip()
            elif response.startswith('```'):
                response = response[3:].strip()
            if response.endswith('```'):
                response = response[:-3].strip()
            
            # Try to parse the response as JSON
            try:
                translation_data = json.loads(response)
            except json.JSONDecodeError as e:
                logger.error(f"JSON Parse Error: {str(e)}")
                logger.error(f"Failed JSON text: {response}")
                raise ValueError(f"Invalid translation response format: {str(e)}")
            
            # Validate the response structure
            if not isinstance(translation_data, dict):
                raise ValueError("Translation response is not a dictionary")
            
            if 'translation' not in translation_data:
                raise ValueError("Missing required field 'translation' in response")
            
            if not translation_data['translation'].strip():
                raise ValueError("Translation is empty")
            
            return translation_data
            
        except Exception as e:
            logger.error(f"Error in translate_text: {str(e)}")
            raise ValueError(f"Failed to translate text: {str(e)}")

    def generate_glossary(self, hindi_text: str) -> Dict[str, Dict[str, str]]:
        """
        Generate a glossary of important Hindi words and phrases from the text.
        
        Args:
            hindi_text: The Hindi text to analyze
            
        Returns:
            Dictionary containing word/phrase entries with their meanings, examples, and usage notes
        """
        if not hindi_text:
            raise ValueError("Input text cannot be empty")
        
        logger.info(f"Generating glossary for text of length {len(hindi_text)}")
        
        user_message = f"""Please analyze this Hindi text and create a glossary of important words and phrases:

{hindi_text}

Return a valid JSON object with the following structure:
{{
    "glossary": [
        {{
            "word": "Hindi word or phrase",
            "meaning": "English meaning",
            "example": "Simple example sentence in Hindi",
            "example_translation": "English translation of example"
        }}
    ]
}}

Requirements:
- Focus on culturally significant or commonly used words/phrases
- Include both literal and contextual meanings
- Provide clear examples in Hindi with English translations
- Return only the JSON object with no additional text
"""
        
        response = self._query_model(
            user_input=user_message,
            system_prompt=glossary_system,
            temperature=0.3  # Lower temperature for more consistent responses
        )
        
        try:
            glossary = json.loads(response)
            if not isinstance(glossary, dict) or "glossary" not in glossary:
                raise ValueError("Response must be a JSON object with a 'glossary' key")
            
            # Validate each entry has required fields
            for entry in glossary["glossary"]:
                if not all(key in entry for key in ["word", "meaning", "example", "example_translation"]):
                    raise ValueError(f"Missing required fields in glossary entry: {entry}")
                
            return glossary
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse glossary response: {e}")
            raise ValueError("Invalid JSON response from model")
        except Exception as e:
            logger.error(f"Error processing glossary: {e}")
            raise

# Create a singleton instance
qa_model = DeepSeekQAModel() 