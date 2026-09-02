import operator
from typing import Annotated, Sequence, Optional, Dict, Any, List
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

def merge_dicts(left: Optional[Dict[str, Any]], right: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Custom reducer to merge parallel agent outputs into graph state."""
    merged = dict(left or {})
    if right:
        merged.update(right)
    return merged

class DevSecOpsState(TypedDict):
    """
    Industry-Grade Multi-Agent State Schema for Autonomous SRE & DevSecOps Swarm.
    
    Features:
    - Channel-isolated reducers for parallel Fan-Out/Fan-In convergence.
    - Self-healing feedback channels tracking compiler/test tracebacks across cyclic iterations.
    - Dynamic agent reasoning scratchpads and tool execution audit trails.
    - Cryptographic CAB Governance tokens and compliance records.
    """
    # Core Message & Incident Channel
    messages: Annotated[Sequence[BaseMessage], add_messages]
    incident_description: Optional[str]
    service_target: Optional[str]
    severity_level: Optional[str]
    
    # Dynamic Agent Reasoning & Tool Audit Logs (Using native operator.add reducers)
    active_agents: Annotated[List[str], operator.add]
    agent_thoughts: Annotated[List[str], operator.add]
    tool_audit_trail: Annotated[List[Dict[str, Any]], operator.add]
    
    # Parallel Diagnostic Intelligence Channels
    telemetry_diagnostics: Annotated[Optional[Dict[str, Any]], merge_dicts]
    runbook_intelligence: Annotated[Optional[Dict[str, Any]], merge_dicts]
    root_cause_analysis: Optional[str]
    
    # Code Patch, Sandbox QA & Cyclic Reflection
    patch_code: Optional[str]
    test_code: Optional[str]
    qa_passed: Optional[bool]
    qa_output: Optional[str]
    qa_attempt_count: Optional[int]
    compiler_feedback: Annotated[List[str], operator.add]
    
    # Security SAST & DevSecOps Compliance
    security_approved: Optional[bool]
    security_audit_report: Optional[str]
    cwe_vulnerabilities_found: Optional[int]
    
    # Governance, Deployment & Executive Artifacts
    cab_approval_token: Optional[str]
    cab_risk_score: Optional[float]
    git_branch: Optional[str]
    git_pr_url: Optional[str]
    post_mortem_report: Optional[str]
