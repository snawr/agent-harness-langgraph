# state.py
from typing import TypedDict, List, Dict, Any, Optional


class AgentState(TypedDict):
    task: str

    plan: List[str]
    current_step: int

    files: Dict[str, str]  # snapshot repo (path -> content)

    last_patch: Optional[str]
    last_logs: str

    iteration: int
    max_iterations: int

    status: str  # "running" | "success" | "failed"