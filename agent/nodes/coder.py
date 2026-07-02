# nodes/coder.py

def coder_node(state):
    task = state["task"]
    step = state["current_step"]

    # placeholder diff (tu będzie Qwen)
    patch = f"""
--- a/example.py
+++ b/example.py
@@
+ # TODO generated for: {task}, step {step}
"""

    return {
        "last_patch": patch
    }