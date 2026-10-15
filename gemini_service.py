from google import genai
from config import Config

# Validate settings before triggering endpoints
Config.validate()

# Initialize the modern unified Google GenAI Client
client = genai.Client(api_key=Config.GEMINI_API_KEY)

def generate_chat_response(prompt: str) -> str:
    """
    Sends the user prompt to the Gemini API and returns the generated text.
    """
    try:
        response = client.models.generate_content(
            model=Config.MODEL_NAME,
            contents=prompt,
        )
        return response.text
    except Exception as e:
        print(f"Error calling Gemini API: {e}")
        return "Sorry, I encountered an error processing your request. Please check your backend logs."