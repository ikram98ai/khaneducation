from agents import AsyncOpenAI, OpenAIChatCompletionsModel
from dotenv import load_dotenv
import os

load_dotenv()

def get_model():
    gemini_client = AsyncOpenAI(
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        api_key=os.getenv("GEMINI_API_KEY")
    )
    model = OpenAIChatCompletionsModel(
        openai_client=gemini_client,
        model="gemini-2.0-flash-lite"
    )

    return model

