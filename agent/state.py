from typing import TypedDict, List, Dict, Any, Optional


class CommandResult(TypedDict):
    command: str
    returncode: int
    stdout: str
    stderr: str
    timed_out: bool


class PatchResult(TypedDict):
    success: bool
    logs: str
    changed_files: List[str]


class AgentState(TypedDict):
    task: str

    plan: List[str]
    current_step: int

    files: Dict[str, str]  # snapshot repo (path -> content)

    last_patch: Optional[str]
    patch_result: Optional[PatchResult]
    last_command: Optional[CommandResult]
    last_logs: str

    iteration: int
    max_iterations: int

    status: str  # "running" | "success" | "failed"
    trace: List[str]
