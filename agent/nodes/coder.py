# nodes/coder.py
from agent.llm.client import LLMClient
from agent.parsers import UnifiedDiff
from agent.config.prompts import CODER_SYSTEM, CODER_USER_TEMPLATE
from agent.logging import log_state, record_event

llm = LLMClient()


def coder_node(state):
    task = state["task"]
    step = state["current_step"]
    # repo_context = state.get("repo_context", "")
    repo_context = state.get("files", "")

    user_prompt = CODER_USER_TEMPLATE.format(task=task, step=step, repo_context=repo_context)
    print(f"Coder node user prompt:\n{user_prompt}\n{'-'*40}")
    messages = [
        {"role": "system", "content": CODER_SYSTEM},
        {"role": "user", "content": user_prompt},
    ]

    # record_event(state, "coder_input", {"messages": messages})
    log_state(state, "coder", "input")

    response = llm.invoke(messages)
    patch = (response.content or "").strip()

    # Basic validation — keep the original text but flag errors for the graph
    parsed = UnifiedDiff.parse(patch)
    if parsed is None:
        return {"last_patch": patch, "patch_error": "invalid unified-diff format"}

    # Use the cleaned/raw version produced by the parser (stripped fences)
    cleaned = parsed.get("raw", patch)
    return {"last_patch": cleaned}