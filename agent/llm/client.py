import os
from typing import Any, Dict, List

try:
    from langchain_ollama import ChatOllama  # type: ignore
except Exception:
    ChatOllama = None

import requests
import json
from json.decoder import JSONDecodeError


class SimpleResponse:
    def __init__(self, content: str, raw: Any = None):
        self.content = content
        self.raw = raw


class LLMClient:
    """Configurable LLM client with fallback to Ollama HTTP API.

    Environment variables:
    - OLLAMA_API_URL (default: http://localhost:11434)
    - OLLAMA_MODEL (default: qwen3:14b)
    """

    def __init__(self):
        self.api_url = os.environ.get("OLLAMA_API_URL", "http://localhost:11434")
        self.model = os.environ.get("OLLAMA_MODEL", "qwen3:14b")
        self.temperature = float(os.environ.get("OLLAMA_TEMPERATURE", "0"))

        self._client = None
        if ChatOllama is not None:
            try:
                self._client = ChatOllama(model=self.model, temperature=self.temperature)
            except Exception:
                self._client = None

    def health_check(self) -> bool:
        """Return True if Ollama API is reachable (HTTP) or langchain client initialized."""
        if self._client is not None:
            return True
        try:
            resp = requests.get(f"{self.api_url}/api/status", timeout=3)
            return resp.status_code == 200
        except Exception:
            return False

    def _invoke_http(self, messages: List[Dict[str, str]]) -> SimpleResponse:
        payload = {"model": self.model, "messages": messages}
        try:
            resp = requests.post(f"{self.api_url}/api/chat", json=payload, timeout=60)
            resp.raise_for_status()
            # Try parsing JSON; Ollama may return NDJSON or multiple JSON objects.
            try:
                j = resp.json()
            except JSONDecodeError:
                text = resp.text
                # Try parse per-line JSON (NDJSON / streaming)
                content_parts: list[str] = []
                last_obj = None
                for line in text.splitlines():
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        j = json.loads(line)
                    except Exception:
                        j = None
                    if not isinstance(j, dict):
                        continue
                    last_obj = j
                    # If it's Ollama-like streaming, message may contain incremental 'thinking'
                    msg = j.get("message")
                    if isinstance(msg, dict):
                        part = msg.get("content") or msg.get("text") or ""
                        if part:
                            content_parts.append(part)
                    # If the chunk signals done, return accumulated content
                    if j.get("done") is True:
                        assembled = "".join(content_parts)
                        return SimpleResponse(assembled, raw={"ndjson_raw": resp.text, "last": last_obj})
                # If we collected parts, return them; otherwise return full text
                if content_parts:
                    return SimpleResponse("".join(content_parts), raw={"ndjson_raw": resp.text, "last": last_obj})
                return SimpleResponse(text, raw={"ndjson_raw": resp.text})

            # Ollama returns {choices: [{message: {role, content}}], ...}
            if isinstance(j, dict):
                choices = j.get("choices") or j.get("output")
                if choices and isinstance(choices, list):
                    first = choices[0]
                    # Try different nesting shapes
                    if isinstance(first, dict):
                        msg = first.get("message") or first.get("content") or first.get("text")
                        if isinstance(msg, dict):
                            content = msg.get("content") or msg.get("text") or ""
                        else:
                            content = msg or ""
                        return SimpleResponse(content, raw=j)
            # Fallback to stringified JSON or text
            return SimpleResponse(json.dumps(j), raw=j)
        except Exception as e:
            # Include response text when available for easier debugging
            resp_text = None
            try:
                resp_text = resp.text
            except Exception:
                resp_text = None
            return SimpleResponse("", raw={"error": str(e), "text": resp_text})

    def invoke(self, messages: List[Dict[str, str]]) -> SimpleResponse:
        """Invoke the configured LLM and return a SimpleResponse with `content` string.

        `messages` should be a list of dicts with `role` and `content` keys.
        """
        # Prefer langchain_ollama client if available
        if self._client is not None:
            try:
                result = self._client.invoke(messages)
                # Try common shapes
                if hasattr(result, "content"):
                    return SimpleResponse(result.content, raw=result)
                if isinstance(result, dict):
                    # langchain types sometimes return {'content': '...'}
                    content = result.get("content") or result.get("text") or str(result)
                    return SimpleResponse(content, raw=result)
                # Fallback to str()
                return SimpleResponse(str(result), raw=result)
            except Exception:
                # Fall through to HTTP
                pass

        # HTTP fallback to Ollama
        return self._invoke_http(messages)


__all__ = ["LLMClient", "SimpleResponse"]