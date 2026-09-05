import io
import json

from english_learning.infrastructure.ollama_client import OllamaClient, OllamaStatus


class Response(io.BytesIO):
    def __enter__(self): return self
    def __exit__(self, *args): self.close()


def test_status_ready_and_missing():
    def ready(request, timeout=None):
        url = request if isinstance(request, str) else request.full_url
        payload = {"version": "1.2.3"} if url.endswith("version") else {"models": [{"name": "qwen3:4b"}]}
        return Response(json.dumps(payload).encode())
    client = OllamaClient(opener=ready)
    assert client.status("qwen3:4b") == OllamaStatus("ready", "Готово: qwen3:4b", "1.2.3")
    assert client.status("other:4b").state == "model_missing"


def test_pull_reports_stream_progress():
    values = []
    stream = b'{"status":"pulling","completed":5,"total":10}\n{"status":"success","completed":10,"total":10}\n'
    OllamaClient(opener=lambda request, timeout=None: Response(stream)).pull(
        "qwen3:4b", lambda value, status: values.append((value, status)))
    assert values == [(50, "pulling"), (100, "success")]
