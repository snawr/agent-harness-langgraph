# Project Summary and Development Guide

> Living document. Update this file whenever a larger architectural, workflow, state-schema, or product-scope change is merged.

Last reviewed: 2026-07-15

## Purpose

This project is a small local coding-agent harness built with LangGraph and Ollama. It accepts a coding task, asks a local model to plan and generate a unified diff, applies that diff to a repository, runs verification, and either succeeds, retries, or stops at an iteration limit.

The current goal is a reliable single-agent development loop, not a general autonomous software engineer. The intended near-term workflow is:

```text
task -> planner -> coder -> patcher -> executor -> critic
                    ^                              |
                    +------------- retry ----------+
```

## Current Architecture

| Area | Location | Responsibility |
| --- | --- | --- |
| Entrypoint | `main.py` | Builds initial state and invokes the graph |
| Graph | `agent/graph.py` | Defines nodes, edges, retry routing, and tracing wrappers |
| State | `agent/state.py` | Defines the data contract shared by all nodes |
| Planner | `agent/nodes/planner.py` | Produces a JSON list of implementation steps |
| Coder | `agent/nodes/coder.py` | Produces one unified diff for the selected step |
| Patcher | `agent/nodes/patcher.py` | Validates and applies the generated patch |
| Executor | `agent/nodes/executor.py` | Runs verification commands and records their output |
| Critic | `agent/nodes/critic.py` | Selects success, failure, or retry using deterministic rules |
| LLM client | `agent/llm/client.py` | Connects through ChatOllama with an HTTP fallback |
| Prompts | `agent/config/prompts.py` | Holds planner and coder prompt templates |
| Patch support | `agent/parsers.py`, `agent/patching.py` | Parses diffs, checks paths, and calls `git apply` |
| OS support | `agent/tools.py` | Reads files and runs processes or shell commands |
| Observability | `agent/logging.py` | Emits state snapshots and trace events |
| Tests | `tests/` | Node, parser, patching, and smoke-test coverage |

The separation of graph, state, nodes, model integration, and tools is a good foundation. It is easy to locate responsibilities and small enough to change safely. A `src/` migration or deeper package hierarchy would add churn without solving the current reliability problems, so restructuring the package should not be the first priority.

## Current State

The main loop and its supporting components exist, but this is still a prototype rather than a dependable coding harness.

What already works:

- Explicit LangGraph workflow with a bounded retry loop.
- Local Ollama configuration through environment variables.
- Planner and coder prompts isolated from node logic.
- Basic model-output and unified-diff validation.
- Patch path containment checks and `git apply --check`.
- Some idempotency handling for repeated new-file patches.
- Structured command results, state snapshots, and trace events.
- Focused regression tests for several node decisions and patch cases.

Important gaps:

- Only `plan[0]` is used; `current_step` is never advanced.
- Retry attempts do not give the coder the previous patch error or execution logs explicitly.
- The repository context is a manually supplied dictionary and is not refreshed after changes.
- The patcher operates relative to the harness repository, while the executor currently verifies `./workspaces`; workspace ownership is unclear.
- Verification is hard-coded and mostly checks syntax rather than task completion.
- `patch_error` is passed between nodes but is absent from `AgentState`.
- Planner JSON parsing and LLM failures do not have a structured recovery path.
- A new-file conflict may be reported as a successful skip even when contents differ.
- `run_command` uses `shell=True`; model-proposed commands would need an allowlist or a non-shell execution contract.
- Some smoke tests refer to files that do not exist and do not represent the current application.
- The entrypoint contains a hard-coded task and file context instead of a usable CLI or API.

## What to Handle First

### Priority 0: Establish a trustworthy baseline

Do this before adding more agent behavior.

