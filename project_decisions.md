# Project Decisions

This file records the important product and engineering decisions that shaped the agent harness so they can be referenced later.

## 1. Core architecture
- The project is built around a LangGraph state graph with five nodes: planner, coder, patcher, executor, and critic.
- The loop is intentionally simple and explicit: each node performs one responsibility and passes state forward.
- The shared state is centralized in the agent state schema so the graph can evolve without ad-hoc data handling.

## 2. LLM integration
- The harness uses a local LLM setup via Ollama and a configurable client layer.
- Prompt templates and system prompts are kept in the config package rather than embedded in node logic.
- The coder node is responsible for requesting code changes, while the patcher node handles applying them.

## 3. Resilience around patching
- A repeated patch that tries to create a file that already exists with matching content is treated as a successful no-op rather than a hard failure.
- This was chosen to make the loop robust and prevent the graph from dying on a common idempotency case.
- Patch results are preserved in state so later steps can inspect what happened.

## 4. Verification flow
- The executor runs verification commands and captures their output, exit code, and logs.
- The critic decides whether the loop should continue or stop based on the latest verification result and the current iteration.
- The loop is capped by a maximum iteration count to avoid endless retries.

## 5. Observability and debugging
- The project uses structured tracing to log node entry/exit, input/output state snapshots, and execution details.
- Traces are written to both the console and the log file at artifacts/agent-loop.log.
- The logging format is intentionally readable so prompts, patch results, and state transitions are easy to inspect.

## 6. Environment and tooling
- The project uses a local virtual environment and the repository Python interpreter for running tests and harness commands.
- pytest is the primary verification tool for regression and smoke tests.
- The repository keeps runtime artifacts separate from source code under artifacts/.

## 7. Project maintenance direction
- The current focus is on a working loop first, not on building a highly complex autonomous agent.
- Documentation and traceability are treated as important because the project is still evolving and needs to be easy to debug.
