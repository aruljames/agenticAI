import httpx
import os
from app.langfuse_client import getClient

MODEL_NAME = os.getenv("MODEL_NAME")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
OPENROUTER_API_URL = os.getenv("OPENROUTER_API_URL")

async def llm(prompt: str):
    trace = getClient().trace(name="llm_call", input=prompt)
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": MODEL_NAME,
        "messages": [{"role": "user", "content": prompt}]
    }

    try:
        async with httpx.AsyncClient(timeout=40) as client:
            response = await client.post(
                OPENROUTER_API_URL,
                headers=headers,
                json=payload
            )
            response.raise_for_status()
            data = response.json()
            output = data["choices"][0]["message"]["content"]

            trace.update(output=output, status="completed")
            return output

    except Exception as e:
        trace.update(output=str(e), status="error")
        raise
