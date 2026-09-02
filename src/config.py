import os
from typing import Optional, Literal
from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Load .env file
load_dotenv()

class AppSettings(BaseSettings):
    """Production application settings and telemetry configuration."""
    
    # Provider Selection: "groq" or "openai"
    llm_provider: Optional[Literal["groq", "openai"]] = Field(default=None, alias="LLM_PROVIDER")
    
    # API Keys
    groq_api_key: Optional[str] = Field(default=None, alias="GROQ_API_KEY")
    openai_api_key: Optional[str] = Field(default=None, alias="OPENAI_API_KEY")
    
    # Model Configuration (Defaults to qwen/qwen3.8-27b for Groq)
    model_name: Optional[str] = Field(default=None, alias="MODEL_NAME")
    model_temperature: float = Field(default=0.0, alias="MODEL_TEMPERATURE")
    
    # LangSmith Observability Settings
    langsmith_tracing: bool = Field(default=True, alias="LANGSMITH_TRACING")
    langsmith_endpoint: str = Field(default="https://api.smith.langchain.com", alias="LANGSMITH_ENDPOINT")
    langsmith_api_key: Optional[str] = Field(default=None, alias="LANGSMITH_API_KEY")
    langsmith_project: str = Field(default="pr-majestic-fiber-62", alias="LANGSMITH_PROJECT")
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )

    def get_resolved_provider(self) -> str:
        """Determines the active provider based on available keys."""
        if self.llm_provider:
            return self.llm_provider.lower()
        if self.groq_api_key:
            return "groq"
        if self.openai_api_key:
            return "openai"
        return "groq"

    def get_resolved_model_name(self) -> str:
        """Returns the appropriate model name for the selected provider."""
        if self.model_name:
            return self.model_name
        provider = self.get_resolved_provider()
        if provider == "groq":
            # Active tool-calling model on Groq
            return "qwen/qwen3.8-27b"
        return "gpt-4o-mini"

    def apply_telemetry_environment(self) -> None:
        """Applies configuration directly to os.environ for LangChain/LangSmith SDK automatic pickup."""
        if self.langsmith_tracing:
            os.environ["LANGSMITH_TRACING"] = "true"
            os.environ["LANGSMITH_ENDPOINT"] = self.langsmith_endpoint
            os.environ["LANGSMITH_PROJECT"] = self.langsmith_project
            if self.langsmith_api_key:
                os.environ["LANGSMITH_API_KEY"] = self.langsmith_api_key
        if self.groq_api_key:
            os.environ["GROQ_API_KEY"] = self.groq_api_key
        if self.openai_api_key:
            os.environ["OPENAI_API_KEY"] = self.openai_api_key

# Global singleton configuration instance
settings = AppSettings()
settings.apply_telemetry_environment()