1. Make the full test suite deterministic and green without a running LLM. Mock the planner LLM in unit tests and keep live-model checks in an explicitly marked integration suite.
2. Remove or rewrite stale smoke tests so every collected test represents supported behavior.
3. Stop tracking generated files such as `__pycache__`, `.pyc`, logs, artifacts, and disposable workspaces. Keep only deliberate fixtures.
4. Add CI for formatting/linting and tests, using one documented Python version and one reproducible dependency workflow.
5. Add a root `AGENTS.md` with canonical setup, test, lint, architectural-boundary, and safety instructions for Codex and other coding agents.

Exit condition: a fresh checkout has one documented setup path and one command that reliably validates the repository.

### Priority 1: Define workspace and safety boundaries

This is the most important product-level issue. The harness must never confuse its own source repository with the repository being modified.

1. Add an explicit `workspace_root` to configuration and `AgentState`.
2. Resolve all reads, patch application, and verification relative to that root.
3. Reject absolute paths, traversal, symlink escapes, and changes to protected paths.
4. Replace shell command strings with argument lists where possible. Define which commands can be selected by the agent and which remain developer-configured.
5. Decide how a run handles an already-dirty workspace and document rollback/cleanup behavior. Do not make automatic destructive Git operations the default.

Exit condition: an integration test proves that the agent can modify a temporary fixture repository but cannot write outside it.

### Priority 2: Make state and transitions correct

1. Make `AgentState` match every field actually exchanged, including structured errors.
2. Define node input/output contracts and status values with enums or literals instead of unrestricted strings.
3. Separate `plan_step` progression from retry count. Advance after a verified step and finish only after all steps pass.
4. Clear stale data such as `patch_error`, `last_command`, and `patch_result` at defined transition points.
5. Add graph-level tests for successful execution, patch failure, command failure, retry exhaustion, and multi-step completion.

Exit condition: graph behavior is deterministic under mocked node results and a two-step plan completes in the expected order.

### Priority 3: Build real repository context and feedback

1. Introduce a repository-context service that lists relevant files, reads selected content, respects ignore rules, and enforces size limits.
2. Refresh context after applying a patch.
3. Include the last patch result, verification logs, iteration number, and prior attempted patch in retry prompts.
4. Use structured model output for the plan and validate it with a schema. Return recoverable node errors rather than allowing parsing exceptions to terminate the graph.
5. Record prompt/model metadata without leaking secrets or producing unbounded logs.

Exit condition: the second coder attempt can explain and correct a failure using information from the first attempt.

### Priority 4: Make verification prove the task

1. Represent verification as a list of structured steps: name, argument list, timeout, working directory, and whether failure is required or advisory.
2. Detect project-provided checks conservatively, with explicit configuration taking precedence.
3. Support syntax/build checks, tests, and task-specific smoke checks.
4. Store all command results instead of only `last_command`.
5. Make success require all mandatory checks and all plan steps, not merely one successful `compileall` invocation.

Exit condition: deliberately incorrect behavior can compile successfully but is still rejected by a behavioral test.

### Priority 5: Improve the developer interface and observability

1. Replace the hard-coded `main.py` example with a CLI accepting task, workspace, model, iteration limit, and verification configuration.
2. Assign each run an ID and write bounded structured events to an ignored artifact directory.
3. Print a concise final summary: status, changed files, checks, retries, and failure reason.
4. Add typed configuration rather than reading environment variables throughout the application.
5. Once behavior stabilizes, split fast unit tests from fixture-repository integration tests and optional Ollama end-to-end tests.

## Recommended Near-Term Milestones

### Milestone 1: Development baseline

- Clean tracked generated files.
- Repair the test suite and mark live-LLM tests.
- Add `AGENTS.md`, CI, formatter/linter configuration, and canonical commands.

### Milestone 2: Safe workspace runner

- Introduce typed run configuration and `workspace_root`.
- Route patching, context collection, and execution through the workspace abstraction.
- Add containment and temporary-repository integration tests.

### Milestone 3: Correct feedback loop

- Correct the state schema and stale-state handling.
- Feed failures into retries.
- Implement plan-step progression and graph-level tests.

### Milestone 4: Verification engine

- Support multiple structured validation steps.
- Run repository tests and task-specific checks.
- Base final success on required validations.

