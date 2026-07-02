def critic_node(state):
    iteration = state["iteration"] + 1

    patch_result = state.get("patch_result")
    if patch_result and not patch_result["success"]:
        if iteration >= state["max_iterations"]:
            return {
                "iteration": iteration,
                "status": "failed",
            }

        return {
            "iteration": iteration,
            "current_step": 0,
            "status": "running",
        }

    command = state.get("last_command")
    success = command is not None and command["returncode"] == 0

    if success:
        return {
            "iteration": iteration,
            "status": "success"
        }

    if iteration >= state["max_iterations"]:
        return {
            "iteration": iteration,
            "status": "failed"
        }

    return {
        "iteration": iteration,
        "current_step": 0
    }
