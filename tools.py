import json
from pathlib import Path
from typing import Dict, Any
from langchain_core.tools import tool
from guardrails import validate_pid, validate_sop_topic, log_event

DATA_DIR = Path(__file__).parent / "data"
METRICS_PATH = DATA_DIR / "db_metrics.json"
SOPS_PATH = DATA_DIR / "sops.json"

# Load mock data into memory so simulated remediation persists during the session
with open(METRICS_PATH, "r", encoding="utf-8") as f:
    _DB_STATE: Dict[str, Any] = json.load(f)

with open(SOPS_PATH, "r", encoding="utf-8") as f:
    _SOPS_DATA: Dict[str, Any] = json.load(f)


def _get_current_scenario() -> Dict[str, Any]:
    active = _DB_STATE["active_scenario"]
    return _DB_STATE["scenarios"][active]


def reset_simulation(scenario_name: str = "blocking_locks_incident") -> None:
    """Helper for testing/demos to reset or switch active incident scenarios."""
    global _DB_STATE
    with open(METRICS_PATH, "r", encoding="utf-8") as f:
        _DB_STATE = json.load(f)
    if scenario_name in _DB_STATE["scenarios"]:
        _DB_STATE["active_scenario"] = scenario_name


@tool
def check_db_health() -> Dict[str, Any]:
    """Check overall PostgreSQL health, CPU, memory, disk I/O wait, and replication lag."""
    log_event("TOOL_CALL", {"tool": "check_db_health"})
    return _get_current_scenario()["db_health"]


@tool
def check_connections() -> Dict[str, Any]:
    """Check active, idle, and lock-waiting PostgreSQL connections against max_connections."""
    log_event("TOOL_CALL", {"tool": "check_connections"})
    return _get_current_scenario()["connections"]


@tool
def check_blocking_locks() -> Dict[str, Any]:
    """Inspect active blocking locks, blocking PIDs, transaction durations, and blocked sessions."""
    log_event("TOOL_CALL", {"tool": "check_blocking_locks"})
    return _get_current_scenario()["blocking_locks"]


@tool
def check_slow_queries() -> Dict[str, Any]:
    """Inspect currently running slow queries, durations, and wait events."""
    log_event("TOOL_CALL", {"tool": "check_slow_queries"})
    return {"slow_queries": _get_current_scenario()["slow_queries"]}


@tool
def get_sop(topic: str) -> Dict[str, Any]:
    """
    Retrieve the approved Standard Operating Procedure (SOP) for a database issue.
    Valid topics: 'db_status', 'connection_exhaustion', 'blocking_locks', 'slow_queries'.
    """
    clean_topic = validate_sop_topic(topic)
    log_event("TOOL_CALL", {"tool": "get_sop", "topic": clean_topic})
    return _SOPS_DATA[clean_topic]


@tool
def terminate_blocking_session(pid: int, reason: str) -> Dict[str, Any]:
    """
    DISRUPTIVE ACTION: Terminate a blocking PostgreSQL session by PID (simulates pg_terminate_backend).
    Requires human engineer approval before execution.
    """
    validate_pid(pid)
    log_event("DISRUPTIVE_TOOL_EXECUTION", {"tool": "terminate_blocking_session", "pid": pid, "reason": reason})

    scenario = _get_current_scenario()
    blocking_info = scenario["blocking_locks"]
    sessions = blocking_info.get("blocking_sessions", [])

    target = next((s for s in sessions if s["blocking_pid"] == pid), None)
    if not target:
        return {"status": "FAILED", "message": f"PID {pid} is not currently listed as a blocking session."}

    # Simulate database recovery after terminating the blocker
    _DB_STATE["active_scenario"] = "healthy_baseline"
    return {
        "status": "SUCCESS",
        "terminated_pid": pid,
        "released_blocked_pids": target["blocked_pids"],
        "message": f"Session PID {pid} terminated. Lock contention cleared and connection pool recovering."
    }


READ_ONLY_TOOLS = [
    check_db_health,
    check_connections,
    check_blocking_locks,
    check_slow_queries,
    get_sop,
]

ALL_TOOLS = READ_ONLY_TOOLS + [terminate_blocking_session]