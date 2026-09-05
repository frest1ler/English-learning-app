"""Process-level application configuration."""

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class AppConfig:
    ollama_url: str = "http://127.0.0.1:11434"
    ollama_model: str = "qwen3:4b"
    log_level: str = "INFO"

    @classmethod
    def from_environment(cls) -> "AppConfig":
        return cls(
            ollama_url=os.environ.get("ENGLISH_LEARNING_OLLAMA_URL", cls.ollama_url).rstrip("/"),
            ollama_model=os.environ.get("ENGLISH_LEARNING_OLLAMA_MODEL", cls.ollama_model),
            log_level=os.environ.get("ENGLISH_LEARNING_LOG_LEVEL", cls.log_level).upper(),
        )
