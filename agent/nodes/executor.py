from agent.logging import log_state, record_event
from agent.tools import run_command


def executor_node(state):
    patch_result = state.get("patch_result")
    # record_event(state, "executor_input", {"patch_result": patch_result})
    log_state(state, "executor", "input")

    if patch_result and not patch_result["success"]:
        result = {
            "last_logs": patch_result["logs"],
            "last_command": None,
        }
        record_event(state, "executor_output", result)
        log_state(state, "executor", "output")
        return result

    # result = run_command("pytest -q")
    result = run_command(cmd="echo pwd", cwd="./workspaces")
    output = {
        "last_command": result,
        "last_logs": result["stdout"] + result["stderr"],
    }
    # record_event(state, "executor_output", output)
    log_state(state, "executor", "output")
    return output
