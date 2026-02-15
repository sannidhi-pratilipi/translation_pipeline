import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

_client = OpenAI(
    api_key=os.getenv("TFY_API_KEY"),
    base_url=os.getenv("TFY_BASE_URL"),
)

def complete_gpt(
    messages,
    model="openai/gpt-4-1-mini",
    temperature=0.3,
    max_tokens=2500,
) -> str:
    """
    Streaming chat completion wrapper.

    - Uses TFY gateway + logging headers
    - Returns final concatenated string output
    - No retries, no post-processing
    """

    stream = _client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        stream=True,
        extra_headers={
            "X-TFY-METADATA": "{}",
            "X-TFY-LOGGING-CONFIG": '{"enabled": true}',
        },
    )

    parts: list[str] = []

    for chunk in stream:
        if (
            chunk.choices
            and chunk.choices[0].delta
            and chunk.choices[0].delta.content
        ):
            parts.append(chunk.choices[0].delta.content)

    return "".join(parts).strip()
