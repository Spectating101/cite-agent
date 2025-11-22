# Temporary API Key System - Fast Local Mode

## Overview

Cite-Agent uses a **temporary API key system** that allows authenticated users to run queries **locally** instead of routing through the backend. This provides:

- ⚡ **10x faster responses** (no backend roundtrip)
- 💰 **Lower backend costs** (reduced load)
- 🔒 **Still subscription-gated** (requires valid account)
- 🌐 **Works offline** (once key is issued)

## How It Works

### Architecture Flow

```
1. User logs in → Backend issues temp Cerebras key (14 days)
2. Client saves key to session.json
3. Client uses temp key for direct LLM calls (fast!)
4. Key expires → Falls back to backend mode
```

### Key Issuance (Backend)

**File:** `cite-agent-api/src/routes/auth.py` (lines 241-271)

When user logs in, backend:
1. Generates temp key using round-robin across 4 Cerebras keys
2. Sets expiration (14 days from login)
3. Returns in AuthResponse:
   ```json
   {
     "temp_api_key": "csk-xxxxx",
     "temp_key_expires": "2025-12-24T...",
     "temp_key_provider": "cerebras"
   }
   ```

### Key Storage (Client)

**File:** `cite_agent/auth.py` (lines 30-52)

Login response saved to `~/.nocturnal_archive/session.json`:
```json
{
  "email": "user@example.com",
  "user_id": "...",
  "access_token": "...",
  "temp_api_key": "csk-xxxxx",
  "temp_key_expires": "2025-12-24T...",
  "temp_key_provider": "cerebras"
}
```

### Key Usage (Client)

**File:** `cite_agent/enhanced_ai_agent.py` (lines 188-217)

On startup, client:
1. Reads `session.json`
2. Checks if `temp_api_key` exists and not expired
3. If valid → Sets `self.temp_api_key` and uses **local mode**
4. If expired/missing → Uses **backend mode**

## User Experience

### With Temp Key (Fast Mode)
```bash
$ cite-agent
✅ Using temporary local key (expires in 13.2h)

👤 You: test
🤖 Agent: [Instant response, 0-1s latency]
```

### Without Temp Key (Backend Mode)
```bash
$ cite-agent
⚙️ Using backend mode

👤 You: test
💭 Thinking... (backend is busy, retrying automatically)
🤖 Agent: [Slow response, 3-10s latency]
```

## Debugging

### Check if Temp Key Exists

```bash
# View session file
cat ~/.nocturnal_archive/session.json | python3 -m json.tool

# Look for these fields:
# - temp_api_key
# - temp_key_expires
# - temp_key_provider
```

### Enable Debug Mode

```bash
# See detailed key loading
export NOCTURNAL_DEBUG=1
cite-agent

# Look for these messages:
# ✅ Using temporary local key (expires in X.Xh)
# ⏰ Temporary key expired, using backend mode
# ⚠️ Error parsing temp key expiration: ...
```

### Force Re-Login to Get Fresh Key

```bash
# Clear session
rm ~/.nocturnal_archive/session.json

# Login again
cite-agent
# Choose option 3 (Logout), then login again
```

## Backend Requirements

For temp keys to work, backend must have Cerebras keys configured:

```bash
# Backend environment variables (Heroku)
CEREBRAS_API_KEY_1=csk-...
CEREBRAS_API_KEY_2=csk-...
CEREBRAS_API_KEY_3=csk-...
CEREBRAS_API_KEY_4=csk-...
```

Round-robin load balancing distributes users across 4 keys:
- User hash % 4 = key index (1-4)
- Prevents any single key from rate limiting

## Common Issues

### Issue 1: "backend is busy"
**Symptom:** Slow responses, queries hang
**Cause:** Temp key not in session.json or expired
**Fix:** Re-login to get fresh key

### Issue 2: Key not saved during login
**Symptom:** Backend mode even after fresh login
**Cause:** Backend not returning temp_api_key in response
**Fix:** Check backend env vars, deploy latest auth.py code

### Issue 3: Key expired
**Symptom:** Works for 14 days, then suddenly slow
**Cause:** Natural expiration (security measure)
**Fix:** Automatic - just re-login when prompted

## Security

- ✅ Keys expire after 14 days (automatic rotation)
- ✅ Keys stored locally with 600 permissions (owner only)
- ✅ Keys issued per-user (not shared)
- ✅ Still requires valid subscription (gated by login)
- ✅ Backend tracks usage even in local mode (via LLM provider logs)

## Performance Metrics

**Backend Mode:**
- Latency: 3-10 seconds
- Backend load: 100%
- Tokens: Backend quota

**Local Mode (Temp Key):**
- Latency: 0.5-2 seconds (10x faster)
- Backend load: 0% (only auth)
- Tokens: Cerebras quota

## ⚠️ CRITICAL: Tool Execution in Both Modes

**Added in v1.5.10** - This is a key architectural insight that caused bugs:

The agent has TWO SEPARATE code paths in `enhanced_ai_agent.py`:

### BACKEND MODE (lines ~6700-8100)
```
Condition: self.client is None
Flow: Query → Request Analysis → Tool Execution → call_backend_query() → Response
Tool execution: Lines 7565-7627 (data_analysis), etc.
```

### LOCAL MODE (lines ~8116-8700)
```
Condition: self.client is not None (temp_api_key loaded)
Flow: Query → Request Analysis → Tool Execution → Direct LLM Call → Response
Tool execution: Lines 8447-8510 (data_analysis), etc.
```

### The Bug That Was Fixed (v1.5.10)
- **Problem**: Data analysis tool execution only existed in BACKEND MODE
- **Symptom**: Follow-up queries like "which group did better?" failed 20% of the time in LOCAL MODE
- **Cause**: LOCAL MODE was missing the data_analysis block - `api_results["dataset_in_memory"]` was never populated
- **Fix**: Added complete data_analysis tool execution to LOCAL MODE

### Developer Rule
**When adding ANY new tool execution:**
1. Add to BACKEND MODE block (~line 7565)
2. Add to LOCAL MODE block (~line 8447)
3. Test BOTH modes separately

## ⚠️ Architecture Clarification (v1.5.10+)

**There is ONE execution mode** - direct Python code generation for analysis queries.

**What v1.5.10 fixed**:
1. **Dataset persistence** - DataAnalyzer (in tool_executor) now persists across queries ✅
2. **Anti-hallucination** - LLM code generation now includes loaded dataset context ✅
3. **Dataframe injection** - Generated code automatically has `df = pd.read_csv()` prepended ✅

**Common confusion**:
- `tool_executor` exists but does NOT control execution flow
- It's primarily a container for `_data_analyzer` to enable dataset persistence
- All analysis queries use the same code generation path (lines ~8198-8300)

If follow-up queries show "Dataset in memory: X rows" but return wrong numbers, check:
1. Is the dataset actually loaded? (Check `tool_executor._data_analyzer.current_dataset`)
2. Is the code generation including dataset context? (Should see sample data in prompt)
3. Is the dataframe injection working? (Check generated code has `df = pd.read_csv()` at top)

## Future Improvements

- [ ] Auto-refresh temp keys before expiration
- [ ] Client-side usage tracking
- [ ] Better error messages when key expires
- [ ] Support for multiple LLM providers (not just Cerebras)
- [ ] Telemetry: track local vs backend mode usage ratio
- [ ] Refactor: Consolidate tool execution to single location (DRY)
