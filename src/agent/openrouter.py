
import os
from typing import Optional
from dotenv import load_dotenv
from langchain_core.utils.utils import secret_from_env
from langchain_openai import ChatOpenAI
from pydantic import Field, SecretStr

load_dotenv()

class ChatOpenRouter(ChatOpenAI):
    """
    A custom ChatOpenAI class that uses the OpenRouter API.
    """
    openrouter_api_key: Optional[SecretStr] = Field(
        alias="api_key",
        default_factory=secret_from_env("OPENROUTER_API_KEY", default=None),
    )

    @property
    def lc_secrets(self) -> dict[str, str]:
        return {"openrouter_api_key": "OPENROUTER_API_KEY"}

    def __init__(self, openrouter_api_key: Optional[str] = None, **kwargs):
        openrouter_api_key = (
            openrouter_api_key or os.environ.get("OPENROUTER_API_KEY")
        )
        super().__init__(
            base_url="https://openrouter.ai/api/v1",
            api_key=openrouter_api_key,
            **kwargs,
        )
