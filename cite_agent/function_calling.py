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
    assistant_message: Optional[Any] = None  # Original assistant message with tool_calls


def format_tool_result(tool_name: str, result: Dict[str, Any]) -> str:
    """
    Format tool results into concise, structured summaries for synthesis.
    Reduces token usage and improves LLM understanding.
    """
    if "error" in result:
        return f"Error: {result['error']}"

    # Format based on tool type
    if tool_name == "search_papers":
        papers = result.get("papers", [])
        count = len(papers)
        if count == 0:
            return "No papers found"

        # Concise paper list (title, year, citations only)
        paper_summaries = []
        for p in papers[:5]:  # Max 5 papers in summary
            title = p.get("title", "Unknown")[:80]  # Truncate long titles
            year = p.get("year", "N/A")
            citations = p.get("citations_count", 0)
            paper_summaries.append(f"- {title} ({year}, {citations} cites)")

        return f"Found {count} papers:\n" + "\n".join(paper_summaries)

    elif tool_name == "get_financial_data":
        ticker = result.get("ticker", "Unknown")
        data = result.get("data", {})

        # Extract key metrics
        summaries = []
        for metric, info in data.items():
            if isinstance(info, dict):
                value = info.get("value", "N/A")
                period = info.get("period", "")
                summaries.append(f"{metric}: ${value:,.0f}" if isinstance(value, (int, float)) else f"{metric}: {value}")

        return f"{ticker} - " + ", ".join(summaries) if summaries else json.dumps(result)[:200]

    elif tool_name == "list_directory":
        listing = result.get("listing", "")
        lines = listing.split("\n")[:10]  # Max 10 lines
        return "\n".join(lines) + ("...[more files]" if len(listing.split("\n")) > 10 else "")

    elif tool_name == "chat":
        return result.get("message", "")

    # Default: truncated JSON
    return json.dumps(result)[:400]


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
            # Default system prompt (compressed for token efficiency)
            messages.append({
                "role": "system",
                "content": (
                    "Route queries to tools: papers/research→search_papers, "
                    "financials/stocks→get_financial_data, files/folders→list_directory, "
                    "shell commands→execute_shell_command, news/current events→web_search. "
                    "Use chat only for greetings/thanks. Prefer action tools."
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
                    print(f"⚠️ [Function Calling] {self.provider} rate limited (429)")
                # Return user-friendly rate limit message
                return FunctionCallingResponse(
                    response="The AI service is experiencing high traffic right now. Please try again in a moment.",
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
            model=self.model,
            assistant_message=message  # Include original assistant message for finalize
        )

    async def finalize_response(
        self,
        original_query: str,
        conversation_history: List[Dict[str, str]],
        tool_calls: List[ToolCall],
        tool_execution_results: Dict[str, Any],
        assistant_message: Optional[Any] = None
    ) -> FunctionCallingResponse:
        """
        Get final response from LLM after tools have been executed.

        Args:
            original_query: Original user query
            conversation_history: Conversation history
            tool_calls: Tool calls that were made
            tool_execution_results: Results from executing tools
            assistant_message: Original assistant message with tool_calls (optional)

        Returns:
            Final response from LLM
        """
        # OPTIMIZATION: Skip synthesis for simple chat responses (saves ~700 tokens)
        if (len(tool_calls) == 1 and
            tool_calls[0].name == "chat" and
            len(original_query.split()) <= 3):  # Simple greetings like "hi", "hello", "thanks"

            # Return chat response directly without second LLM call
            result = tool_execution_results.get(tool_calls[0].id, {})
            if "message" in result:
                if self.debug_mode:
                    print(f"🔍 [Function Calling] Skipping synthesis for simple chat (token optimization)")
                return FunctionCallingResponse(
                    response=result["message"],
                    tool_calls=tool_calls,
                    tool_results=tool_execution_results,
                    tokens_used=0,  # No second LLM call
                    model=self.model
                )

        # Build messages for second LLM call
        messages = conversation_history.copy()

        # If tool_calls is empty, conversation_history already has everything
        # (multi-step execution case)
        if tool_calls:
            # Single-step case: Add assistant message and tool results

            # Add assistant message with tool_calls if provided
            # This is REQUIRED by OpenAI's chat completion API
            if assistant_message and hasattr(assistant_message, 'tool_calls') and assistant_message.tool_calls:
                messages.append({
                    "role": "assistant",
                    "content": assistant_message.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in assistant_message.tool_calls
                    ]
                })

            # Add tool responses (formatted for efficiency and clarity)
            for tool_call in tool_calls:
                result = tool_execution_results.get(tool_call.id, {})

                # Format result into structured summary (reduces tokens, improves synthesis)
                result_str = format_tool_result(tool_call.name, result)

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_call.name,
                    "content": result_str
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
        'hi', 'hello', 'hey', 'chat', 'test', 'testing', 'thanks', 'thank',
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
