import sys
import os
import time
import argparse

# Force UTF-8 on Windows terminals
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

from langchain_core.messages import HumanMessage

from src.config import settings
from src.graph import build_incident_graph
from src.ui import IncidentPresenter

DEFAULT_ALERT = (
    "CRITICAL INCIDENT: The checkout-api microservice is experiencing severe 504 gateway timeouts "
    "and elevated 5xx error rates. Investigate telemetry, diagnose root causes, consult SOP runbooks, "
    "and execute necessary safe remediations to restore service stability."
)

def run_pipeline(user_prompt: str, thread_id: str = None) -> None:
    """Executes the Incident Triage Graph with live streaming telemetry."""
    
    # 1. Validate credentials
    active_provider = settings.get_resolved_provider()
    if active_provider == "groq" and not settings.groq_api_key:
        print("\n⚠️ WARNING: GROQ_API_KEY is not set in your .env or environment.")
        print("Please configure GROQ_API_KEY in .env before running live API calls.\n")
    elif active_provider == "openai" and not settings.openai_api_key:
        print("\n⚠️ WARNING: OPENAI_API_KEY is not set in your .env or environment.")
        print("Please configure OPENAI_API_KEY in .env before running live API calls.\n")

    thread_id = thread_id or f"incident-{int(time.time())}"
    presenter = IncidentPresenter()
    
    # 2. Print initial presentation header
    presenter.print_header(
        project_name=settings.langsmith_project,
        model_name=f"{settings.get_resolved_model_name()} ({active_provider.upper()})"
    )
    presenter.print_alert(user_prompt)

    # 3. Build compiled LangGraph engine
    graph = build_incident_graph(checkpointer=True)
    config = {"configurable": {"thread_id": thread_id}}

    step_counter = 1

    # 4. Stream execution supersteps
    events = graph.stream(
        {
            "messages": [HumanMessage(content=user_prompt)],
            "incident_id": thread_id,
            "step_count": 0
        },
        config=config,
        stream_mode="updates"
    )

    for event in events:
        for node_name, node_output in event.items():
            messages = node_output.get("messages", [])
            for msg in messages:
                if node_name == "agent":
                    if hasattr(msg, "tool_calls") and msg.tool_calls:
                        for tool_call in msg.tool_calls:
                            presenter.print_step(
                                step_number=step_counter,
                                tool_name=tool_call["name"],
                                tool_args=tool_call["args"]
                            )
                            step_counter += 1
                    elif msg.content:
                        presenter.print_resolution(msg.content)
                elif node_name == "tools":
                    presenter.print_tool_output(str(msg.content))

    # 5. Print footer with LangSmith trace reference
    presenter.print_footer(project_name=settings.langsmith_project)

def main():
    parser = argparse.ArgumentParser(
        description="Enterprise Incident & Operations Triage Agent Demo"
    )
    parser.add_argument(
        "query",
        nargs="*",
        default=[DEFAULT_ALERT],
        help="Custom incident report or prompt to triage."
    )
    parser.add_argument(
        "--thread",
        type=str,
        default=None,
        help="Custom session thread ID for state checkpointing."
    )
    
    args = parser.parse_args()
    user_prompt = " ".join(args.query) if isinstance(args.query, list) else args.query
    
    run_pipeline(user_prompt=user_prompt, thread_id=args.thread)

if __name__ == "__main__":
    main()
