# nodes/planner.py

from agent.logging import log_state, record_event


def planner_node(state):
    task = state["task"]
    record_event(state, "planner_input", {"task": task})
    log_state(state, "planner", "input")

    plan = [
        f"Analyze task: {task}",
        "Identify required files",
        "Implement changes",
        "Run tests",
        "Fix issues if needed"
    ]

    result = {
        "plan": plan,
        "current_step": 0,
        "iteration": 0,
        "status": "running",
    }
    record_event(state, "planner_output", result)
    log_state(state, "planner", "output")
    return result