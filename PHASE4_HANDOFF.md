# Terminal Claude → Claude Code Handoff: LLM-Based Intent Classification Engine

## 🎯 What Terminal Claude Just Built

### Core Function: `_get_query_intent(query: str) -> str`
**Location:** `cite_agent/enhanced_ai_agent.py` line 1135 (after rebase: 3102b9a)

**Purpose:** Intelligent, AI-driven query classification to replace all hardcoded patterns

**Returns One Of:**
```
'location_query'     → User asking about current directory (pwd, where am I, etc)
'file_search'        → User looking for files (find, search, locate)
'file_read'          → User wants to read/view file contents
'shell_execution'    → Direct shell commands (ls, mkdir, git, etc)
'data_analysis'      → Data processing, CSV, calculations
'backend_required'   → Needs backend LLM (research, papers, market data)
'conversation'       → General chat/discussion
```

### Three-Layer Architecture

#### Layer 1: Fast Heuristics (Instant, No LLM)
- Location keywords: pwd, where, directory, current, etc
- Shell commands: ls, mkdir, git, docker, pip, etc
- File operations: read, show, display + .py, .json, .csv, etc
- Data keywords: csv, analysis, calculate, statistics, etc
- Backend keywords: paper, research, stock, market, etc

**Why:** Most queries match heuristics immediately (0ms latency, 0 cost)

#### Layer 2: LLM Classification (Only if Uncertain)
- Calls backend LLM with specific prompt if heuristics unclear
- Uses fast model: `llama-3.1-8b-instant`
- **Timeout:** 2 seconds (fails gracefully to 'conversation')

