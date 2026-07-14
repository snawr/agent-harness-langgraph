"""Prompt templates for agent nodes.

Keep templates small and editable. Start with Python constants for simplicity.
"""

PLANNER_SYSTEM = (
    "You are an assistant that produces a short, actionable plan for implementing a requested coding task. "
)

PLANNER_USER_TEMPLATE = (
    "TASK:\n{task}\n\nREPO_CONTEXT:\n{repo_context}\n\n"
    "Return a JSON array of short step descriptions for implementing the task."
)

CODER_SYSTEM = (
    "You are a coding assistant. You MUST output ONLY a single valid unified diff patch. "
    "Do not include any explanations, markdown, or extra text."
)

CODER_USER_TEMPLATE = (
    "TASK:\n{task}\n\nSTEP:\n{step}\n\nREPO_CONTEXT:\n{repo_context}\n\n"
    "Return a unified diff patch that implements the step."
)

__all__ = ["PLANNER_SYSTEM", "CODER_SYSTEM", "CODER_USER_TEMPLATE"]
