import json
import logging
import os
from pathlib import Path
from typing import Any

LOGGER_NAME = "agent_harness"


def configure_logging(log_file: str | None = None) -> logging.Logger:
    level_name = os.getenv("AGENT_LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(level)
    logger.propagate = False

    if logger.handlers:
        return logger

    formatter = logging.Formatter("%(levelname)s %(name)s: %(message)s")

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        if log_path.exists():
            log_path.unlink()
        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def _format_value(value: Any) -> str:
    if isinstance(value, (dict, list)):
        try:
            return json.dumps(value, indent=2, default=str)
        except Exception:
            return str(value)
    return str(value)


def _emit_section(logger: logging.Logger, title: str, content: Any) -> None:
    text = _format_value(content)
    logger.info("%s\n%s", title, text)


def write_run_header(logger: logging.Logger, label: str) -> None:
    logger.info("\n===== %s =====", label)


def append_trace(state: dict[str, Any], message: str) -> None:
    trace = state.setdefault("trace", [])
    if not isinstance(trace, list):
        trace = []
        state["trace"] = trace
    trace.append(message)


def record_event(state: dict[str, Any], event: str, payload: Any = None) -> None:
    append_trace(state, f"{event}={payload if payload is not None else ''}")


def snapshot_state(state: dict[str, Any]) -> dict[str, Any]:
    return {
        "task": state.get("task"),
        "status": state.get("status"),
        "iteration": state.get("iteration"),
        "current_step": state.get("current_step"),
        "plan": state.get("plan"),
        "last_patch": state.get("last_patch"),
        "patch_result": state.get("patch_result"),
        "last_command": state.get("last_command"),
        "last_logs": state.get("last_logs"),
    }


def log_state(state: dict[str, Any], node_name: str, detail: str | None = None) -> None:
    logger = configure_logging(os.getenv("AGENT_LOG_FILE", "artifacts/agent-loop.log"))
    snapshot = snapshot_state(state)
    prefix = f"node={node_name}"
    if detail:
        prefix = f"{prefix} {detail}"
    logger.info("[%s]", prefix)
    _emit_section(logger, "state:", snapshot)


logger = logging.getLogger(LOGGER_NAME)
