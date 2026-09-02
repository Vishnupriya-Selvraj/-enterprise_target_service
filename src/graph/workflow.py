from langgraph.graph import StateGraph, START, END

# Resilient checkpointer loader across all LangGraph package versions
try:
    from langgraph.checkpoint.memory import MemorySaver
except (ImportError, AttributeError):
    try:
        from langgraph.checkpoint.base import InMemorySaver as MemorySaver
    except (ImportError, AttributeError):
        MemorySaver = None

from src.state import DevSecOpsState
from src.graph.nodes import (
    sre_commander_node,
    telemetry_analyst_node,
    runbook_rag_node,
    diagnostic_fusion_node,
    patch_engineer_node,
    sandbox_qa_node,
    security_sast_node,
    human_cab_gate_node,
    deployment_and_postmortem_node,
    route_after_qa,
    route_after_security
)

def build_devsecops_swarm_graph(checkpointer: bool = False):
    """
    Constructs the 9-Node Autonomous SRE & DevSecOps Swarm StateGraph.
    
    Architecture Highlights:
    1. Parallel Fan-Out: sre_commander ➔ telemetry_analyst & runbook_rag concurrently.
    2. Fan-In Merge: Both streams converge at diagnostic_fusion.
    3. Self-Healing Code Loop: sandbox_qa ➔ patch_engineer if unit tests fail.
    4. DevSecOps Security Gate: security_sast ➔ patch_engineer if SAST audit fails.
    5. Change Advisory Board Gate: human_cab_gate ➔ deployment_and_postmortem.
    """
    workflow = StateGraph(DevSecOpsState)

    # Register all 9 Nodes
    workflow.add_node("sre_commander", sre_commander_node)
    workflow.add_node("telemetry_analyst", telemetry_analyst_node)
    workflow.add_node("runbook_rag", runbook_rag_node)
    workflow.add_node("diagnostic_fusion", diagnostic_fusion_node)
    workflow.add_node("patch_engineer", patch_engineer_node)
    workflow.add_node("sandbox_qa", sandbox_qa_node)
    workflow.add_node("security_sast", security_sast_node)
    workflow.add_node("human_cab_gate", human_cab_gate_node)
    workflow.add_node("deployment_and_postmortem", deployment_and_postmortem_node)

    # Wire Parallel Topology
    workflow.add_edge(START, "sre_commander")
    
    # Fan-Out to both parallel branches
    workflow.add_edge("sre_commander", "telemetry_analyst")
    workflow.add_edge("sre_commander", "runbook_rag")
    
    # Fan-In convergence
    workflow.add_edge("telemetry_analyst", "diagnostic_fusion")
    workflow.add_edge("runbook_rag", "diagnostic_fusion")
    
    # Patch Engineering
    workflow.add_edge("diagnostic_fusion", "patch_engineer")
    workflow.add_edge("patch_engineer", "sandbox_qa")
    
    # Self-Healing QA Conditional Edge
    workflow.add_conditional_edges(
        "sandbox_qa",
        route_after_qa,
        {"security_sast": "security_sast", "patch_engineer": "patch_engineer"}
    )
    
    # DevSecOps SAST Conditional Edge
    workflow.add_conditional_edges(
        "security_sast",
        route_after_security,
        {"human_cab_gate": "human_cab_gate", "patch_engineer": "patch_engineer"}
    )
    
    # CAB Gate to Production Deployment
    workflow.add_edge("human_cab_gate", "deployment_and_postmortem")
    workflow.add_edge("deployment_and_postmortem", END)

    if checkpointer and MemorySaver is not None:
        try:
            memory = MemorySaver()
            return workflow.compile(checkpointer=memory)
        except Exception:
            return workflow.compile()
            
    return workflow.compile()

# Canonical graph export for LangGraph Studio (checkpointer=False for platform persistence)
graph = build_devsecops_swarm_graph(checkpointer=False)
