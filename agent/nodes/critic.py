from agent.logging import log_state, record_event


def critic_node(state):
    iteration = state["iteration"] + 1
    record_event(state, "critic_input", {"iteration": iteration, "patch_result": state.get("patch_result"), "last_command": state.get("last_command")})
    log_state(state, "critic", "input")

    patch_result = state.get("patch_result")
    if patch_result and not patch_result["success"]:
        if iteration >= state["max_iterations"]:
            result = {
                "iteration": iteration,
                "status": "failed",
            }
            record_event(state, "critic_output", result)
            log_state(state, "critic", "output")
            return result

        result = {
            "iteration": iteration,
            "current_step": 0,
            "status": "running",
        }
        record_event(state, "critic_output", result)
        log_state(state, "critic", "output")
        return result

    command = state.get("last_command")
    success = command is not None and command["returncode"] == 0

    if success:
        result = {
            "iteration": iteration,
            "status": "success"
        }
        record_event(state, "critic_output", result)
        log_state(state, "critic", "output")
        return result

    if iteration >= state["max_iterations"]:
        result = {
            "iteration": iteration,
            "status": "failed"
        }
        record_event(state, "critic_output", result)
        log_state(state, "critic", "output")
        return result

    result = {
        "iteration": iteration,
        "current_step": 0,
        "status": "running"
    }
    record_event(state, "critic_output", result)
    log_state(state, "critic", "output")
    return result
