from agent.patching import apply_unified_diff


def patcher_node(state):
    patch = state.get("last_patch") or ""

    # If a previous node already flagged a parse/format error, surface it
    patch_error = state.get("patch_error")
    if patch_error:
        return {"patch_result": {"success": False, "logs": f"Patch validation error: {patch_error}", "changed_files": []}}

    if not patch.strip():
        return {"patch_result": {"success": False, "logs": "No patch provided.", "changed_files": []}}

    patch_result = apply_unified_diff(".", patch)

    return {"patch_result": patch_result}
