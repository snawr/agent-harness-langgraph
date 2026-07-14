def main():
    from agent.graph import build_graph
    from agent.logging import configure_logging

    configure_logging("artifacts/agent-loop.log")
    graph = build_graph()
    result = graph.invoke(
        {
            "task": "Ceate simple calculator in python. No GUI. The calculator should support addition, subtraction, multiplication, and division.",
            "plan": [],
            "current_step": 0,
            "files": {"./workspaces/calculator/calculator.py": "main file for calculator app"},
            "last_patch": None,
            "patch_result": None,
            "last_command": None,
            "last_logs": "",
            "iteration": 0,
            "max_iterations": 3,
            "status": "running",
            "trace": [],
        }
    )
    print(f"status={result['status']}")
    if result.get("trace"):
        print("trace:")
        for step in result["trace"]:
            print(f" - {step}")


if __name__ == "__main__":
    main()
