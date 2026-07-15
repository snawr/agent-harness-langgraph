from pathlib import Path


def test_agent_graph_builds_without_invoking_an_llm():
    """The graph can be constructed without requiring a live model service."""
    from agent.graph import build_graph

    assert build_graph() is not None


def test_required_source_files_exist():
    root = Path(__file__).resolve().parents[1]
    required_files = [
        "main.py",
        "agent/graph.py",
        "agent/state.py",
        "agent/config/prompts.py",
    ]

    assert all((root / path).is_file() for path in required_files)
