# nodes/planner.py

def planner_node(state):
    task = state["task"]

    # placeholder (później Qwen)
    plan = [
        f"Analyze task: {task}",
        "Identify required files",
        "Implement changes",
        "Run tests",
        "Fix issues if needed"
    ]

    return {
        "plan": plan,
        "current_step": 0,
        "iteration": 0,
        "status": "running"
    }