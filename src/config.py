import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

class Settings:
    """Centralized configuration loader for the Agentic SRE Workbench."""
    
    # LangSmith Observability
    langsmith_tracing: bool = os.getenv("LANGSMITH_TRACING", "true").lower() == "true"
    langsmith_endpoint: str = os.getenv("LANGSMITH_ENDPOINT", "https://api.smith.langchain.com")
    langsmith_api_key: Optional[str] = os.getenv("LANGSMITH_API_KEY")
    langsmith_project: str = os.getenv("LANGSMITH_PROJECT", "pr-majestic-fiber-62")
    
    # LLM API Keys
    groq_api_key: Optional[str] = os.getenv("GROQ_API_KEY")
    openai_api_key: Optional[str] = os.getenv("OPENAI_API_KEY")
    
    # Target Infrastructure
    mongodb_uri: str = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
    github_token: Optional[str] = os.getenv("GITHUB_TOKEN")
    github_repo: str = os.getenv("GITHUB_REPO", "Vishnupriya-Selvraj/-enterprise_target_service")

    def get_resolved_provider(self) -> str:
        if self.groq_api_key:
            return "groq"
        elif self.openai_api_key:
            return "openai"
        return "mock"

    def get_resolved_model_name(self) -> str:
        if self.groq_api_key:
            return "openai/gpt-oss-120b"
        elif self.openai_api_key:
            return "gpt-4o"
        return "mock-model"

settings = Settings()
