import openai
import os
from openai import OpenAI
from dotenv import load_dotenv

def test_openai_key():
    # Load environment variables from .env file
    load_dotenv()
    
    try:
        # Initialize the client (it will automatically use OPENAI_API_KEY from env)
        client = OpenAI()
        
        # Try a simple completion
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": "Say 'API key is working!'"}
            ]
        )
        
        # Print the response
        print("OpenAI Response:", response.choices[0].message.content)
        print("\nAPI key is valid and working!")
        
    except Exception as e:
        print("\nError testing OpenAI API key:")
        print(str(e))

if __name__ == "__main__":
    print("Testing OpenAI API key...")
    test_openai_key() 