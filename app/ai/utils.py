from agents import AsyncOpenAI, OpenAIChatCompletionsModel
from dotenv import load_dotenv
import os

load_dotenv()


def get_model():
    gemini_client = AsyncOpenAI(base_url="https://generativelanguage.googleapis.com/v1beta/openai/", api_key=os.getenv("GEMINI_API_KEY"))
    model = OpenAIChatCompletionsModel(openai_client=gemini_client, model="gemini-2.0-flash-lite")

    return model


async def get_completion(instruction: str, user_messages: str | list, output_type=None, model="gemini-2.0-flash-lite"):
    client = AsyncOpenAI(base_url="https://generativelanguage.googleapis.com/v1beta/openai/", api_key=os.getenv("GEMINI_API_KEY"))
    if isinstance(user_messages, str):
        user_messages = [{"role": "user", "content": user_messages}]

    if output_type:
        completion = await client.chat.completions.parse(
            model=model,
            messages=[{"role": "system", "content": instruction}] + user_messages,
            response_format=output_type,
        )
        return completion.choices[-1].message.parsed

    response = await client.chat.completions.create(
        model=model,
        messages=[{"role": "system", "content": instruction}] + user_messages,
    )
    return response.choices[-1].message.content
