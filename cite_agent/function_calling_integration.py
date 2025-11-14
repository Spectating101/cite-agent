"""
Integration patch for function calling in EnhancedNocturnalAgent.

This module adds the process_request_with_function_calling method
that should be added to enhanced_ai_agent.py
"""

async def process_request_with_function_calling(self, request: ChatRequest) -> ChatResponse:
    """
    Process request using function calling (local mode only).

    This is the NEW path that uses Cerebras/OpenAI function calling API
    instead of keyword matching.

    Workflow:
    1. Check for workflow commands
    2. Call LLM with function calling to determine what tools to use
    3. Execute requested tools
    4. Get final response from LLM with tool results

    NOTE: ALL queries go through function calling. No hardcoded bypasses.
    The LLM intelligently chooses the 'chat' tool for simple greetings.
    """
    from .function_calling import FunctionCallingAgent
    from .tool_executor import ToolExecutor
    import os

    debug_mode = os.getenv("NOCTURNAL_DEBUG", "").lower() == "1"

    try:
        # Check workflow commands first
        workflow_response = await self._handle_workflow_commands(request)
        if workflow_response:
            return workflow_response

        # ALL queries go through function calling - no hardcoded bypasses

        # Initialize function calling agent
        if not hasattr(self, '_function_calling_agent'):
            self._function_calling_agent = FunctionCallingAgent(
                client=self.client,
                model=self._get_model_name(),
                provider=self.llm_provider
            )

        # Initialize tool executor
        if not hasattr(self, '_tool_executor'):
            self._tool_executor = ToolExecutor(agent=self)

        if debug_mode:
            print(f"🔍 [Function Calling] Processing query: {request.question[:100]}...")

        # Step 1: Get tool calls from LLM
        fc_response = await self._function_calling_agent.process_query(
            query=request.question,
            conversation_history=self.conversation_history[-10:] if hasattr(self, 'conversation_history') else []
        )

        # If no tool calls, return direct response
        if not fc_response.tool_calls:
            if debug_mode:
                print(f"🔍 [Function Calling] Direct response (no tools)")

            # Update conversation history
            if hasattr(self, 'conversation_history'):
                self.conversation_history.append({
                    "role": "user",
                    "content": request.question
                })
                self.conversation_history.append({
                    "role": "assistant",
                    "content": fc_response.response
                })

            return ChatResponse(
                response=fc_response.response,
                tokens_used=fc_response.tokens_used,
                tools_used=["chat"],
                confidence_score=0.8,
                api_results={}
            )

        # Step 2: Execute tools
        if debug_mode:
            print(f"🔍 [Function Calling] Executing {len(fc_response.tool_calls)} tool(s)")

        tool_execution_results = {}
        tools_used = []

        for tool_call in fc_response.tool_calls:
            result = await self._tool_executor.execute_tool(
                tool_name=tool_call.name,
                arguments=tool_call.arguments
            )
            tool_execution_results[tool_call.id] = result
            tools_used.append(tool_call.name)

            if debug_mode:
                print(f"🔍 [Function Calling] Tool {tool_call.name} executed: "
                      f"{'error' if 'error' in result else 'success'}")

        # Step 3: Get final response from LLM with tool results
        if debug_mode:
            print(f"🔍 [Function Calling] Getting final response with tool results")

        # Build conversation for finalize
        conversation = []
        if hasattr(self, 'conversation_history'):
            conversation = self.conversation_history[-10:].copy()
        conversation.append({
            "role": "user",
            "content": request.question
        })

        final_response = await self._function_calling_agent.finalize_response(
            original_query=request.question,
            conversation_history=conversation,
            tool_calls=fc_response.tool_calls,
            tool_execution_results=tool_execution_results
        )

        # Update conversation history
        if hasattr(self, 'conversation_history'):
            self.conversation_history.append({
                "role": "user",
                "content": request.question
            })
            self.conversation_history.append({
                "role": "assistant",
                "content": final_response.response
            })

        if debug_mode:
            print(f"🔍 [Function Calling] Final response: {final_response.response[:100]}...")

        return ChatResponse(
            response=final_response.response,
            tokens_used=fc_response.tokens_used + final_response.tokens_used,
            tools_used=tools_used,
            confidence_score=0.85,
            api_results=tool_execution_results
        )

    except Exception as e:
        if debug_mode:
            print(f"❌ [Function Calling] Error: {e}")
            import traceback
            traceback.print_exc()

        # Fallback to error response
        return ChatResponse(
            response=f"I encountered an error processing your request: {str(e)}",
            error_message=str(e),
            tokens_used=0,
            tools_used=["error"],
            confidence_score=0.0,
            api_results={}
        )


def _get_model_name(self) -> str:
    """Get the appropriate model name for the current provider"""
    if self.llm_provider == "cerebras":
        return "gpt-oss-120b"
    elif self.llm_provider == "groq":
        return "llama-3.1-70b-versatile"
    else:
        return "gpt-4o-mini"  # Fallback
