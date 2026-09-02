from pydantic import BaseModel, Field
from typing import Literal

class TelemetryTraceQueryInput(BaseModel):
    """Input schema for querying distributed microservice traces, p99 latency, and error metrics."""
    service_name: str = Field(
        ...,
        description="The target microservice name (e.g. 'checkout-api', 'orders-db', 'auth-service').",
        examples=["checkout-api", "orders-db"]
    )
    metric_window_minutes: int = Field(
        default=15,
        description="Time window in minutes to inspect error rates and latency anomalies."
    )

class RunbookRAGInput(BaseModel):
    """Input schema for searching architecture docs and disaster recovery runbooks."""
    incident_symptoms: str = Field(
        ...,
        description="Keywords describing the failure mode (e.g. 'connection pool exhaustion', 'row lock contention', '504 gateway timeout')."
    )
    architecture_tier: Literal["database_storage", "api_gateway", "compute_worker"] = Field(
        default="database_storage",
        description="The infrastructure tier undergoing triage."
    )

class DatabaseLockAnalysisInput(BaseModel):
    """Input schema for running deep database lock contention and query plan analysis."""
    database_cluster: str = Field(
        ...,
        description="Identifier of the database cluster (e.g. 'orders-db-primary', 'checkout-api-primary')."
    )

class SandboxTestExecutionInput(BaseModel):
    """Input schema for executing code patches and unit tests in a secure sandboxed environment."""
    patch_code: str = Field(
        ...,
        description="The source code patch or database index migration command."
    )
    test_code: str = Field(
        default="",
        description="The unit test suite to execute against the patch."
    )

class SecuritySASTAuditInput(BaseModel):
    """Input schema for static application security testing (SAST) and vulnerability scanning."""
    code_to_audit: str = Field(
        ...,
        description="Source code or SQL/NoSQL command to inspect for injection vulnerabilities or security flaws."
    )
    target_language: Literal["python", "sql", "bash", "javascript", "nosql", "json"] = Field(
        default="javascript",
        description="Programming language of the code undergoing security scan."
    )

class GitPRDeploymentInput(BaseModel):
    """Input schema for creating a GitHub Pull Request and triggering automated CI/CD deployment."""
    repository_name: str = Field(
        ...,
        description="Target GitHub repository (e.g. 'enterprise/checkout-api')."
    )
    branch_name: str = Field(
        ...,
        description="Feature/Hotfix branch name (e.g. 'hotfix/p0-checkout-api-remediation')."
    )
    commit_message: str = Field(
        ...,
        description="Conventional commit message describing the patch."
    )
    patch_content: str = Field(
        ...,
        description="The validated code changes to merge into main."
    )
