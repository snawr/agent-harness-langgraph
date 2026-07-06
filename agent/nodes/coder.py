# nodes/coder.py
from agent.llm.client import LLMClient
from agent.parsers import UnifiedDiff
from agent.config.prompts import CODER_SYSTEM, CODER_USER_TEMPLATE

llm = LLMClient()


def coder_node(state):
    task = state["task"]
    step = state["current_step"]
    repo_context = state.get("repo_context", "")

    user_prompt = CODER_USER_TEMPLATE.format(task=task, step=step, repo_context=repo_context)

    messages = [
        {"role": "system", "content": CODER_SYSTEM},
        {"role": "user", "content": user_prompt},
    ]

    response = llm.invoke(messages)
    patch = (response.content or "").strip()

    # Basic validation — keep the original text but flag errors for the graph
    parsed = UnifiedDiff.parse(patch)
    if parsed is None:
        return {"last_patch": patch, "patch_error": "invalid unified-diff format"}

    # Use the cleaned/raw version produced by the parser (stripped fences)
    cleaned = parsed.get("raw", patch)
    return {"last_patch": cleaned}