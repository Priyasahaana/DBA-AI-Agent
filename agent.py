import os
from typing import Literal
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver

from state import AgentState
from tools import ALL_TOOLS, READ_ONLY_TOOLS, terminate_blocking_session
from guardrails import DISRUPTIVE_TOOLS, log_event

load_dotenv()

SYSTEM_PROMPT = """You are a Senior Site Reliability Engineer and PostgreSQL DBA Assistant.
Your job is to systematically investigate database incidents using your diagnostic tools before jumping to conclusions.

Investigation Protocol:
1. Start by checking database health (`check_db_health`) and connections (`check_connections`).
2. Based on findings, inspect deeper diagnostics (`check_blocking_locks` or `check_slow_queries`).
3. Always consult the relevant Standard Operating Procedure (`get_sop`) before recommending or executing any remediation.
4. Provide a clear, concise root-cause diagnosis citing exact metrics (PIDs, connection counts, durations, SOP ID).
5. If an SOP recommends a disruptive action (such as `terminate_blocking_session`), call the tool so the system can request human approval. Never fabricate tool results.
"""


def build_dba_graph():
    llm = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=0,
    ).bind_tools(ALL_TOOLS)

    def agent_node(state: AgentState):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + state["messages"]
        response = llm.invoke(messages)

        new_logs = list(state.get("audit_log", []))
        if response.tool_calls:
            for tc in response.tool_calls:
                new_logs.append(
                    log_event("AGENT_DECISION", {"planned_tool": tc["name"], "args": tc["args"]})
                )
        else:
            new_logs.append(log_event("AGENT_CONCLUSION", {"summary": response.content[:120] + "..."}))

        return {"messages": [response], "audit_log": new_logs}

    def route_after_agent(state: AgentState) -> Literal["safe_tools", "disruptive_tools", "__end__"]:
        last_message = state["messages"][-1]
        tool_calls = getattr(last_message, "tool_calls", None)

        if not tool_calls:
            return END

        # If any planned tool call is disruptive, route to the approval-gated node
        if any(tc["name"] in DISRUPTIVE_TOOLS for tc in tool_calls):
            return "disruptive_tools"

        return "safe_tools"

    safe_tool_node = ToolNode(READ_ONLY_TOOLS)
    disruptive_tool_node = ToolNode([terminate_blocking_session])

    workflow = StateGraph(AgentState)
    workflow.add_node("agent", agent_node)
    workflow.add_node("safe_tools", safe_tool_node)
    workflow.add_node("disruptive_tools", disruptive_tool_node)

    workflow.set_entry_point("agent")
    workflow.add_conditional_edges("agent", route_after_agent)
    workflow.add_edge("safe_tools", "agent")
    workflow.add_edge("disruptive_tools", "agent")

    # MemorySaver enables multi-turn conversation memory + interrupt_before checkpoints
    memory = MemorySaver()
    return workflow.compile(
        checkpointer=memory,
        interrupt_before=["disruptive_tools"],
    )