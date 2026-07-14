import os
import shlex
import subprocess
import sys
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


def _resolve_python_executable(cwd: str | Path) -> str:
    repo_root = Path(cwd).resolve()
    venv_python = repo_root / ".venv" / "bin" / "python"
    if venv_python.exists():
        return str(venv_python)
    return sys.executable


def run_command(
    cmd: str,
    cwd: str | Path = ".",
    timeout: int = 60,
    input_text: str | None = None,
) -> CommandResult:
    env = os.environ.copy()
    repo_root = Path(cwd).resolve()


    python_executable = _resolve_python_executable(repo_root)
    venv_bin = repo_root / ".venv" / "bin"
    if venv_bin.exists():
        env["VIRTUAL_ENV"] = str(repo_root / ".venv")
        env["PATH"] = f"{venv_bin}:{env.get('PATH', '')}"

    try:
        parsed = shlex.split(cmd, posix=True)
        if parsed and parsed[0] == "pytest":
            command = " ".join(
                [shlex.quote(python_executable), "-m", "pytest", *[shlex.quote(part) for part in parsed[1:]]]
            )
        else:
            command = cmd

        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=cwd,
            input=input_text,
            env=env,
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
