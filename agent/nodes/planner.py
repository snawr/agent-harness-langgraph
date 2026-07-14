# nodes/planner.py

from agent.logging import log_state, record_event
from agent.config.prompts import PLANNER_SYSTEM, PLANNER_USER_TEMPLATE
from agent.llm.client import LLMClient

llm = LLMClient()

def planner_node(state):
    task = state["task"]
    # repo_context = state.get("repo_context", "")
    repo_context = state.get("files", "")

    # record_event(state, "planner_input", {"task": task})
    log_state(state, "planner", "input")

    user_prompt = PLANNER_USER_TEMPLATE.format(task=task, repo_context=repo_context)
    print(f"Planner node user prompt:\n{user_prompt}\n{'-'*40}")
    messages = [
        {"role": "system", "content": PLANNER_SYSTEM},
        {"role": "user", "content": user_prompt},
    ]

    # record_event(state, "coder_input", {"messages": messages})
    log_state(state, "coder", "input")

    response = llm.invoke(messages)
    plan = (response.content or "").strip()

    result = {
        "plan": plan,
        "current_step": 0,
        "iteration": 0,
        "status": "running",
    }

    record_event(state, "planner_output", result)
    log_state(state, "planner", "output")
    return result