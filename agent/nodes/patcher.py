from agent.logging import log_state, record_event
from agent.patching import apply_unified_diff


def patcher_node(state):
    patch = state.get("last_patch") or ""
    record_event(state, "patcher_input", {"patch": patch})
    log_state(state, "patcher", "input")

    patch_error = state.get("patch_error")
    if patch_error:
        result = {"patch_result": {"success": False, "logs": f"Patch validation error: {patch_error}", "changed_files": []}}
        record_event(state, "patcher_output", result)
        log_state(state, "patcher", "output")
        return result

    if not patch.strip():
        result = {"patch_result": {"success": False, "logs": "No patch provided.", "changed_files": []}}
        record_event(state, "patcher_output", result)
        log_state(state, "patcher", "output")
        return result

    patch_result = apply_unified_diff(".", patch)
    result = {"patch_result": patch_result}
    record_event(state, "patcher_output", result)
    log_state(state, "patcher", "output")
    return result
