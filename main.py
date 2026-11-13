import uuid
from langchain_core.messages import HumanMessage, ToolMessage
from agent import build_dba_graph
from tools import reset_simulation


def run_cli():
    reset_simulation("blocking_locks_incident")
    graph = build_dba_graph()
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}

    print("=" * 65)
    print(" PostgreSQL Agentic DBA Assistant (Type 'exit' to quit)")
    print(" Active Simulated Incident: blocking_locks_incident")
    print("=" * 65)

    while True:
        user_input = input("\nDBA User > ").strip()
        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit"}:
            print("Session ended.")
            break

        # Run graph until completion OR until it hits interrupt_before=["disruptive_tools"]
        for event in graph.stream(
            {"messages": [HumanMessage(content=user_input)]},
            config=config,
            stream_mode="values",
        ):
            last_msg = event["messages"][-1]
            if last_msg.type == "ai" and not last_msg.tool_calls and last_msg.content:
                print(f"\nDBA Agent >\n{last_msg.content}")

        # Check if the graph paused at the Human-in-the-Loop approval gate
        snapshot = graph.get_state(config)
        if snapshot.next and "disruptive_tools" in snapshot.next:
            pending_ai_msg = snapshot.values["messages"][-1]
            tool_call = pending_ai_msg.tool_calls[0]

            print("\n" + "!" * 65)
            print(" HUMAN APPROVAL REQUIRED (High-Impact Action)")
            print(f" Proposed Action : {tool_call['name']}")
            print(f" Arguments       : {tool_call['args']}")
            print("!" * 65)

            decision = input("Approve execution? (yes/no) > ").strip().lower()

            if decision in {"yes", "y"}:
                print("\n[Approved] Executing action and resuming investigation...\n")
                # Passing None resumes execution from the saved checkpoint
                for event in graph.stream(None, config=config, stream_mode="values"):
                    last_msg = event["messages"][-1]
                    if last_msg.type == "ai" and not last_msg.tool_calls and last_msg.content:
                        print(f"\nDBA Agent >\n{last_msg.content}")
            else:
                print("\n[Rejected] Action blocked by human engineer.\n")
                # Inject a ToolMessage informing the LLM that the human rejected the action
                rejection_msg = ToolMessage(
                    tool_call_id=tool_call["id"],
                    name=tool_call["name"],
                    content="ACTION_REJECTED_BY_HUMAN: The DBA engineer denied permission to terminate this session. Provide manual mitigation alternatives instead.",
                )
                graph.update_state(config, {"messages": [rejection_msg]})
                for event in graph.stream(None, config=config, stream_mode="values"):
                    last_msg = event["messages"][-1]
                    if last_msg.type == "ai" and not last_msg.tool_calls and last_msg.content:
                        print(f"\nDBA Agent >\n{last_msg.content}")


if __name__ == "__main__":
    run_cli()