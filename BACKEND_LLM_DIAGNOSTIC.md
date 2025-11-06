# 🔍 Backend LLM Provider Diagnostic

**Status**: Backend API is healthy, but LLM provider is failing

## Test Results Summary

```
✅ Backend API: Running (127.0.0.1:8000)
✅ Health Check: Passing (/readyz returns 200 OK)
❌ LLM Queries: Failing (503 Service Unavailable)
```

## What's Happening

From the test output:
```
💭 Thinking... (backend is busy, retrying automatically)
❌ Service unavailable. Please try again in a few minutes.
```

This means:
1. Agent successfully connects to backend
2. Backend receives the query
3. **Backend fails to call LLM provider** (Cerebras/Groq)
4. Returns 503 error after exhausting retries

## Root Cause Options

### Option 1: Cerebras API Key Issue (Most Likely)
```
- Invalid/expired API key
- Rate limit exceeded
- Cerebras service temporarily down
```

### Option 2: Network/Connectivity Issue
```
- Firewall blocking outbound HTTPS
- DNS resolution failing
- Proxy configuration needed
```

### Option 3: Missing Configuration
```
- LLM provider not configured in backend
- API keys not loaded from environment
- Wrong model name specified
```

## 🔧 Immediate Fix Options

### Fix #1: Switch to Groq (Fastest)

Groq has better reliability than Cerebras. To switch:

**1. Check if you have Groq API key:**
```bash
grep -i groq /home/phyrexian/Downloads/llm_automation/project_portfolio/Cite-Agent/cite-agent-api/.env.local 2>/dev/null || echo "No .env.local found"
```

**2. If you have Groq key, set it as primary:**
```bash
# In cite-agent-api/.env.local or export in shell
export GROQ_API_KEY="your_groq_key_here"
export LLM_PROVIDER="groq"  # Force Groq instead of Cerebras
```

**3. Restart backend:**
```bash
# Kill existing backend
pkill -f "uvicorn src.main:app"

# Restart with Groq
cd /home/phyrexian/Downloads/llm_automation/project_portfolio/Cite-Agent/cite-agent-api
GROQ_API_KEY="your_key" LLM_PROVIDER="groq" nohup bash -c 'PYTHONPATH=/home/phyrexian/Downloads/llm_automation/project_portfolio/Cite-Agent:/home/phyrexian/Downloads/llm_automation/project_portfolio/Cite-Agent/cite-agent-api /home/phyrexian/Downloads/llm_automation/project_portfolio/Cite-Agent/.venv/bin/python -m uvicorn src.main:app --host 127.0.0.1 --port 8000' > /tmp/backend.log 2>&1 &
```

### Fix #2: Test Cerebras API Key Directly

**1. Test Cerebras API manually:**
```bash
curl -X POST https://api.cerebras.ai/v1/chat/completions \
  -H "Authorization: Bearer YOUR_CEREBRAS_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-oss-120b",
    "messages": [{"role": "user", "content": "test"}],
    "max_tokens": 10
  }'
```

**Expected responses:**
- ✅ Success: `{"id":"...", "choices":[...]}`
- ❌ Invalid key: `{"error": {"message": "Invalid API key"}}`
- ❌ Rate limit: `{"error": {"message": "Rate limit exceeded"}}`
- ❌ Service down: `503 Service Unavailable`

### Fix #3: Check Backend Logs for Actual Error

**1. View backend logs in real-time:**
```bash
tail -f /tmp/backend.log | grep -E "error|ERROR|503|cerebras|groq"
```

**2. Make a test query:**
```bash
# In another terminal
python test_debug_agent.py
```

**3. Look for error lines like:**
```
ERROR: Cerebras API returned 503
ERROR: Invalid API key
ERROR: Rate limit exceeded
```

### Fix #4: Use Local LLM Mode (Bypass Backend)

If you want to test agent logic WITHOUT backend LLM:

**1. Set local mode:**
```bash
export USE_LOCAL_KEYS="true"
export GROQ_API_KEY="your_groq_key"
```

**2. Run agent tests:**
```bash
USE_LOCAL_KEYS=true GROQ_API_KEY="your_key" python test_agent_intelligence.py
```

This bypasses the backend entirely and uses Groq directly from the agent.

## 🎯 Recommended Action Order

1. **Check which API keys you have** (5 min)
   ```bash
   ls -la /home/phyrexian/Downloads/llm_automation/project_portfolio/Cite-Agent/cite-agent-api/.env*
   grep -i 'groq\|cerebras\|openai' /home/phyrexian/Downloads/llm_automation/project_portfolio/Cite-Agent/cite-agent-api/.env* 2>/dev/null
   ```

2. **Test API key directly** (5 min)
   - Use curl command from Fix #2 above
   - This will tell you EXACTLY what's wrong

3. **Check backend logs during query** (5 min)
   - Run `tail -f /tmp/backend.log`
   - Run test query in another terminal
   - Look for actual error message

4. **Switch to working provider** (10 min)
   - If Cerebras is down → Use Groq
   - If both down → Use OpenAI (slower but reliable)
   - If no keys work → Request new keys

## Expected Timeline

- **Diagnosis**: 10-15 minutes
- **Fix (if have valid key)**: 5 minutes
- **Fix (if need new key)**: 30-60 minutes
- **Total**: 15-75 minutes depending on key availability

## After Fix - Verify Working

```bash
# 1. Backend should respond to /query endpoint
curl -X POST http://127.0.0.1:8000/v1/query/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_AUTH_TOKEN" \
  -d '{
    "query": "What is 2+2?",
    "model": "openai/gpt-oss-120b"
  }'

# Expected: {"response": "4", "tokens_used": ...}

# 2. Agent test should work
python test_agent_intelligence.py
```

## 📞 Need Help?

If you've tried all fixes and still stuck:

1. **Share these logs:**
   ```bash
   tail -100 /tmp/backend.log > backend_error.log
   cat backend_error.log
   ```

2. **Share API key test result:**
   ```bash
   # Test Cerebras
   curl -X POST https://api.cerebras.ai/v1/chat/completions \
     -H "Authorization: Bearer YOUR_KEY" \
     -H "Content-Type: application/json" \
     -d '{"model": "gpt-oss-120b", "messages": [{"role": "user", "content": "test"}]}' 2>&1
   ```

3. **Share backend health response:**
   ```bash
   curl -v http://127.0.0.1:8000/readyz 2>&1
   ```

With these three outputs, the exact problem will be obvious.
