"""Small dependency-free client for Ollama's local HTTP API."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import Callable, Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


class OllamaError(RuntimeError):
    """A friendly error raised when the local Ollama service cannot be used."""


@dataclass(frozen=True)
class OllamaStatus:
    state: str
    message: str
    version: str = ""


class OllamaClient:
    def __init__(self, base_url: str = "http://127.0.0.1:11434", timeout: float = 5,
                 opener: Callable = urlopen):
        parsed = urlparse(base_url)
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            raise ValueError("Ollama URL must be an http(s) URL")
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._open = opener

    def _json(self, path: str) -> dict:
        try:
            with self._open(f"{self.base_url}{path}", timeout=self.timeout) as response:
                return json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, OSError, ValueError, json.JSONDecodeError) as error:
            raise OllamaError(str(error)) from error

    def version(self) -> str:
        return str(self._json("/api/version").get("version", "unknown"))

    def models(self) -> list[str]:
        payload = self._json("/api/tags")
        return [str(item.get("name", "")) for item in payload.get("models", [])]

    def status(self, model: str) -> OllamaStatus:
        try:
            version = self.version()
            models = self.models()
        except OllamaError:
            return OllamaStatus("unavailable", "Ollama не отвечает")
        aliases = {name.removesuffix(":latest") for name in models}
        if model not in models and model.removesuffix(":latest") not in aliases:
            return OllamaStatus("model_missing", f"Нужна модель {model}", version)
        return OllamaStatus("ready", f"Готово: {model}", version)

    def pull(self, model: str, progress: Callable[[int, str], None] | None = None) -> None:
        body = json.dumps({"model": model, "stream": True}).encode("utf-8")
        request = Request(f"{self.base_url}/api/pull", data=body,
                          headers={"Content-Type": "application/json"}, method="POST")
        try:
            with self._open(request, timeout=None) as response:
                self._consume_pull(response, progress)
        except (HTTPError, URLError, TimeoutError, OSError, ValueError, json.JSONDecodeError) as error:
            raise OllamaError(str(error)) from error

    @staticmethod
    def _consume_pull(lines: Iterable[bytes], progress: Callable[[int, str], None] | None) -> None:
        for line in lines:
            if not line.strip():
                continue
            event = json.loads(line.decode("utf-8"))
            if event.get("error"):
                raise OllamaError(str(event["error"]))
            total = int(event.get("total", 0) or 0)
            completed = int(event.get("completed", 0) or 0)
            percent = min(100, round(completed * 100 / total)) if total else 0
            if progress:
                progress(percent, str(event.get("status", "")))