## Suitability for Coding Agents

The project is understandable to a coding agent, but it is only partially prepared for sustained agent-assisted development.

Good properties:

- Small modules with mostly single responsibilities.
- Central graph and state definitions.
- Prompts separated from orchestration code.
- Existing tests and architectural decision notes.
- A narrow product scope.

Missing properties that matter to Codex-like agents:

- A root `AGENTS.md` containing exact setup and validation commands.
- A deterministic test suite that does not silently depend on Ollama.
- Clear separation between unit, integration, and live-model tests.
- One authoritative roadmap; `PLAN.md`, `notes/todo.md`, and other notes currently overlap and may drift.
- Explicit workspace/safety invariants near the code that enforces them.
- Automated formatting, linting, type checking, and CI feedback.
- Small fixture repositories for testing full runs safely.
- Stable public contracts for state, node outputs, and configuration.

After Priorities 0 through 2, the repository will be substantially safer and easier for a coding agent to change autonomously. Until then, an agent should inspect workspace boundaries and run focused tests after every orchestration change.

## Structure Recommendation

Keep the current top-level package for now, with a few focused additions:

```text
agent/
  config/             typed run configuration and prompts
  llm/                provider client and response schemas
  nodes/              graph node implementations
  context.py          repository discovery and bounded context building
  workspace.py        path containment and workspace operations
  verification.py     structured validation engine
  graph.py
  state.py
tests/
  unit/
  integration/
  fixtures/
  live/               optional Ollama tests
scripts/
AGENTS.md
PROJECT_SUMMARY.md
README.md
```

Do not create every module preemptively. Add each boundary when implementing its corresponding milestone. The key structural change is a first-class workspace abstraction, not a broad file rearrangement.

## Development Conventions to Add

Suggested canonical commands, once configured:

```bash
uv sync
uv run pytest -q
uv run ruff check .
uv run ruff format --check .
uv run mypy agent
```

Use the dependency manager already represented by `uv.lock`, and decide whether `uv.lock` is committed. For an application-style harness, committing it is generally useful for reproducibility.

Tests should use these categories:

- Unit: no filesystem mutation outside `tmp_path`, no network, no Ollama.
- Integration: temporary fixture Git repositories, real patching and subprocesses, no Ollama.
- Live: explicit opt-in, requires Ollama and a configured model.

## Major Decisions Still Needed

Record resolutions in `project_decisions.md`:

1. Is each task executed against an external repository, a copied sandbox, or a Git worktree?
2. Who chooses verification commands: configuration, planner, repository detection, or a controlled combination?
3. Does the planner produce implementation steps only, or steps plus acceptance checks?
4. Can the agent modify tests, configuration, and dependency files by default?
5. What constitutes success when the target repository has no tests?
6. What data may be written to logs, and how long should artifacts be retained?

## Definition of a Reliable MVP

The harness is ready to call a reliable MVP when it can:

- Accept a task and explicit workspace from a CLI.
- Build bounded, relevant repository context.
- Apply changes only inside that workspace.
- Recover from malformed model output and failed patches.
- Feed concrete failure evidence into retries.
- Complete and verify every plan step.
- Run configured behavioral checks, not only syntax compilation.
- Produce a clear final report and bounded trace.
- Pass deterministic unit and integration tests on a fresh checkout.

## Updating This Document

Update this file in the same change whenever any of the following happens:

- A graph node, edge, retry rule, or terminal condition changes.
- The shared state or node output contract changes.
- Workspace, command-execution, or patch safety rules change.
- The LLM provider or structured-output contract changes.
- A milestone is completed or reprioritized.
- The supported setup, test, lint, or run commands change.
- Project scope changes materially.

When updating it:

1. Change `Last reviewed`.
2. Update both the current-state description and priorities.
3. Move durable architectural choices into `project_decisions.md`.
4. Keep `README.md` focused on setup and usage; keep this file focused on architecture, readiness, and direction.
5. Remove completed warnings instead of leaving the document as a historical changelog; Git already preserves history.
