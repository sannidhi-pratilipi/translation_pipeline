import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(
    api_key=os.getenv("TFY_API_KEY"),
    base_url=os.getenv("TFY_BASE_URL"),
)

def complete_gemini(
    messages,
    model="google-vertex/gemini-2-5-pro",
    temperature=0.1,
    max_tokens=2500,
) -> str:
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        extra_headers={
            "X-TFY-METADATA": "{}",
            "X-TFY-LOGGING-CONFIG": '{"enabled": true}',
        },
    )

    if (
        response.choices
        and len(response.choices) > 0
        and response.choices[0].message
        and response.choices[0].message.content
    ):
        return response.choices[0].message.content.strip()

    return ""
