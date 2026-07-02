from agent.tools import run_command


def executor_node(state):
    patch_result = state.get("patch_result")
    if patch_result and not patch_result["success"]:
        return {
            "last_logs": patch_result["logs"],
            "last_command": None,
        }

    result = run_command("pytest -q")

    return {
        "last_command": result,
        "last_logs": result["stdout"] + result["stderr"],
    }
