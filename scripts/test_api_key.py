"""Direct API key test"""
import os
from dotenv import load_dotenv
import anthropic

load_dotenv()

api_key = os.getenv('ANTHROPIC_API_KEY')
print(f"Testing API key: {api_key[:20]}...{api_key[-10:]}")

try:
    client = anthropic.Anthropic(api_key=api_key)
    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=100,
        messages=[{"role": "user", "content": "Say 'API key works!'"}]
    )
    print(f" SUCCESS: {message.content[0].text}")
except anthropic.AuthenticationError as e:
    print(f" Authentication Error: {e}")
except Exception as e:
    print(f" Error: {e}")
