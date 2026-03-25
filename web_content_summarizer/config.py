from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def _get_env(*keys: str) -> str | None:
    for key in keys:
        value = os.getenv(key)
        if value:
            return value.strip()
    return None


@dataclass(frozen=True)
class Settings:
    api_key: str
    model: str
    base_url: str | None
    request_timeout_seconds: float
    max_input_chars: int
    output_dir: Path

    @classmethod
    def from_env(cls) -> "Settings":
        api_key = _get_env("api_key", "OPENAI_API_KEY", "LLM_API_KEY")
        model = _get_env("model", "OPENAI_MODEL", "LLM_MODEL")
        base_url = _get_env("base_url", "OPENAI_BASE_URL", "LLM_BASE_URL")

        if not api_key:
            raise ValueError("Missing API key in .env (api_key or OPENAI_API_KEY).")
        if not model:
            raise ValueError("Missing model in .env (model or OPENAI_MODEL).")

        timeout_raw = _get_env("request_timeout_seconds", "REQUEST_TIMEOUT_SECONDS")
        max_input_raw = _get_env("max_input_chars", "MAX_INPUT_CHARS")
        output_dir_raw = _get_env("output_dir", "OUTPUT_DIR")

        request_timeout_seconds = float(timeout_raw) if timeout_raw else 20.0
        max_input_chars = int(max_input_raw) if max_input_raw else 12000
        output_dir = Path(output_dir_raw) if output_dir_raw else Path("runs")

        return cls(
            api_key=api_key,
            model=model,
            base_url=base_url,
            request_timeout_seconds=request_timeout_seconds,
            max_input_chars=max_input_chars,
            output_dir=output_dir,
        )
