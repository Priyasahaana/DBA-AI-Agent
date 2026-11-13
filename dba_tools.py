
from langchain_core.tools import tool


@tool
def check_db_health() -> dict:
    """Check PostgreSQL database health, including CPU,
    memory, database status and response time."""

    return {
        "database": "postgresql",
        "status": "running",
        "cpu_usage_percent": 92,
        "memory_usage_percent": 85,
        "response_time_ms": 2500,
        "health": "degraded"
    }
