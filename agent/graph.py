from langgraph.graph import StateGraph, END

from agent.nodes.planner import planner_node
from agent.nodes.coder import coder_node
from agent.nodes.patcher import patcher_node
from agent.nodes.executor import executor_node
from agent.nodes.critic import critic_node

from agent.state import AgentState


def build_graph():
    graph = StateGraph(AgentState)

    graph.add_node("planner", planner_node)
    graph.add_node("coder", coder_node)
    graph.add_node("patcher", patcher_node)
    graph.add_node("executor", executor_node)
    graph.add_node("critic", critic_node)

    graph.set_entry_point("planner")

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
