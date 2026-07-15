"""Prompt templates for agent nodes.

Keep templates small and editable.
"""

PLANNER_SYSTEM = (
    "You are an assistant that produces a short, actionable plan for implementing a requested coding task. "
)

PLANNER_USER_TEMPLATE = (
    "TASK:\n{task}\n\nREPO_CONTEXT:\n{repo_context}\n\n"
    "Return a JSON array of short step descriptions for implementing the task."
    "Each step should be verifiable and actionable."
    "Do not include any explanations, markdown, or extra text."
)



CODER_SYSTEM = (
    "You are a coding assistant. You MUST output ONLY a single valid unified diff patch for current step."
    "Each patch should be verifable, testable and implement a single step of the plan. "
    "Do not include any explanations, markdown, or extra text."
)

CODER_USER_TEMPLATE = (
    "TASK:\n{task}\n\nPLAN:\n{plan}\n\nCURRENT_STEP:\n{step}\n\nREPO_CONTEXT:\n{repo_context}\n\n"
    "Return a unified diff patch that implements the step."
)

__all__ = ["PLANNER_SYSTEM", "PLANNER_USER_TEMPLATE", "CODER_SYSTEM", "CODER_USER_TEMPLATE"]
