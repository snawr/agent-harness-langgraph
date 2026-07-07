# Agent Harness LangGraph

This project is a small LangGraph-based agent harness that runs a planner -> coder -> patcher -> executor -> critic loop against a local LLM setup.

## Project layout
- agent/ — core graph, state, logging, and node implementations
- agent/nodes/ — individual loop nodes
- agent/config/ — prompt templates and configuration
- tests/ — regression and smoke tests
- artifacts/ — generated runtime traces and logs
- notes/ — working notes and task tracking

## Main entrypoint
Run the harness with:

```bash
PYTHONPATH=. .venv/bin/python main.py
```

Run the test suite with:

```bash
PYTHONPATH=. .venv/bin/python -m pytest -q
```

## Reference docs
- project_decisions.md — important architecture and product decisions
- PLAN.md — current implementation plan and milestones
