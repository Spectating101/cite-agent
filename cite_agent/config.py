#!/usr/bin/env python3
"""
Configuration Management for Cite-Agent
Centralizes all hard-coded values and environment variables
"""
import os
from typing import Optional
from dataclasses import dataclass


@dataclass
class AgentConfig:
    """Configuration for Enhanced Nocturnal Agent"""

    # Token and Cost Limits
    daily_token_limit: int = 100_000
    per_user_token_limit: int = 50_000  # 50 queries at ~1000 tokens each
    cost_per_1k_tokens: float = 0.0001  # Groq pricing estimate

    # Rate Limiting
    daily_query_limit: int = 100  # Can be overridden by env var
    key_recheck_seconds: float = 3600.0  # 1 hour
    health_check_ttl: float = 30.0  # seconds

    # Shell Execution
    shell_command_timeout: int = 30  # seconds (increased for R scripts)
    shell_read_timeout: float = 1.0  # seconds per readline

    # Conversation History
    max_history_messages: int = 100  # Keep last 100 messages (50 exchanges)

    # API Configuration
    backend_api_url: str = "https://cite-agent-api-720dfadd602c.herokuapp.com"
    archive_api_url: str = "https://cite-agent-api-720dfadd602c.herokuapp.com/api"
    finsight_api_url: str = "https://cite-agent-api-720dfadd602c.herokuapp.com/v1/finance"

    # API Timeouts
    backend_query_timeout: int = 60  # seconds
    backend_retry_delays: list = None  # Will be set in __post_init__

    # Response Generation
    llm_temperature: float = 0.2  # Low temp for accuracy
    llm_max_tokens: int = 4000
    llm_model: str = "openai/gpt-oss-120b"  # Production model

    # File Operations
    max_file_preview_lines: int = 10
    max_file_read_size: int = 1_000_000  # 1MB

    # Search and Grep
    default_search_results: int = 100
    max_glob_results: int = 1000

    def __post_init__(self):
        """Initialize computed values"""
        if self.backend_retry_delays is None:
            self.backend_retry_delays = [5, 15, 30]  # Exponential backoff

        # Override from environment variables
        self.daily_query_limit = int(os.getenv("NOCTURNAL_QUERY_LIMIT", str(self.daily_query_limit)))
        self.backend_api_url = os.getenv("NOCTURNAL_API_URL", self.backend_api_url)
        self.archive_api_url = os.getenv("ARCHIVE_API_URL", self.archive_api_url)
        self.finsight_api_url = os.getenv("FINSIGHT_API_URL", self.finsight_api_url)

        # Debug mode
        self.debug_mode = os.getenv("NOCTURNAL_DEBUG", "").lower() == "1"


# Global configuration instance
_config: Optional[AgentConfig] = None


def get_config() -> AgentConfig:
    """Get global configuration instance (singleton pattern)"""
    global _config
    if _config is None:
        _config = AgentConfig()
    return _config


def set_config(config: AgentConfig):
    """Set global configuration (for testing)"""
    global _config
    _config = config


# Convenience accessors
def get_backend_url() -> str:
    return get_config().backend_api_url


def get_archive_url() -> str:
    return get_config().archive_api_url


def get_finsight_url() -> str:
    return get_config().finsight_api_url


def is_debug_mode() -> bool:
    return get_config().debug_mode


def get_shell_timeout() -> int:
    return get_config().shell_command_timeout


def get_max_history() -> int:
    return get_config().max_history_messages
