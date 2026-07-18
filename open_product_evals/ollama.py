"""Minimal Ollama client implemented with the Python standard library."""

from __future__ import annotations

import json
import time
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


class OllamaError(RuntimeError):
    """Raised when a local Ollama request cannot be completed."""


def generate_json(
    *,
    model: str,
    system_prompt: str,
    ticket: str,
    base_url: str = "http://localhost:11434",
    timeout: float = 120.0,
) -> tuple[Any, float, str]:
    """Generate one JSON prediction and return value, latency, and raw content."""

    payload = {
        "model": model,
        "stream": False,
        "format": "json",
        "options": {"temperature": 0},
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": ticket},
        ],
    }
    request = Request(
        f"{base_url.rstrip('/')}/api/chat",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    started = time.perf_counter()
    try:
        with urlopen(request, timeout=timeout) as response:
            body = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise OllamaError(f"Ollama returned HTTP {exc.code}: {detail}") from exc
    except URLError as exc:
        raise OllamaError(
            "Could not reach Ollama. Start it locally, then pull the requested model."
        ) from exc

    latency = time.perf_counter() - started
    try:
        content = body["message"]["content"]
    except (KeyError, TypeError) as exc:
        raise OllamaError(f"Unexpected Ollama response: {body!r}") from exc

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        parsed = None

    return parsed, latency, content

