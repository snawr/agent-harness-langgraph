# nodes/executor.py

from tools import run_command

def executor_node(state):
    logs = run_command("pytest -q")

    return {
        "last_logs": logs
    }