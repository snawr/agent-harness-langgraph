# tools.py
import os
import subprocess


def read_file(path: str) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def write_file(path: str, content: str):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def run_command(cmd: str) -> str:
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.stdout + "\n" + result.stderr
    except Exception as e:
        return str(e)


def list_files(root=".") -> list[str]:
    out = []
    for r, _, files in os.walk(root):
        for f in files:
            out.append(os.path.join(r, f))
    return out