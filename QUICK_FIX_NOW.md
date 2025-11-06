# ⚡ QUICK FIX - Get Agent Working NOW

**Problem**: Backend is healthy, but LLM provider (Cerebras) returns 503 errors
**Solution**: Test and switch to working LLM provider

---

## 🎯 5-Minute Fix (Copy-Paste Commands)

### Step 1: Find Your API Keys (30 seconds)

```bash
cd /home/phyrexian/Downloads/llm_automation/project_portfolio/Cite-Agent/cite-agent-api

# Check what keys you have
grep -i 'API_KEY\|GROQ\|CEREBRAS\|OPENAI' .env* 2>/dev/null | grep -v example
```

**Look for lines like:**
```
GROQ_API_KEY=gsk_...
CEREBRAS_API_KEY=csk_...
OPENAI_API_KEY=sk-...
```

### Step 2: Test Cerebras Key (1 minute)

```bash
# Replace YOUR_CEREBRAS_KEY with actual key from Step 1
curl -s -X POST https://api.cerebras.ai/v1/chat/completions \
  -H "Authorization: Bearer YOUR_CEREBRAS_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"gpt-oss-120b","messages":[{"role":"user","content":"test"}],"max_tokens":5}' 2>&1
```

**What you'll see:**
- ✅ **Working**: `{"id":"...", "choices":[{"message":{"content":"..."}}]}`
- ❌ **Invalid**: `{"error":"Invalid API key"}`
- ❌ **Rate Limited**: `{"error":"Rate limit exceeded"}`
- ❌ **Down**: `503 Service Unavailable` or timeout

### Step 3A: If Cerebras Works

```bash
# Just restart backend - it should work now
pkill -f "uvicorn src.main:app"

cd /home/phyrexian/Downloads/llm_automation/project_portfolio/Cite-Agent/cite-agent-api
nohup bash -c 'PYTHONPATH=/home/phyrexian/Downloads/llm_automation/project_portfolio/Cite-Agent:/home/phyrexian/Downloads/llm_automation/project_portfolio/Cite-Agent/cite-agent-api /home/phyrexian/Downloads/llm_automation/project_portfolio/Cite-Agent/.venv/bin/python -m uvicorn src.main:app --host 127.0.0.1 --port 8000' > /tmp/backend.log 2>&1 &

# Test it
sleep 3
python /home/phyrexian/Downloads/llm_automation/project_portfolio/Cite-Agent/test_debug_agent.py
```

### Step 3B: If Cerebras Fails - Switch to Groq

```bash
# Test Groq key first
curl -s -X POST https://api.groq.com/openai/v1/chat/completions \
  -H "Authorization: Bearer YOUR_GROQ_KEY" \
  -H "Content-Type: application/json" \
  -d '{"model":"llama-3.1-70b-versatile","messages":[{"role":"user","content":"test"}],"max_tokens":5}' 2>&1

# If that works, restart backend with Groq
pkill -f "uvicorn src.main:app"

cd /home/phyrexian/Downloads/llm_automation/project_portfolio/Cite-Agent/cite-agent-api
LLM_PROVIDER=groq GROQ_API_KEY=YOUR_GROQ_KEY nohup bash -c 'PYTHONPATH=/home/phyrexian/Downloads/llm_automation/project_portfolio/Cite-Agent:/home/phyrexian/Downloads/llm_automation/project_portfolio/Cite-Agent/cite-agent-api /home/phyrexian/Downloads/llm_automation/project_portfolio/Cite-Agent/.venv/bin/python -m uvicorn src.main:app --host 127.0.0.1 --port 8000' > /tmp/backend.log 2>&1 &
```

### Step 4: Verify It's Working (30 seconds)

```bash
# Test agent
cd /home/phyrexian/Downloads/llm_automation/project_portfolio/Cite-Agent
/home/phyrexian/Downloads/llm_automation/project_portfolio/Cite-Agent/.venv/bin/python test_debug_agent.py
```

**Expected output:**
```
🤖 AGENT RESPONSE:
I am a research assistant designed to help you with...
```

**NOT:**
```
💭 Thinking... (backend is busy, retrying automatically)
❌ Service unavailable
```

### Step 5: Run Full Intelligence Test (2 minutes)

```bash
cd /home/phyrexian/Downloads/llm_automation/project_portfolio/Cite-Agent
/home/phyrexian/Downloads/llm_automation/project_portfolio/Cite-Agent/.venv/bin/python test_agent_intelligence.py
```

This will run all 6 test scenarios and generate a report.

---

## 🆘 Still Not Working?

### Check Backend Logs

```bash
tail -50 /tmp/backend.log | grep -i error
```

### Watch Logs in Real-Time

```bash
# Terminal 1: Watch logs
tail -f /tmp/backend.log

# Terminal 2: Run test
cd /home/phyrexian/Downloads/llm_automation/project_portfolio/Cite-Agent
python test_debug_agent.py
```

Look for error messages like:
```
ERROR: Cerebras API returned 503
ERROR: Invalid API key
ERROR: Connection timeout
```

### Nuclear Option - Use Local Mode

Skip backend entirely and test agent directly:

```bash
cd /home/phyrexian/Downloads/llm_automation/project_portfolio/Cite-Agent

# Use Groq directly (no backend)
USE_LOCAL_KEYS=true GROQ_API_KEY=YOUR_KEY python test_agent_intelligence.py
```

---

## 📊 Expected Results After Fix

**Simple test:**
```bash
$ python test_debug_agent.py
🤖 Initializing agent...
✅ Agent initialized

📝 Question: What is your purpose and capabilities?
🤖 AGENT RESPONSE:
I am a research assistant designed to help you with academic research,
financial analysis, and file operations. I can search academic papers,
analyze company financials, and work with your local files.
```

**Full test:**
```bash
$ python test_agent_intelligence.py

================================================================================
🤖 AGENT INTELLIGENCE TEST - BETA LAUNCH VALIDATION
================================================================================

TEST: BASIC_UNDERSTANDING ━━━━━━━━━━━━━━━━━━━━━━━━━━ [3/3 questions]
✅ PASS - Agent demonstrates understanding of citation concepts

TEST: RESEARCH_CAPABILITY ━━━━━━━━━━━━━━━━━━━━━━━━━ [3/3 questions]
✅ PASS - Agent can search and analyze research papers

... (continues for 6 tests)

FINAL SCORE: 6/6 tests passed (100%)
✅ Agent is ready for beta launch!
```

---

## 🎯 Total Time Required

| Step | Time |
|------|------|
| Find API keys | 30 sec |
| Test Cerebras | 1 min |
| Switch to Groq (if needed) | 2 min |
| Verify working | 30 sec |
| Run full test | 2 min |
| **TOTAL** | **6 minutes** |

---

## 💡 Pro Tips

1. **Keep backend logs open** while testing:
   ```bash
   tail -f /tmp/backend.log | grep -E "error|ERROR|200|503"
   ```

2. **Test API keys BEFORE restarting backend** - saves time

3. **If both Cerebras and Groq fail**, you likely need to:
   - Request new API keys
   - Check if services are down (status.cerebras.ai)
   - Verify network connectivity

4. **Once working**, commit your .env.local config:
   ```bash
   # Don't commit secrets!
   # Just note which provider works for you
   echo "Working provider: groq" >> WORKING_CONFIG.txt
   ```

---

**Last Updated**: After test run showing Cerebras 503 errors
**Status**: Ready to execute - just need valid API key
