import os
import pytest
from langchain_core.messages import HumanMessage
from guardrails import validate_pid, validate_sop_topic
from tools import reset_simulation, check_blocking_locks
from agent import build_dba_graph


def test_guardrail_blocks_protected_pids():
    with pytest.raises(PermissionError):
        validate_pid(1)


def test_guardrail_rejects_invalid_pid():
    with pytest.raises(ValueError):
        validate_pid(-5)


def test_guardrail_rejects_unknown_sop():
    with pytest.raises(ValueError):
        validate_sop_topic("drop_all_tables")


def test_simulation_reset():
    reset_simulation("blocking_locks_incident")
    result = check_blocking_locks.invoke({})
    assert result["has_blocking_locks"] is True
    assert result["blocking_sessions"][0]["blocking_pid"] == 48291


@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="Requires OPENAI_API_KEY")
def test_agent_investigates_and_pauses_for_approval():
    reset_simulation("blocking_locks_incident")
    graph = build_dba_graph()
    config = {"configurable": {"thread_id": "test-thread-1"}}

    graph.invoke(
        {"messages": [HumanMessage(content="Database is slow and connections are timing out. Investigate and fix.")]},
        config=config,
    )

    state = graph.get_state(config)
    # Verify the agent halted at the HITL checkpoint before terminating PID 48291
    assert "disruptive_tools" in state.next
    pending_calls = state.values["messages"][-1].tool_calls
    assert pending_calls[0]["name"] == "terminate_blocking_session"
    assert pending_calls[0]["args"]["pid"] == 48291

    # Verify diagnostic tools were called during investigation
    audit_tools = [entry["planned_tool"] for entry in state.values["audit_log"] if "planned_tool" in entry]
    assert "check_db_health" in audit_tools
    assert "check_blocking_locks" in audit_tools
    assert "get_sop" in audit_tools