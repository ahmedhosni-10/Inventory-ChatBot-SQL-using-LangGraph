import sqlite3
import os

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from .state import AgentState
from .prompts import SYSTEM_PROMPT, REPLAN_PROMPT, RESPONSE_PROMPT, get_schema_string

# ─────────────────────────────────────────────────────────────────────────────
# DB path — LLM created lazily so GROQ_API_KEY is loaded from .env before use
# ─────────────────────────────────────────────────────────────────────────────
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "inventory.db")


def _get_llm() -> ChatGroq:
    """Create a ChatGroq instance at call-time (after .env is loaded)."""
    return ChatGroq(model="llama-3.3-70b-versatile", temperature=0)


# ─────────────────────────────────────────────────────────────────────────────
def sql_generator_node(state: AgentState) -> dict:
    """Generates the initial SQL query based on the question."""
    schema = get_schema_string(DB_PATH)
    prompt = SYSTEM_PROMPT.format(schema=schema, question=state["question"])

    response = _get_llm().invoke([
        SystemMessage(content=prompt),
        HumanMessage(content=state["question"]),
    ])

    # Strip any accidental markdown fences
    sql = response.content.strip().strip("```sql").strip("```").strip()

    return {
        "messages": [AIMessage(content=sql)],
        "sql_query": sql,
        "error": None,
    }


# ─────────────────────────────────────────────────────────────────────────────
def sql_executor_node(state: AgentState) -> dict:
    """Executes the SQL query against the database."""
    sql = state["sql_query"]

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(sql)
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description] if cursor.description else []
        conn.close()

        # Convert to list of dicts for readability
        results = [dict(zip(columns, row)) for row in rows]

        return {
            "sql_result": results,
            "error": None,
        }

    except Exception as e:
        return {
            "sql_result": None,
            "error": str(e),
        }


# ─────────────────────────────────────────────────────────────────────────────
def sql_corrector_node(state: AgentState) -> dict:
    """Refines the SQL if an error occurred."""
    prompt = REPLAN_PROMPT.format(
        question=state["question"],
        sql_query=state["sql_query"],
        error=state["error"],
    )

    response = _get_llm().invoke([
        SystemMessage(content=prompt),
        HumanMessage(content="Please fix the SQL query."),
    ])

    corrected_sql = response.content.strip().strip("```sql").strip("```").strip()

    return {
        "messages": [AIMessage(content=corrected_sql)],
        "sql_query": corrected_sql,
        "error": None,
        "revision_count": state.get("revision_count", 0) + 1,
    }


# ─────────────────────────────────────────────────────────────────────────────
def responder_node(state: AgentState) -> dict:
    """Converts query results into a natural language response."""
    # Handle case where max retries hit — give a graceful message
    if state.get("error") and state.get("revision_count", 0) >= 3:
        answer = (
            f"I'm sorry, I couldn't build a valid query after "
            f"{state['revision_count']} attempts. "
            f"Could you rephrase your question?\n"
            f"[Debug] Last error: {state['error']}"
        )
        return {"messages": [AIMessage(content=answer)], "sql_result": answer}

    prompt = RESPONSE_PROMPT.format(
        question=state["question"],
        sql_query=state.get("sql_query", ""),
        sql_result=state.get("sql_result", []),
    )

    response = _get_llm().invoke([
        SystemMessage(content=prompt),
        HumanMessage(content=f"Answer my question: {state['question']}"),
    ])

    answer = response.content.strip()
    return {
        "messages": [AIMessage(content=answer)],
        "sql_result": answer,
    }