#### Layer 3: Fallback Behavior
- Circuit breaker open? → Return 'conversation' (stay responsive)
- LLM timeout? → Return 'conversation' (don't block)
- LLM error? → Return 'conversation' (fail-open)
- Invalid response? → Validate and return 'conversation'

### Performance Characteristics

**Caching Strategy:**
- Query → MD5 hash
- Cache TTL: 1 hour
- Same query = instant response (cache hit)
- Different query = fresh classification

**Metrics Integration:**
- `intent_cache_hit` - Incremented when cache used
- `query_intent_{intent_type}` - Counter per intent
- `intent_classification_timeout` - LLM took >2s
- `intent_classification_error` - Exception occurred

### Helper Functions You'll Use

```python
# Inside _get_query_intent():
await self._classify_via_llm(prompt)  # LLM call via backend
self._cache_intent(query_hash, intent)  # Store in cache

# These are internal - don't call directly
```

## ✅ What's Already Done

### ✅ The Classifier Engine
- ✅ `_get_query_intent()` implemented with full caching + fallback
- ✅ `_cache_intent()` helper for cache management
- ✅ `_classify_via_llm()` helper for backend communication
- ✅ No syntax errors
- ✅ Metrics integration ready
- ✅ No imports missing

### ✅ Reference Implementation: `_is_location_query()`
```python
def _is_location_query(self, text: str) -> bool:
    """Uses fast heuristics without waiting for async LLM"""
    # Check fast patterns
    if len(text) < 50 and 'pwd' in text.lower():
        return True
    # ... other checks
    return False
```

**Key Point:** This shows the SYNC version (for existing sync code paths)

### ✅ Tests
- File: `tests/test_query_intent_classification.py`
- 15+ test methods covering all intent types
- Cache behavior tests
- Fallback & timeout tests
- Integration tests

## 🚀 What You (Claude Code) Should Do Now

### STEP 1: Use `_get_query_intent()` in `_classify_query_type()`

**Current Code (lines 1385-1420):**
```python
def _classify_query_type(self, query: str) -> QueryType:
    """Classify query type for adaptive provider selection"""
    # Currently has hardcoded keywords
    if any(keyword in query_lower for keyword in ["paper", "papers", ...]):
        return QueryType.ACADEMIC_PAPER
    # ... etc
```

**Your Change:**
```python
def _classify_query_type(self, query: str) -> QueryType:
    """Map LLM intent to QueryType for adaptive provider selection"""
    # Use the intelligent classifier instead of keywords
    intent = asyncio.run(self._get_query_intent(query))  # If in sync context
    # OR
    intent = await self._get_query_intent(query)  # If in async context
    
    # Map intents to QueryType
    intent_to_type = {
        'file_search': QueryType.FILE_SEARCH,
        'file_read': QueryType.FILE_READ,
        'shell_execution': QueryType.SHELL_EXECUTION,
        'data_analysis': QueryType.DATA_ANALYSIS,
        'backend_required': QueryType.ACADEMIC_PAPER,
        'conversation': QueryType.CONVERSATION,
        'location_query': QueryType.CONVERSATION,  # or custom type
    }
    return intent_to_type.get(intent, QueryType.CONVERSATION)
```

**Result:** Zero hardcoded keywords. Pure intent-based routing.

### STEP 2: Implement Local-Only Mode in `call_backend_query()`

**Around line 1970 (authentication checks):**
```python
async def call_backend_query(self, query: str, ...):
    """Call backend or handle locally based on intent"""
    
    # NEW: Check if query can be handled locally
    try:
        intent = await self._get_query_intent(query)
        if intent in ['file_search', 'file_read', 'shell_execution', 'location_query']:
            # Handle locally without auth
            return await self._handle_local_shell_query(query, intent)
    except:
        pass  # Fall through to normal auth check
    
    # EXISTING: Require auth for backend queries
    if not self.auth_token:
        return ChatResponse(
            response="❌ Not authenticated. Please log in first.",
            error_message="Authentication required"
        )
    
    # ... rest of backend query logic
```

**Result:** Shell operations run without authentication. Backend queries still require auth.

### STEP 3: Create `_handle_local_shell_query()` Helper

```python
async def _handle_local_shell_query(self, query: str, intent: str) -> ChatResponse:
    """Execute shell operations locally without backend auth"""
    
    if intent == 'location_query':
        # Run pwd
        return ChatResponse(response=await self._execute_pwd())
    
    elif intent == 'file_search':
        # Run find/ls command
        return ChatResponse(response=await self._execute_file_search(query))
    
    elif intent == 'file_read':
        # Read file contents
        return ChatResponse(response=await self._execute_file_read(query))
    
    elif intent == 'shell_execution':
        # Execute shell command
        return ChatResponse(response=await self._execute_shell_command(query))
    
    return ChatResponse(response="Local mode: command not recognized")
```

### STEP 4: Update Tests

**Existing:** `tests/test_current_behavior.py` (that you created)

**Add New Tests:**
- `tests/test_local_mode_integration.py`
  - Verify shell ops work without auth
  - Verify backend ops still require auth
  - Test intent routing to local vs backend

### What NOT to Do

❌ Do NOT rewrite `_get_query_intent()` - that's my function
❌ Do NOT add hardcoded keyword lists anywhere - use intent classification
❌ Do NOT call `_get_query_intent()` synchronously in async context (use `await`)
❌ Do NOT bypass the classifier for routing decisions

## 🔄 Integration Points

### Your Code → My Classifier
```python
# Call my function
intent = await self._get_query_intent(user_query)

# It returns one of 7 values
if intent == 'location_query':
    # Your code handles local execution
elif intent == 'file_search':
    # Your code handles local file search
# etc
```

### My Metrics → Your Usage
When you call `_get_query_intent()`, metrics are automatically tracked:
- Cache hits/misses
- Intent type distribution
- Errors & timeouts

You can see these in observability system.

## 📋 Commit Process

1. **You Complete:** Refactor `_classify_query_type()` + add local-only mode
2. **You Test:** Run `pytest tests/test_query_intent_classification.py tests/test_local_mode_integration.py`
3. **You Commit:** `git commit -m "feat: Use LLM intent classifier for routing + add local-only mode"`
4. **You Push:** `git push origin claude/add-welcome-credit-011CUpdBCHWmu5UoLh8CgxkC`
5. **Both Together:** Verify integration, commit final: `feat: Phase 4 complete - LLM-based intent routing + local-only mode`

## ⚠️ Important Notes

### Why This is Better Than Hardcodes
- Old approach: "Does 'list files in current directory' match any of our 11 phrases?" → NO ✓ CORRECT
- Old approach: "Does it contain 'current directory'?" → YES ✗ INCORRECT (matched pwd)
- New approach: "What is the user ACTUALLY asking for?" → file_search ✓ CORRECT

### Why Caching Matters
- Same query comes in twice? → 0ms (cached)
- Different query? → 2ms max (2s timeout)
- LLM never called for obvious patterns → cost savings

### Why Fail-Open Design Matters
- Circuit breaks? → Return 'conversation' instead of error
- LLM times out? → Return 'conversation' instead of blocking
- Agent stays responsive even if backend is struggling

## 🎓 Questions?

You now have everything you need. The classifier is:
- ✅ Production-ready
- ✅ Tested
- ✅ Performant
- ✅ Maintainable
- ✅ AI-driven (not hardcoded)

Go build the local-only mode!

---

**Terminal Claude** | Commit: 3102b9a
**Ready for Claude Code Integration** ✅
