"""
Utilities for memory, telemetry, and token management
"""

import hashlib
from typing import Dict, Any, Optional
from datetime import datetime, timezone


class AgentUtilities:
    """
    Utility methods for memory, telemetry, and resource management

    Features:
    - Memory context management
    - Telemetry emission
    - Token budget tracking
    - Identifier hashing
    """

    def get_memory_context(self, memory: Dict, user_id: str, conversation_id: str) -> str:
        """
        Get relevant memory context for the conversation

        Args:
            memory: Memory dictionary
            user_id: User identifier
            conversation_id: Conversation identifier

        Returns:
            Formatted memory context string
        """
        if user_id not in memory:
            memory[user_id] = {}

        if conversation_id not in memory[user_id]:
            memory[user_id][conversation_id] = []

        # Get last 3 interactions for context
        recent_memory = memory[user_id][conversation_id][-3:]
        if not recent_memory:
            return ""

        context = "Recent conversation context:\n"
        for mem in recent_memory:
            context += f"- {mem}\n"
        return context

    def update_memory(self, memory: Dict, user_id: str, conversation_id: str, interaction: str):
        """
        Update memory with new interaction

        Args:
            memory: Memory dictionary
            user_id: User identifier
            conversation_id: Conversation identifier
            interaction: New interaction to add
        """
        if user_id not in memory:
            memory[user_id] = {}

        if conversation_id not in memory[user_id]:
            memory[user_id][conversation_id] = []

        memory[user_id][conversation_id].append(interaction)

        # Keep only last 10 interactions
        if len(memory[user_id][conversation_id]) > 10:
            memory[user_id][conversation_id] = memory[user_id][conversation_id][-10:]

    @staticmethod
    def hash_identifier(value: Optional[str]) -> Optional[str]:
        """
        Hash identifier for privacy

        Args:
            value: Value to hash

        Returns:
            First 16 chars of SHA256 hash
        """
        if not value:
            return None
        digest = hashlib.sha256(value.encode("utf-8")).hexdigest()
        return digest[:16]

    @staticmethod
    def format_model_error(details: str) -> str:
        """
        Format model error message

        Args:
            details: Error details

        Returns:
            Formatted error message
        """
        headline = "⚠️ I couldn't finish the reasoning step because the language model call failed."
        advice = "Please retry shortly or verify your Groq API keys and network connectivity."
        if details:
            return f"{headline}\n\nDetails: {details}\n\n{advice}"
        return f"{headline}\n\n{advice}"

    def check_token_budget(self, daily_token_usage: int, daily_limit: int, estimated_tokens: int) -> bool:
        """Check if we have enough token budget"""
        return (daily_token_usage + estimated_tokens) < daily_limit

    def check_user_token_budget(
        self,
        user_token_usage: Dict[str, int],
        per_user_token_limit: int,
        user_id: str,
        estimated_tokens: int
    ) -> bool:
        """Check user-specific token budget"""
        current = user_token_usage.get(user_id, 0)
        return (current + estimated_tokens) < per_user_token_limit

    def check_query_budget(
        self,
        daily_query_count: int,
        daily_query_limit: int,
        user_query_counts: Dict[str, int],
        per_user_query_limit: int,
        user_id: Optional[str]
    ) -> bool:
        """Check if user has query budget remaining"""
        if daily_query_limit > 0 and daily_query_count >= daily_query_limit:
            return False

        effective_limit = per_user_query_limit if per_user_query_limit > 0 else daily_query_limit
        if user_id and effective_limit > 0 and user_query_counts.get(user_id, 0) >= effective_limit:
            return False

        return True

    def ensure_usage_day(
        self,
        usage_day: str,
        daily_token_usage: int,
        user_token_usage: Dict[str, int],
        daily_query_count: int,
        user_query_counts: Dict[str, int]
    ) -> tuple:
        """
        Ensure usage tracking is for current day, reset if needed

        Returns:
            Tuple of (new_usage_day, new_daily_token_usage, new_user_token_usage, new_daily_query_count, new_user_query_counts)
        """
        current_day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        if current_day != usage_day:
            return current_day, 0, {}, 0, {}
        return usage_day, daily_token_usage, user_token_usage, daily_query_count, user_query_counts
