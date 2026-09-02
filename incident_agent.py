import os
import sys
import time
from typing import Literal
from dotenv import load_dotenv

# Load environment variables from .env if present
load_dotenv()

# Verify environment variables
os.environ.setdefault("LANGSMITH_TRACING", "true")
os.environ.setdefault("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
os.environ.setdefault("LANGSMITH_PROJECT", "pr-majestic-fiber-62")

from langchain_core.messages import HumanMessage, SystemMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode

# Optional rich formatting for a jaw-dropping terminal presentation
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.markdown import Markdown
    console = Console()
    HAS_RICH = True
except ImportError:
    HAS_RICH = False
    console = None

def print_banner():
    title = "⚡ ENTERPRISE INCIDENT & OPERATIONS TRIAGE AGENT ⚡"
    subtitle = "Powered by LangChain (Tools) + LangGraph (Cyclic Engine) + LangSmith (Observability)"
    if HAS_RICH:
        console.print(Panel.fit(f"[bold cyan]{title}[/bold cyan]\n[dim yellow]{subtitle}[/dim yellow]", border_style="bright_blue"))
    else:
        print("=" * 70)
        print(title)
        print(subtitle)
        print("=" * 70)

# =====================================================================
# 1. LANGCHAIN LAYER: Define Standardized Enterprise Tools
# =====================================================================

@tool
def fetch_service_telemetry(service_name: str) -> str:
    """Queries live telemetry and metrics (CPU, memory, latency, connection pools) for an internal microservice."""
    metrics_db = {
        "checkout-api": {
            "status": "CRITICAL",
            "http_5xx_rate": "18.4%",
            "p99_latency": "4200ms",
            "upstream_dependency": "orders-db",
            "active_pods": 12
        },
        "orders-db": {
            "status": "DEGRADED",
            "cpu_utilization": "94%",
            "connection_pool": "100/100 (SATURATED)",
            "waiting_clients": 142,
            "read_replica_lag": "0.4s"
        },
        "payment-gateway": {
            "status": "HEALTHY",
            "http_5xx_rate": "0.01%",
            "p99_latency": "120ms"
        }
    }
    key = service_name.lower().strip()
    data = metrics_db.get(key, None)
    if data:
        return f"Telemetry for [{service_name}]: {data}"
    return f"Service '{service_name}' not found in telemetry registry. Available services: {list(metrics_db.keys())}"

@tool
def search_internal_runbooks(query: str) -> str:
    """Searches engineering runbooks, disaster recovery procedures, and standard operating procedures (SOPs)."""
    runbooks = [
        {
            "id": "RB-042",
            "topic": "database connection pool saturation",
            "procedure": "1. Run query inspection to find long-running lock contention or unindexed queries. 2. If unindexed query is blocking, terminate stale connection pool sessions. 3. Allocate 2 additional read replicas."
        },
        {
            "id": "RB-019",
            "topic": "payment gateway timeout",
            "procedure": "1. Verify 3rd-party webhook status. 2. Enable circuit-breaker pattern. 3. Route to backup processor (Stripe -> Adyen fallback)."
        }
    ]
    query_lower = query.lower()
    matched = [rb for rb in runbooks if any(word in rb["topic"] for word in query_lower.split())]
    if matched:
        return f"Found matching runbook: {matched[0]}"
    return f"Found default runbook [RB-001]: Inspect logs, verify dependency telemetry, and notify on-call engineer."

@tool
def inspect_database_queries(database_name: str) -> str:
    """Inspects active transactions, lock contention, and top slow queries on a database instance."""
    if "orders-db" in database_name.lower():
        return (
            "Active Queries Analysis for [orders-db]:\n"
            "- Found 84 blocked threads waiting on PID 40912\n"
            "- PID 40912 Query: 'SELECT * FROM cart_items WHERE user_id = ? FOR UPDATE' (Running for 312s)\n"
            "- Root Cause: Missing composite index on `cart_items(user_id, status)` causing full table scan during checkout peak."
        )
    return f"Database '{database_name}' has 12 active connections, all queries executing under 15ms."

@tool
def execute_safe_remediation(target_resource: str, action: str) -> str:
    """Executes verified remediation actions (e.g. terminating stale locked transaction, restarting connection pool)."""
    valid_actions = ["terminate_stale_pid", "flush_connection_pool", "scale_read_replica"]
    action_clean = action.lower().strip()
    return f"SUCCESS: Action '{action_clean}' executed on resource '{target_resource}'. Latency dropped back to 85ms. Connection pool restored to 22/100."

# Bind tools to the foundation model
tools = [
    fetch_service_telemetry,
    search_internal_runbooks,
    inspect_database_queries,
    execute_safe_remediation
]

# Model configuration
model = ChatOpenAI(
    model="gpt-4o-mini",
    temperature=0
).bind_tools(tools)

# =====================================================================
# 2. LANGGRAPH LAYER: Cyclic Multi-Step Graph Definition
# =====================================================================

SYSTEM_PROMPT = """You are an Enterprise Incident & Operations Copilot inside our Agentic Workbench.
When an incident or alert is reported:
1. Fetch live telemetry for affected services.
2. Search internal runbooks to determine standard operating procedures (SOP).
3. Inspect deep diagnostics (e.g., database slow queries or logs) to confirm root cause.
4. Execute safe remediation actions if approved by runbooks.
5. Provide a crisp Executive Incident Summary:
   - Root Cause
   - Immediate Remediation Taken
   - Long-term Prevention Recommendation
"""

def should_continue(state: MessagesState) -> Literal["tools", "__end__"]:
    """Conditional Edge: Inspects if the model requested tool execution."""
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return "__end__"

def call_model(state: MessagesState):
    """Agent Node: Calls the LLM with full message history and system prompt."""
    messages = state["messages"]
    # Ensure system prompt is prepended on first turn
    if not any(isinstance(m, SystemMessage) for m in messages):
        messages = [SystemMessage(content=SYSTEM_PROMPT)] + messages
    
    response = model.invoke(messages)
    return {"messages": [response]}

# Assemble the StateGraph
workflow = StateGraph(MessagesState)

# Add Nodes
workflow.add_node("agent", call_model)
workflow.add_node("tools", ToolNode(tools))

# Add Edges
workflow.add_edge(START, "agent")
workflow.add_conditional_edges("agent", should_continue, ["tools", END])
workflow.add_edge("tools", "agent")  # Cyclic loop back to agent

# Compile into Pregel runnable
app = workflow.compile()

# =====================================================================
# 3. RUNTIME & PRESENTATION OUTPUT
# =====================================================================

def run_incident_demo(user_query: str):
    print_banner()
    
    if HAS_RICH:
        console.print(Panel(f"[bold white]User Incident Report:[/bold white]\n[yellow]{user_query}[/yellow]", title="Incoming Workbench Alert", border_style="red"))
    else:
        print(f"\n[ALERT]: {user_query}\n")

    thread_id = f"incident-{int(time.time())}"
    config = {"configurable": {"thread_id": thread_id}}

    step_count = 1
    events = app.stream(
        {"messages": [HumanMessage(content=user_query)]},
        config=config,
        stream_mode="updates"
    )

    for event in events:
        for node_name, node_output in event.items():
            messages = node_output.get("messages", [])
            for msg in messages:
                if node_name == "agent":
                    if hasattr(msg, "tool_calls") and msg.tool_calls:
                        for tc in msg.tool_calls:
                            if HAS_RICH:
                                console.print(f"[bold yellow]Step {step_count} (Reasoning -> Tool Call):[/bold yellow] Calling [bold green]{tc['name']}[/bold green] with args [cyan]{tc['args']}[/cyan]")
                            else:
                                print(f"Step {step_count} (Agent): Requesting Tool '{tc['name']}' with {tc['args']}")
                            step_count += 1
                    else:
                        # Final synthesized answer
                        if HAS_RICH:
                            console.print("\n")
                            console.print(Panel(Markdown(msg.content), title="[bold green]Executive Incident Resolution[/bold green]", border_style="green"))
                        else:
                            print("\n=== EXECUTIVE INCIDENT RESOLUTION ===")
                            print(msg.content)
                elif node_name == "tools":
                    if HAS_RICH:
                        preview = str(msg.content)[:180] + "..." if len(str(msg.content)) > 180 else str(msg.content)
                        console.print(f"[dim]  └── Tool Output: {preview}[/dim]\n")
                    else:
                        print(f"  └── Tool Output: {msg.content}\n")

    print("\n" + "=" * 70)
    print("🎯 EXECUTION COMPLETE!")
    print(f"📊 Project: {os.environ.get('LANGSMITH_PROJECT')}")
    print(f"🔗 View Full Trace in LangSmith: https://smith.langchain.com")
    print("=" * 70)

if __name__ == "__main__":
    default_alert = "CRITICAL ALERT: checkout-api is throwing 504 gateway timeouts. Investigate telemetry, diagnose root cause, consult runbooks, and remediate."
    
    # If user passes custom prompt via command line args, use it
    if len(sys.argv) > 1:
        query = " ".join(sys.argv[1:])
    else:
        query = default_alert

    run_incident_demo(query)
