from langgraph.graph import StateGraph, END

from agent.logging import append_trace, configure_logging, log_state, record_event
from agent.nodes.planner import planner_node
from agent.nodes.coder import coder_node
from agent.nodes.patcher import patcher_node
from agent.nodes.executor import executor_node
from agent.nodes.critic import critic_node

from agent.state import AgentState


def build_graph():
    configure_logging()
    graph = StateGraph(AgentState)

    graph.set_entry_point("planner")

    def wrap_node(name, node):
        def wrapped(state):
            append_trace(state, f"enter:{name}")
            record_event(state, "node_enter", name)
            # log_state(state, name, "enter")
            result = node(state)
            if isinstance(result, dict):
                state.update(result)
            append_trace(state, f"exit:{name}")
            record_event(state, "node_exit", name)
            # log_state(state, name, "exit")
            return result

        return wrapped

    graph.add_node("planner", wrap_node("planner", planner_node))
    graph.add_node("coder", wrap_node("coder", coder_node))
    graph.add_node("patcher", wrap_node("patcher", patcher_node))
    graph.add_node("executor", wrap_node("executor", executor_node))
    graph.add_node("critic", wrap_node("critic", critic_node))

    graph.add_edge("planner", "coder")
    graph.add_edge("coder", "patcher")
    graph.add_edge("patcher", "executor")
    graph.add_edge("executor", "critic")

    def route(state):
        if state["status"] == "success":
            return END
        if state["status"] == "failed":
            return END
        return "coder"

    graph.add_conditional_edges("critic", route)

    return graph.compile()
