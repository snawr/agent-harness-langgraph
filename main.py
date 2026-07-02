def main():
    from agent.graph import build_graph

    graph = build_graph()
    result = graph.invoke(
        {
            "task": "Smoke test agent harness",
            "plan": [],
            "current_step": 0,
            "files": {},
            "last_patch": None,
            "patch_result": None,
            "last_command": None,
            "last_logs": "",
            "iteration": 0,
            "max_iterations": 1,
            "status": "running",
        }
    )
    print(result["status"])


if __name__ == "__main__":
    main()
