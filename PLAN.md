# PLAN: Integrate local Qwen3:14B and make repo runnable

TL;DR - Integrate a local Qwen3:14B LLM (Ollama) and make the project runnable end-to-end by making the LLM client configurable, adding a smoke-test, and iterating until the harness runs and tests pass.

## Steps

1. Make `agent/llm/client.py` configurable via env vars: `OLLAMA_API_URL` (default `http://localhost:11434`) and `OLLAMA_MODEL` (default `qwen3:14b`). Add health-check and error handling.
2. Normalize `LLMClient.invoke(messages)` so it returns an object with `content` (string). Adapt to `langchain_ollama` response shape and provide an HTTP fallback to Ollama API.
3. Add a smoke-test script `scripts/smoke_llm.py` that sends a short prompt and prints the response.
4. Install dependencies and run the harness: `python main.py`; iterate on runtime fixes.
5. Run `pytest -q` via the executor node and fix any issues.
6. Optional: add HTTP adapter fallback improvements, streaming, and performance tuning.

## Verification

- Environment: `python --version` >= 3.13 and `pip install` dependencies from `pyproject.toml`.
- LLM reachability: confirm Ollama reachable at `http://localhost:11434`.
- Run smoke-test: `python scripts/smoke_llm.py` — expect plain text output.
- Run harness: `python main.py` and inspect printed status and logs.
- Run `pytest -q` to validate executor behavior.

## Notes

- The repository currently uses `langchain_ollama` but the client now falls back to HTTP if `langchain_ollama` is not available or initialization fails.
- If Ollama uses a different API path or authentication, update `OLLAMA_API_URL` accordingly.
