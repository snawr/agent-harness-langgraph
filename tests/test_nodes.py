from pathlib import Path
from unittest.mock import patch

from agent.llm.client import SimpleResponse
from agent.parsers import UnifiedDiff
from agent.patching import apply_unified_diff
from agent.tools import run_command
from agent.nodes.planner import planner_node
from agent.nodes.coder import coder_node
from agent.nodes.patcher import patcher_node
from agent.nodes.executor import executor_node
from agent.nodes.critic import critic_node


def make_state(**overrides):
    state = {
        "task": "Test task",
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
    state.update(overrides)
    return state


def test_planner_returns_plan():
    result = planner_node(make_state(task="Create development plan for snake game in python"))
    print(f"test_planner_returns_plan result: {result}")
    assert "plan" in result
    assert isinstance(result["plan"], list)
    assert result["status"] == "running"
    assert result["current_step"] == 0


def test_coder_returns_cleaned_patch():
    raw_patch = "```diff\ndiff --git a/foo.py b/foo.py\n--- /dev/null\n+++ b/foo.py\n@@ -0,0 +1 @@\n+print(\"hi\")\n```"
    with patch("agent.nodes.coder.llm.invoke", return_value=SimpleResponse(raw_patch)):
        result = coder_node(make_state())

    print(f"test_coder_returns_cleaned_patch result: {result}")
    assert "last_patch" in result
    assert result["last_patch"].startswith("diff --git")
    assert "```" not in result["last_patch"]


def test_coder_returns_patch_error_for_invalid_diff():
    with patch("agent.nodes.coder.llm.invoke", return_value=SimpleResponse("not a diff")):
        result = coder_node(make_state())

    print(f"test_coder_returns_patch_error_for_invalid_diff result: {result}")
    assert "patch_error" in result
    assert result["patch_error"] == "invalid unified-diff format"


def test_patcher_applies_patch_successfully():
    patch_result = {"success": True, "logs": "applied", "changed_files": ["foo.py"]}
    with patch("agent.nodes.patcher.apply_unified_diff", return_value=patch_result):
        result = patcher_node(make_state(last_patch="diff --git a/foo.py b/foo.py\n"))

    print(f"test_patcher_applies_patch_successfully result: {result}")
    assert result["patch_result"] == patch_result


def test_patcher_returns_error_for_empty_patch():
    result = patcher_node(make_state(last_patch=""))

    print(f"test_patcher_returns_error_for_empty_patch result: {result}")
    assert result["patch_result"]["success"] is False
    assert result["patch_result"]["logs"] == "No patch provided."


def test_apply_unified_diff_treats_existing_new_file_as_success(tmp_path):
    target = tmp_path / "tests" / "smoke_test_agent.py"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text('print("hi")\n', encoding="utf-8")

    patch = """diff --git a/tests/smoke_test_agent.py b/tests/smoke_test_agent.py
new file mode 100644
index 0000000..e1f2a3c
--- /dev/null
+++ b/tests/smoke_test_agent.py
@@ -0,0 +1 @@
+print("hi")
"""

    result = apply_unified_diff(tmp_path, patch)

    assert result["success"] is True
    assert "already exist" in result["logs"].lower() or "already applied" in result["logs"].lower()


def test_run_command_uses_active_venv_path():
    repo_root = Path(__file__).resolve().parent.parent
    result = run_command("pytest --version", cwd=repo_root)

    assert result["returncode"] == 0
    assert "pytest" in result["stdout"].lower()


def test_patcher_returns_patch_error_from_state():
    result = patcher_node(make_state(last_patch="diff", patch_error="invalid unified-diff format"))

    print(f"test_patcher_returns_patch_error_from_state result: {result}")  
    assert result["patch_result"]["success"] is False
    assert "Patch validation error" in result["patch_result"]["logs"]


def test_executor_runs_tests_when_patch_ok():
    command_result = {"command": "pytest -q", "returncode": 0, "stdout": "ok", "stderr": "", "timed_out": False}
    print(f"test_executor_runs_tests_when_patch_ok result: {command_result}")
    with patch("agent.nodes.executor.run_command", return_value=command_result):
        result = executor_node(make_state(patch_result={"success": True, "logs": "", "changed_files": []}))

    assert result["last_command"] == command_result
    assert result["last_logs"] == "ok"


def test_executor_skips_when_patch_failed():
    result = executor_node(make_state(patch_result={"success": False, "logs": "bad patch", "changed_files": []}))

    print(f"test_executor_skips_when_patch_failed result: {result}")
    assert result["last_command"] is None
    assert result["last_logs"] == "bad patch"


def test_critic_fails_when_patch_failed_and_max_reached():
    result = critic_node(make_state(patch_result={"success": False, "logs": "bad patch", "changed_files": []}, iteration=0, max_iterations=1))

    print(f"test_critic_fails_when_patch_failed_and_max_reached result: {result}")  
    assert result["status"] == "failed"
    assert result["iteration"] == 1


def test_critic_retries_when_patch_failed_and_iterations_remain():
    result = critic_node(make_state(patch_result={"success": False, "logs": "bad patch", "changed_files": []}, iteration=0, max_iterations=2))

    print(f"test_critic_retries_when_patch_failed_and_iterations_remain result: {result}")
    assert result["status"] == "running"
    assert result["iteration"] == 1
    assert result["current_step"] == 0


def test_critic_succeeds_on_passing_command():
    result = critic_node(make_state(last_command={"returncode": 0}, iteration=0, max_iterations=1))

    print(f"test_critic_succeeds_on_passing_command result: {result}")
    assert result["status"] == "success"
    assert result["iteration"] == 1


def test_critic_retries_on_command_failure():
    result = critic_node(make_state(last_command={"returncode": 1}, iteration=0, max_iterations=2))

    print(f"test_critic_retries_on_command_failure result: {result}")
    assert result["status"] == "running"
    assert result["iteration"] == 1


def test_parse_accepts_fenced_diff():
    text = "```diff\ndiff --git a/foo.py b/foo.py\n--- /dev/null\n+++ b/foo.py\n@@ -0,0 +1 @@\n+print(\"hi\")\n```"
    parsed = UnifiedDiff.parse(text)

    assert parsed is not None
    assert parsed["paths"] == ["foo.py"]


def test_parse_rejects_non_diff_text():
    assert UnifiedDiff.parse("hello world") is None
