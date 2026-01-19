"""Configuration management for AI Company."""

import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings

# Load .env file
load_dotenv()

# Project root directory
PROJECT_ROOT = Path(__file__).parent.parent


class Settings(BaseSettings):
    """Application settings."""

    # LLM
    anthropic_api_key: str = Field(default="", env="ANTHROPIC_API_KEY")
    default_model: str = Field(default="claude-sonnet-4-20250514", env="DEFAULT_MODEL")

    # Database
    database_url: str = Field(
        default=f"sqlite:///{PROJECT_ROOT}/data/state.db",
        env="DATABASE_URL"
    )

    # Vector DB
    chroma_persist_dir: str = Field(
        default=str(PROJECT_ROOT / "data" / "chroma"),
        env="CHROMA_PERSIST_DIR"
    )

    # MCP Tokens (optional)
    mcp_figma_token: Optional[str] = Field(default=None, env="MCP_FIGMA_TOKEN")
    mcp_github_token: Optional[str] = Field(default=None, env="MCP_GITHUB_TOKEN")
    mcp_slack_token: Optional[str] = Field(default=None, env="MCP_SLACK_TOKEN")

    # Observability
    langsmith_api_key: Optional[str] = Field(default=None, env="LANGSMITH_API_KEY")
    langsmith_project: str = Field(default="ai-company", env="LANGSMITH_PROJECT")
    langsmith_tracing: bool = Field(default=False, env="LANGSMITH_TRACING")

    # Application
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    debug: bool = Field(default=False, env="DEBUG")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()


def get_settings() -> Settings:
    """Get application settings."""
    return settings
