from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver

from .state import AgentState
from .nodes import sql_generator_node, sql_executor_node, sql_corrector_node, responder_node

MAX_REVISIONS = 3


def should_continue(state: AgentState) -> str:
    """
    Conditional edge after sql_executor_node.
    - No error → go to responder
    - Error + revisions remaining → go to corrector
    - Error + max revisions hit → go to responder (graceful failure)
    """
    if not state.get("error"):
        return "responder"
    if state.get("revision_count", 0) < MAX_REVISIONS:
        return "corrector"
    return "responder"


# ── Build graph ────────────────────────────────────────────────────────────────
workflow = StateGraph(AgentState)

workflow.add_node("generator", sql_generator_node)
workflow.add_node("executor",  sql_executor_node)
workflow.add_node("corrector", sql_corrector_node)
workflow.add_node("responder", responder_node)

workflow.set_entry_point("generator")

workflow.add_edge("generator", "executor")
workflow.add_conditional_edges(
    "executor",
    should_continue,
    {"corrector": "corrector", "responder": "responder"},
)
workflow.add_edge("corrector", "executor")
workflow.add_edge("responder", END)

memory = MemorySaver()
app = workflow.compile(checkpointer=memory)
