import os
import subprocess
from pathlib import Path

from agent.state import CommandResult


def read_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_file(path: str, content: str):
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def run_command(
    cmd: str,
    cwd: str | Path = ".",
    timeout: int = 60,
    input_text: str | None = None,
) -> CommandResult:
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd,
            input=input_text,
        )
        return {
            "command": cmd,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "timed_out": False,
        }
    except subprocess.TimeoutExpired as e:
        return {
            "command": cmd,
            "returncode": 124,
            "stdout": e.stdout or "",
            "stderr": e.stderr or f"Command timed out after {timeout} seconds.",
            "timed_out": True,
        }
    except Exception as e:
        return {
            "command": cmd,
            "returncode": 1,
            "stdout": "",
            "stderr": str(e),
            "timed_out": False,
        }


def run_process(
    args: list[str],
    cwd: str | Path = ".",
    timeout: int = 60,
    input_text: str | None = None,
) -> CommandResult:
    try:
        result = subprocess.run(
            args,
            shell=False,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd,
            input=input_text,
        )
        return {
            "command": " ".join(args),
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "timed_out": False,
        }
    except subprocess.TimeoutExpired as e:
        return {
            "command": " ".join(args),
            "returncode": 124,
            "stdout": e.stdout or "",
            "stderr": e.stderr or f"Command timed out after {timeout} seconds.",
            "timed_out": True,
        }
    except Exception as e:
        return {
            "command": " ".join(args),
            "returncode": 1,
            "stdout": "",
            "stderr": str(e),
            "timed_out": False,
        }


def list_files(root=".") -> list[str]:
    out = []
    for r, _, files in os.walk(root):
        for f in files:
            out.append(os.path.join(r, f))
    return out
