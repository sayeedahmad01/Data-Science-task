import asyncio
import os
from dotenv import load_dotenv

from autogen_core.models import UserMessage,ModelInfo  
from autogen_ext.models.openai import OpenAIChatCompletionClient

load_dotenv()

async def main():

    gemini_api_key = os.getenv("GEMINI_API_KEY") 
    if not gemini_api_key:
        raise ValueError('GEMINI_API_KEY is not found')

    gemini_model_info = ModelInfo(
        vision=True,
        function_calling=True,
        json_output=True,
        family='gemini')

    model_client = OpenAIChatCompletionClient(
        model = 'gemini-3-flash-preview',
        api_key = gemini_api_key,
        base_url = 'https://generativelanguage.googleapis.com/v1beta/openai/',
        model_info = gemini_model_info)
    
    response = await model_client.create([
        UserMessage(content="What is Autogen framework in agenticai", source="user")       
    ])

    print('Response:\n', response.content)

    await model_client.close()

if __name__ == "__main__":
    asyncio.run(main()) 

    

    

                         











