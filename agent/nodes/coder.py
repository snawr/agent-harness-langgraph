# nodes/coder.py
from agent.llm.client import LLMClient

llm = LLMClient()


def coder_node(state):
    task = state["task"]
    step = state["current_step"]
    repo_context = state.get("repo_context", "")

    messages = [
        {
            "role": "system",
            "content": (
                "You are a coding agent. "
                "You must output ONLY a valid unified diff patch. "
                "No explanations, no markdown."
            ),
        },
        {
            "role": "user",
            "content": f"""
                TASK:
                {task}

                STEP:
                {step}

                REPO CONTEXT:
                {repo_context}

                Return a unified diff patch.
                """
        },
    ]

    response = llm.invoke(messages)

    patch = response.content

    return {
        "last_patch": patch
    }