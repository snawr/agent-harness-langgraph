# PLAN: Integrate local Qwen3:14B and make repo runnable

TL;DR - Integrate a local Qwen3:14B LLM (Ollama) and make the project runnable end-to-end by making the LLM client configurable, adding a smoke-test, and iterating until the harness runs and tests pass.

## Current status

- `agent/llm/client.py` is now configurable via `OLLAMA_API_URL` and `OLLAMA_MODEL`, and supports both `langchain_ollama` and HTTP fallback.
- `scripts/smoke_llm.py` has been added and verified to talk successfully to the local Ollama Qwen model.
- `main.py` and the graph currently execute, but the harness still ends with `failed` because the patcher receives a patch that includes files already present in the repository.
- `agent/patching.py` was updated to attempt more robust patch recovery, but the failure remains in patch application for a patch that creates existing files.

## Remaining blockers

1. `agent/nodes/coder.py` currently generates a patch that creates `tests/smoke/harness.py` and `tests/smoke/test_agent.py`.
2. `agent/patching.py` must be made idempotent for existing new-file patches, or the harness should avoid reusing already-applied patches.
3. `main.py` currently returns `failed` because the graph ends after the first iteration due to patch failure.

## Next steps

1. Fix patcher idempotency:
   - Detect when a patch's new-file contents already exist unchanged in the repo.
   - Treat that condition as success rather than failure.
2. Add minimal logging or state output from the graph so failures are easier to debug in future runs.
3. Run `main.py` again and confirm the graph advances beyond patching.
4. Once the agent loop works, document setup and run instructions in `README.md`.
5. Optionally, add a test harness for `agent/patching.py` and `agent/llm/client.py`.

## Verification

- Environment: `python --version` >= 3.13 via `.venv/bin/python`.
- LLM reachability: Ollama at `http://localhost:11434`.
- Smoke test: `PYTHONPATH=. python3 scripts/smoke_llm.py` should print a text response.
- Harness: `PYTHONPATH=. .venv/bin/python main.py` should run without ending in `failed`.
- Tests: `PYTHONPATH=. .venv/bin/python -m pytest -q` once harnessing works.

## Notes

- `agent/llm/client.py` now handles Ollama streaming-like NDJSON output and builds a single response string.
- `agent/nodes/coder.py` currently assumes the model returns a unified diff patch in plain text.
- If Ollama returns a different shape in future, update `agent/llm/client.py` response parsing accordingly.
