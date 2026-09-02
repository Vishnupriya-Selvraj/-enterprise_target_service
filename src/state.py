from typing import Annotated, Sequence, Optional, Dict, Any, List
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

def merge_dicts(left: Optional[Dict[str, Any]], right: Optional[Dict[str, Any]]) -> Dict[str, Any]:
    """Custom reducer to merge parallel agent outputs into state."""
    merged = dict(left or {})
    if right:
        merged.update(right)
    return merged

class DevSecOpsState(TypedDict):
    """
    Complex 9-Node Multi-Agent State Schema for Autonomous SRE & DevSecOps Swarm.
    
    Attributes:
        messages: Central message history channel.
        incident_description: The original incident report or user alert.
        service_target: The primary affected microservice.
        
        # Parallel Intelligence Channels
        telemetry_diagnostics: Diagnostics from the Telemetry & Log Analyst.
        runbook_intelligence: SOPs & architectural knowledge from Runbook RAG.
        root_cause_analysis: Synthesized root cause from Diagnostic Fusion.
        
        # Code Patch & Validation State
        patch_code: Generated Python/SQL patch and hotfix.
        unit_test_code: Generated unit tests to verify the patch.
        qa_test_results: Execution results and traceback from Sandbox QA.
        qa_passed: Boolean indicating unit test success.
        
        # Security & Compliance State
        security_audit_report: Vulnerability findings from DevSecOps SAST.
        security_passed: Boolean indicating clean security scan.
        
        # Governance & Deployment
        human_approved: Boolean indicating Change Advisory Board (CAB) approval.
        iteration_count: Loop guard counter for self-healing loops.
        git_pr_url: Simulated GitHub Pull Request URL.
        post_mortem_report: Complete Executive Post-Mortem & Remediation Report.
    """
    messages: Annotated[Sequence[BaseMessage], add_messages]
    incident_description: Optional[str]
    service_target: Optional[str]
    
    # Parallel channels
    telemetry_diagnostics: Annotated[Optional[Dict[str, Any]], merge_dicts]
    runbook_intelligence: Annotated[Optional[Dict[str, Any]], merge_dicts]
    root_cause_analysis: Optional[Dict[str, Any]]
    
    # Patch & Testing
    patch_code: Optional[str]
    unit_test_code: Optional[str]
    qa_test_results: Optional[str]
    qa_passed: Optional[bool]
    
    # Security
    security_audit_report: Optional[str]
    security_passed: Optional[bool]
    
    # Deployment
    human_approved: Optional[bool]
    iteration_count: Optional[int]
    git_pr_url: Optional[str]
    post_mortem_report: Optional[str]
