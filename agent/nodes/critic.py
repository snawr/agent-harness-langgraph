# nodes/critic.py

def critic_node(state):
    logs = state["last_logs"]

    iteration = state["iteration"] + 1

    # bardzo prosta heurystyka (na start)
    success = "FAILED" not in logs and "ERROR" not in logs

    if success:
        return {
            "status": "success"
        }

    if iteration >= state["max_iterations"]:
        return {
            "status": "failed"
        }

    return {
        "iteration": iteration,
        "current_step": 0
    }