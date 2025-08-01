import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv('DEEPSEEK_API_KEY'),
    base_url="https://api.deepseek.com/v1"  # Deepseek's API endpoint
)

def deepseek_query(prompt):
    """
    Query the Deepseek API with a prompt
    """
    try:
        response = client.chat.completions.create(
            model="deepseek-chat",  # or whatever model you're using
            messages=[
                {"role": "system", "content": "You are a helpful assistant that explains Hindi words in English."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=8000
        )
        return response.choices[0].message.content
    except Exception as e:
        raise Exception(f"Error querying Deepseek API: {str(e)}")
