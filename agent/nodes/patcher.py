from agent.patching import apply_unified_diff


def patcher_node(state):
    patch = state.get("last_patch") or ""
    patch_result = apply_unified_diff(".", patch)

    return {
        "patch_result": patch_result,
    }
