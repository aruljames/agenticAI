# import httpx
import requests
from openai import AsyncOpenAI
import os
from app.langfuse_client import getClient
import re

MODEL_NAME = os.getenv("MODEL_NAME")
# OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
# OPENROUTER_API_URL = os.getenv("OPENROUTER_API_URL")
OLLAMA_URL = os.getenv("OLLAMA_BASE_URL", "http://host.docker.internal:11434")


def clean_llm_json(raw: str) -> str:
    """
    Remove ```json ... ``` or ``` ... ``` wrappers and return pure JSON text.
    """
    if not raw:
        return raw

    # Remove surrounding code fences
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw.strip(), flags=re.DOTALL)

    return cleaned.strip()

async def llm(prompt: str):
    client = AsyncOpenAI(
        api_key="ollama",  # Ollama doesn't require a real API key
        base_url=f"{OLLAMA_URL}/v1"
    )

    try:
        response = await client.chat.completions.create(
            model=MODEL_NAME,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a strict JSON generator. "
                        "Always respond ONLY with valid JSON. "
                        "No markdown, no explanations."
                    )
                },
                {"role": "user", "content": prompt}
            ]
        )
        raw = response.choices[0].message.content.strip()
        cleaned = clean_llm_json(raw)
        return cleaned
    
    
    except Exception as e:
        print(f"Error calling LLM: {e}")
        raise

    # trace = getClient().trace(name="llm_call", input=prompt)
    # headers = {
    #     "Authorization": f"Bearer {OPENROUTER_API_KEY}",
    #     "Content-Type": "application/json"
    # }

    # payload = {
    #     "model": MODEL_NAME,
    #     "messages": [{"role": "user", "content": prompt}]
    # }

    # try:
    #     async with httpx.AsyncClient(timeout=40) as client:
    #         response = await client.post(
    #             OPENROUTER_API_URL,
    #             headers=headers,
    #             json=payload
    #         )
    #         response.raise_for_status()
    #         data = response.json()
    #         output = data["choices"][0]["message"]["content"]

    #         trace.update(output=output, status="completed")
    #         return output

    # except Exception as e:
    #     trace.update(output=str(e), status="error")
    #     raise
