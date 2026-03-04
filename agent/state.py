from typing import TypedDict, Annotated, List, Union, Optional
from langchain_core.messages import BaseMessage
import operator


class AgentState(TypedDict):
    messages: Annotated[List[BaseMessage], operator.add]  # full conversation history
    question: str                                          # current user question
    sql_query: Optional[str]                              # generated SQL
    sql_result: Optional[Union[List[dict], str]]          # query results or error string
    error: Optional[str]                                  # execution error message
    revision_count: int                                   # number of correction attempts
