from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class Settings:
    """Application settings loaded from environment.

    Keep minimal and explicit to avoid surprises.
    """

    # LLM / providers
    openai_api_key: Optional[str]
    model: str

    # Integrations (optional)
    tavily_api_key: Optional[str]
    odds_api_key: Optional[str]

    # Observability
    langsmith_api_key: Optional[str]
    langchain_tracing_v2: bool

    # Networking
    http_timeout_s: float
    http_retries: int

    @staticmethod
    def load() -> "Settings":
        def getenv_bool(name: str, default: bool = False) -> bool:
            val = os.getenv(name)
            if val is None:
                return default
            return val.strip().lower() in {"1", "true", "yes", "on"}

        return Settings(
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            model=os.getenv("MODEL", "gpt-4o-mini"),
            tavily_api_key=os.getenv("TAVILY_API_KEY"),
            odds_api_key=os.getenv("ODDS_API_KEY"),
            langsmith_api_key=os.getenv("LANGSMITH_API_KEY"),
            langchain_tracing_v2=getenv_bool("LANGCHAIN_TRACING_V2", False),
            http_timeout_s=float(os.getenv("HTTP_TIMEOUT_S", "20")),
            http_retries=int(os.getenv("HTTP_RETRIES", "2")),
        )

