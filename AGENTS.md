# Working in Agent Harness LangGraph

## Purpose

This repository builds a local LangGraph coding-agent harness. The near-term goal is a safe, deterministic single-agent loop:

```text
task -> planner -> coder -> patcher -> executor -> critic
```

Read `PROJECT_SUMMARY.md` for architecture, current limitations, roadmap, and the definition of a reliable MVP. Read `project_decisions.md` before changing a durable architectural decision.

## Repository Map

- `agent/graph.py`: graph topology and routing.
- `agent/state.py`: shared state contract; update it whenever nodes exchange a new field.
- `agent/nodes/`: planner, coder, patcher, executor, and critic implementations.
- `agent/config/prompts.py`: LLM prompt templates.
- `agent/llm/`: Ollama integration.
- `agent/parsers.py`, `agent/patching.py`: patch parsing, validation, and application.
- `agent/tools.py`: filesystem and subprocess helpers.
- `tests/`: regression and smoke tests.
- `notes/`: exploratory notes; do not treat them as the authoritative contract.

## Setup and Commands

Use the repository virtual environment when it exists:

```bash
PYTHONPATH=. .venv/bin/python -m pytest -q
PYTHONPATH=. .venv/bin/python main.py
PYTHONPATH=. .venv/bin/python scripts/smoke_llm.py
```

The LLM smoke script is optional and requires a reachable local Ollama server. Configure it with `OLLAMA_API_URL`, `OLLAMA_MODEL`, and optionally `OLLAMA_TEMPERATURE`.

Run focused tests for the code you change first, then run the full suite when practical. Do not require Ollama or network access for ordinary unit tests.

## Change Rules

1. Keep node responsibilities narrow. Put workflow routing in `graph.py`, shared fields in `state.py`, prompts in `agent/config/`, and OS/process behavior in tools or dedicated support modules.
2. Treat `AgentState` as a public contract. If a node reads or writes a field, declare it, document its meaning, and add or adjust tests.
3. Preserve a bounded retry loop. New retry paths must have explicit terminal conditions.
4. Prefer structured data over parsing prose: typed state, validated JSON/schema output, argument lists for commands, and structured command results.
5. Add or update a regression test for behavior changes, particularly graph routing, patch handling, state transitions, and command execution.
6. Keep production code and test fixtures separate. Do not add generated artifacts, cache files, logs, virtual environments, or disposable workspaces to version control.
7. Keep documentation current. Update `PROJECT_SUMMARY.md` for material architecture, roadmap, safety, or workflow changes; record lasting choices in `project_decisions.md`.

## Workspace and Safety Boundaries

The harness is intended to modify a target workspace, not its own source repository. Until workspace handling is fully centralized, inspect every path and working directory carefully.

- Never broaden a patch, file operation, or command beyond the configured workspace without explicit user approval.
- Reject absolute paths, `..` traversal, and symlink escapes in agent-controlled paths.
- Do not use destructive Git operations such as `git reset --hard`, `git clean`, or forced checkout unless the user explicitly requests them.
- Prefer `subprocess` argument lists with `shell=False`. Do not pass model-generated command text to a shell without a deliberate, tested allowlist and documented justification.
- Do not treat a skipped conflicting patch as success unless the target content has been verified to match the requested patch.

## Testing Expectations

Keep three levels distinct:

- Unit tests: mocked LLMs, no network, no real Ollama, and isolated filesystem access through `tmp_path`.
- Integration tests: temporary fixture Git repositories; exercise patching, paths, and subprocess behavior without a live LLM.
- Live tests: opt-in only; require Ollama and should not run in the default test command.

For a graph change, cover at least the successful path and the relevant failure/retry path. For patching or workspace changes, add a test proving writes cannot escape the target repository.

## Completion Checklist

Before handing off a change:

1. Inspect the diff for unrelated modifications.
2. Run the focused relevant test(s).
3. Run the full deterministic test suite when feasible.
4. State any tests not run and why.
5. Summarize changed behavior, safety implications, and documentation updates.

## What Not to Do Yet

- Do not add multi-agent orchestration, long-term memory, web/RAG, or broad autonomous planning unless the project scope explicitly changes.
- Do not reorganize into a deeper package layout merely for aesthetics.
- Do not make a compilation-only check the sole definition of task success.
