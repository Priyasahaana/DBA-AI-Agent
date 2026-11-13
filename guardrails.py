import logging
from datetime import datetime, timezone
from typing import Dict, Any, Set

# Configure clean observability logger
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger("dba-agent")

# Protected system PIDs that the agent is strictly forbidden from terminating
PROTECTED_PIDS: Set[int] = {1, 2, 100, 999}

# Allowed SOP topics
ALLOWED_SOP_TOPICS: Set[str] = {
    "db_status",
    "connection_exhaustion",
    "blocking_locks",
    "slow_queries"
}

# Tools classified as high-impact / disruptive (trigger HITL interrupt)
DISRUPTIVE_TOOLS: Set[str] = {"terminate_blocking_session"}


def validate_pid(pid: int) -> None:
    """Guardrail: Ensure PID is a valid positive integer and not a system process."""
    if not isinstance(pid, int) or pid <= 0:
        raise ValueError(f"Guardrail Violation: Invalid PID '{pid}'. Must be a positive integer.")
    if pid in PROTECTED_PIDS:
        raise PermissionError(
            f"Guardrail Violation: PID {pid} is a protected PostgreSQL background/replication process."
        )


def validate_sop_topic(topic: str) -> str:
    """Guardrail: Normalize and validate requested SOP topic."""
    clean_topic = topic.strip().lower()
    if clean_topic not in ALLOWED_SOP_TOPICS:
        raise ValueError(
            f"Guardrail Violation: Unknown SOP topic '{topic}'. "
            f"Allowed topics: {', '.join(sorted(ALLOWED_SOP_TOPICS))}"
        )
    return clean_topic


def log_event(event_type: str, details: Dict[str, Any]) -> Dict[str, Any]:
    """Observability helper to record structured agent events."""
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "event_type": event_type,
        **details,
    }
    logger.info(f"[{event_type}] {details}")
    return entry