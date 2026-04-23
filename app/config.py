from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parent.parent
ENV_PATH = BASE_DIR / ".env"
load_dotenv(dotenv_path=ENV_PATH, override=False)


def _to_bool(value: str | None, default: bool) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass(frozen=True)
class AppConfig:
    ollama_base_url: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    ollama_model: str = os.getenv("OLLAMA_MODEL", "qwen3:1.7b")
    embedding_model: str = os.getenv("EMBEDDING_MODEL", "nomic-embed-text")
    chroma_path: str = os.getenv("CHROMA_PATH", str(BASE_DIR / "db" / "chroma"))
    top_k: int = int(os.getenv("TOP_K", "3"))
    temperature: float = float(os.getenv("TEMPERATURE", "0.2"))
    num_predict: int = int(os.getenv("NUM_PREDICT", "160"))
    app_title: str = os.getenv("APP_TITLE", "Machine Trouble AI")
    request_timeout_sec: int = int(os.getenv("REQUEST_TIMEOUT_SEC", "30"))
    rag_enabled: bool = _to_bool(os.getenv("RAG_ENABLED"), default=True)


def load_config() -> AppConfig:
    return AppConfig()