"""
Function calling integration for Cite-Agent.

Handles the function calling workflow:
1. Send user query to LLM with available tools
2. Parse LLM response for tool calls
3. Execute requested tools
4. Send results back to LLM for final response
"""

import json
import os
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

from .function_tools import TOOLS, validate_tool_call


@dataclass
class ToolCall:
    """Represents a tool call from the LLM"""
    id: str
    name: str
    arguments: Dict[str, Any]


@dataclass
class FunctionCallingResponse:
    """Response from function calling workflow"""
    response: str  # Final text response
    tool_calls: List[ToolCall]  # Tools that were called
    tool_results: Dict[str, Any]  # Results from tool executions
    tokens_used: int = 0
    model: str = ""


class FunctionCallingAgent:
    """
    Handles function calling workflow with Cerebras/OpenAI compatible APIs.
    """

    def __init__(self, client, model: str = "gpt-oss-120b", provider: str = "cerebras"):
        """
        Initialize function calling agent.

        Args:
            client: OpenAI-compatible client (Cerebras or OpenAI)
            model: Model name to use
            provider: Provider name ('cerebras' or 'openai')
        """
        self.client = client
        self.model = model
        self.provider = provider
        self.debug_mode = os.getenv("NOCTURNAL_DEBUG", "").lower() == "1"

    async def process_query(
        self,
        query: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        system_prompt: Optional[str] = None
    ) -> FunctionCallingResponse:
        """
        Process a query using function calling.

        Workflow:
        1. Call LLM with query + tools
        2. If LLM wants to call tools:
           a. Execute tools
           b. Send results back to LLM
           c. Get final response
        3. Return final response

        Args:
            query: User query
            conversation_history: Previous messages
            system_prompt: Optional system prompt override

        Returns:
            FunctionCallingResponse with final answer and metadata
        """
        if conversation_history is None:
            conversation_history = []

        # Build messages
        messages = []

        # Add system prompt if provided
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        else:
            # Default system prompt
            messages.append({
                "role": "system",
                "content": (
                    "You are a helpful AI research assistant. You have access to tools for:\n"
                    "- Searching academic papers (200M+ papers)\n"
                    "- Getting financial data (SEC filings, stock prices)\n"
                    "- Web search for current information\n"
                    "- File system operations (read, write, list)\n"
                    "- Shell commands\n\n"
                    "Choose the appropriate tool(s) based on the user's query. "
                    "For conversational queries (greetings, meta questions, acknowledgments), "
                    "use the 'chat' tool directly without calling other tools."
                )
            })

        # Add conversation history
        messages.extend(conversation_history)

        # Add current query
        messages.append({"role": "user", "content": query})

        if self.debug_mode:
            print(f"🔍 [Function Calling] Sending query to {self.provider}: {query[:100]}...")

        # Step 1: Initial LLM call with tools
        try:
            if self.debug_mode:
                print(f"🔍 [Function Calling] Calling {self.provider} with model {self.model}")

            # Add timeout to prevent hanging
            import httpx
            timeout = httpx.Timeout(30.0, connect=10.0)  # 30s total, 10s connect

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                tools=TOOLS,
                tool_choice="auto",  # Let LLM decide
                temperature=0.2,  # Low temperature for more consistent tool selection
                timeout=timeout
            )

            if self.debug_mode:
                print(f"🔍 [Function Calling] Got response from {self.provider}")

        except Exception as e:
            error_str = str(e)

            # Check if it's a rate limit error (429)
            if "429" in error_str or "rate" in error_str.lower() or "queue" in error_str.lower():
                if self.debug_mode:
                    print(f"⚠️ [Function Calling] {self.provider} rate limited (429), using quick response for simple queries")

                # For simple queries like "test", "hi", etc., just return a quick response
                # instead of erroring out
                simple_responses = {
                    "test": "I'm ready to help. What would you like to work on?",
                    "testing": "I'm ready to help. What would you like to work on?",
                    "hi": "Hello! What can I help you with today?",
                    "hello": "Hello! What can I help you with today?",
                    "hey": "Hi! What can I assist you with?",
                    "chat": "I'm here to help. What would you like to discuss?",
                }

                query_lower = query.lower().strip()
                if query_lower in simple_responses:
                    if self.debug_mode:
                        print(f"🔍 [Function Calling] Using fallback response for '{query_lower}'")
                    return FunctionCallingResponse(
                        response=simple_responses[query_lower],
                        tool_calls=[],
                        tool_results={},
                        tokens_used=0
                    )

            if self.debug_mode:
                print(f"❌ [Function Calling] LLM call failed: {type(e).__name__}: {e}")
                import traceback
                traceback.print_exc()

            # Fallback: return error as chat response
            return FunctionCallingResponse(
                response=f"I encountered an error calling the LLM: {str(e)}",
                tool_calls=[],
                tool_results={},
                tokens_used=0
            )

        message = response.choices[0].message
        tokens_used = response.usage.total_tokens if hasattr(response, 'usage') else 0

        # Check if LLM wants to call tools
        if not message.tool_calls:
            # Direct response (chat tool or no tools needed)
            if self.debug_mode:
                print(f"🔍 [Function Calling] No tool calls, direct response")

            return FunctionCallingResponse(
                response=message.content or "I'm not sure how to help with that.",
                tool_calls=[],
                tool_results={},
                tokens_used=tokens_used,
                model=self.model
            )

        # Step 2: Execute tool calls
        if self.debug_mode:
            print(f"🔍 [Function Calling] {len(message.tool_calls)} tool(s) requested")

        tool_calls_list = []
        tool_results = {}
        tool_messages = []  # For sending back to LLM

        for tool_call in message.tool_calls:
            tool_name = tool_call.function.name
            try:
                tool_args = json.loads(tool_call.function.arguments)
            except json.JSONDecodeError as e:
                if self.debug_mode:
                    print(f"❌ [Function Calling] Invalid JSON in arguments: {e}")
                tool_args = {}

            if self.debug_mode:
                print(f"🔍 [Function Calling] Tool: {tool_name}, Args: {tool_args}")

            # Validate tool call
            is_valid, error_msg = validate_tool_call(tool_name, tool_args)
            if not is_valid:
                if self.debug_mode:
                    print(f"❌ [Function Calling] Validation failed: {error_msg}")
                tool_results[tool_call.id] = {"error": error_msg}
                tool_messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps({"error": error_msg})
                })
                continue

            # Store tool call
            tool_calls_list.append(ToolCall(
                id=tool_call.id,
                name=tool_name,
                arguments=tool_args
            ))

            # Tool execution happens in the main agent
            # For now, we just mark it as pending
            tool_results[tool_call.id] = {
                "tool": tool_name,
                "args": tool_args,
                "status": "pending"
            }

        # Return tool calls for execution by main agent
        # The main agent will execute tools and call finalize_response()
        return FunctionCallingResponse(
            response="",  # No final response yet
            tool_calls=tool_calls_list,
            tool_results=tool_results,
            tokens_used=tokens_used,
            model=self.model
        )

    async def finalize_response(
        self,
        original_query: str,
        conversation_history: List[Dict[str, str]],
        tool_calls: List[ToolCall],
        tool_execution_results: Dict[str, Any]
    ) -> FunctionCallingResponse:
        """
        Get final response from LLM after tools have been executed.

        Args:
            original_query: Original user query
            conversation_history: Conversation history
            tool_calls: Tool calls that were made
            tool_execution_results: Results from executing tools

        Returns:
            Final response from LLM
        """
        # Build messages for second LLM call
        messages = conversation_history.copy()

        # Add tool responses
        for tool_call in tool_calls:
            result = tool_execution_results.get(tool_call.id, {})
            messages.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": tool_call.name,
                "content": json.dumps(result)
            })

        if self.debug_mode:
            print(f"🔍 [Function Calling] Sending tool results back to LLM for synthesis")

        # Call LLM again with tool results
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3
            )

            final_response = response.choices[0].message.content
            tokens_used = response.usage.total_tokens if hasattr(response, 'usage') else 0

            if self.debug_mode:
                print(f"🔍 [Function Calling] Final response generated ({tokens_used} tokens)")

            return FunctionCallingResponse(
                response=final_response,
                tool_calls=tool_calls,
                tool_results=tool_execution_results,
                tokens_used=tokens_used,
                model=self.model
            )

        except Exception as e:
            if self.debug_mode:
                print(f"❌ [Function Calling] Finalize call failed: {e}")

            # Fallback: synthesize response from tool results
            results_summary = []
            for tool_call in tool_calls:
                result = tool_execution_results.get(tool_call.id, {})
                if "error" not in result:
                    results_summary.append(f"{tool_call.name}: {json.dumps(result)[:200]}")

            return FunctionCallingResponse(
                response=f"I found:\n" + "\n".join(results_summary) if results_summary else "I completed the requested actions.",
                tool_calls=tool_calls,
                tool_results=tool_execution_results,
                tokens_used=0,
                model=self.model
            )


def detect_simple_chat_query(query: str) -> bool:
    """
    Fast check if query is a simple chat that doesn't need tools.
    Used to bypass function calling for obvious cases.
    """
    query_lower = query.lower().strip()

    # Single word greetings/acknowledgments
    simple_words = {
        'hi', 'hello', 'hey', 'test', 'testing', 'thanks', 'thank',
        'bye', 'ok', 'okay', 'yes', 'no', 'maybe'
    }

    if query_lower in simple_words:
        return True

    # Short conversational phrases
    simple_phrases = [
        'how are you', 'whats up', 'thank you', 'thanks a lot',
        'got it', 'i see', 'sounds good', 'makes sense',
        'just testing', 'this is a test'
    ]

    query_normalized = ''.join(c for c in query_lower if c.isalnum() or c.isspace()).strip()
    if query_normalized in simple_phrases:
        return True

    return False
