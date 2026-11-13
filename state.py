from typing import Annotated, TypedDict, List, Dict, Any
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage


class AgentState(TypedDict):
    # Conversation history (managed automatically by LangGraph)
    messages: Annotated[List[BaseMessage], add_messages]
    # Observability log of every tool call and decision
    audit_log: List[Dict[str, Any]]