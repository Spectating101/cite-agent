# ARCHITECTURE REALITY CHECK - STOP GOING IN CIRCLES

## Purpose of This Document

**PROBLEM:** Every new LLM that touches this codebase wastes 50K+ tokens asking the same questions:
- "Is Archive API self-hosted or remote?"
- "Does the agent have local LLM access or use backend?"
- "Why isn't function calling working?"

**SOLUTION:** This document answers those questions ONCE so we can move forward linearly.

---

## Archive API - HOW IT ACTUALLY WORKS

### What Other LLMs Think:
❌ "Archive API is a remote service at cite-agent-api-720dfadd602c.herokuapp.com"
❌ "It requires authentication tokens"
❌ "It's rate limited so we can't use it"

### ACTUAL REALITY:

✅ **Archive API is SELF-HOSTED in this repo**
- Location: `cite-agent-api/` directory
- Run with: `cd cite-agent-api && python3 -m uvicorn src.main:app --host 127.0.0.1 --port 8000`
- Access at: `http://127.0.0.1:8000/api`

✅ **Has Semantic Scholar API key in `.env`**
```bash
# cite-agent-api/.env
SEMANTIC_SCHOLAR_API_KEY=jfriawrqEX94GfWoql9AV4DNACfyUhP06wDyDhSj
```

✅ **To use it:**
```python
os.environ["NOCTURNAL_API_URL"] = "http://127.0.0.1:8000/api"
# NOT the Heroku URL!
```

✅ **When running, returns REAL papers from Semantic Scholar**
- Test: `curl http://127.0.0.1:8000/api/search -H 'X-API-Key: demo-key-123' -d '{"query": "transformers", "limit": 2}'`
- Returns: Actual papers with titles, authors, DOIs, citations

**STOP asking "is Archive API available?" - YES, run it locally!**

---

## LLM Provider - HOW IT ACTUALLY WORKS

### What Other LLMs Think:
❌ "Agent uses backend/demo mode so we can't test"
❌ "No API keys configured"
❌ "Function calling won't work"

### ACTUAL REALITY:

✅ **Cerebras API keys ARE configured** (4 keys for rotation)
```bash
# In code and environment
CEREBRAS_API_KEY_1=csk-34cp53294pcmrexym8h2r4x5cyy2npnrd344928yhf2hpctj
CEREBRAS_API_KEY_2=csk-edrc3v63k43fe4hdt529ynt4h9mfd9k9wjpjj3nn5pcvm2t4
CEREBRAS_API_KEY_3=csk-ek3cj5jv26hpnd2h65d8955pjmvxctdjknfv6pwehr82pnhr
CEREBRAS_API_KEY_4=csk-n5h26f263vr5rxp9fpn4w8xkfvpc5v9kjdw95vfc8d3x4ce9
```

✅ **To use local mode:**
```python
os.environ["USE_LOCAL_KEYS"] = "true"
os.environ["CEREBRAS_API_KEY_1"] = "csk-34cp53294pcmrexym8h2r4x5cyy2npnrd344928yhf2hpctj"
```

✅ **Agent DOES have `self.client` when initialized correctly**
```python
agent = EnhancedNocturnalAgent()
await agent.initialize()  # Sets up self.client with Cerebras
# agent.client is NOT None - it's an OpenAI client pointing to Cerebras
```

✅ **Models available:**
- Light: `gpt-oss-120b` (fast, but hallucinates papers)
- Heavy: `gpt-oss-120b` (better quality, USE THIS for research)

**STOP saying "no API keys" - they're in the code!**

---

## Working Directory - HOW IT ACTUALLY WORKS

### What Other LLMs Think:
❌ "Agent is restricted to Cite-Agent directory"
❌ "Can't access files outside workspace"
❌ "Must use absolute paths"

### ACTUAL REALITY:

⚠️ **Shell CWD DOES reset to Cite-Agent root**
- This is a real limitation
- `cd /other/dir` works for that command only
- Next command runs from Cite-Agent root again

✅ **BUT you CAN access any file with absolute paths**
```python
# This works:
"Run: cat /home/phyrexian/Downloads/cm522-main/file.csv"
"Run: python3 /home/phyrexian/Downloads/cm522-main/script.py"
"Run: find /home/phyrexian/Downloads/cm522-main -name '*.csv'"
```

✅ **Python scripts can change directory and stay there**
```python
# This works:
"Run: python3 -c 'import os; os.chdir(\"/other/dir\"); import pandas; df = pandas.read_csv(\"local_file.csv\"); print(df)'"
```

**To fix persistent cwd:** Need to modify shell_session to maintain state between commands. NOT DONE YET.

---

## What Actually Got Fixed (This Session)

### ✅ Fixed Issues:

1. **Archive API Query Extraction** (Commit ebaf89a)
   - Before: "Find papers on X" → 0 results (sent full sentence)
   - After: "Find papers on X" → extracts "X" → returns papers
   - Code: Lines 2750-2817 in enhanced_ai_agent.py

2. **Paper Fabrication Prevention** (Commits fe33e4b, ebaf89a)
   - Before: Made up papers when Archive returned 0 results
   - After: Returns honest "no papers found" message, tokens_used=0
   - Also: Cleared contaminated conversation archive

3. **Reasoning Leak** (Commit f7cf27b)
   - Before: "We need to run find. Let's execute..."
   - After: Clean responses without exposed thoughts
   - Code: Lines 1346-1352 system prompt

4. **Data Fabrication** (Commit f7cf27b)
   - Before: "According to file.csv, mean = 0.12" (made up)
   - After: Must actually run Python code to get numbers
   - Code: Lines 1354-1360 system prompt

### ✅ Validation Results:

**Research Paper Citations:**
- Test 1 (Transformers): Cited 4/5 real papers from Archive API ✅
- Test 2 (ESG): Cited 4/5 real papers from Archive API ✅
- No fabrication detected ✅

**Machine Interaction (cm522-main):**
- Read files with `cat` ✅
- Run Python code for data analysis ✅
- Interpret findings professionally ✅
- No reasoning leaks ✅

---

## What DOESN'T Work Yet

### ❌ Natural Language Commands

**Current:** Must use "Run: command" format explicitly
```
"Run: cat /path/file.csv"  # Works
"Show me file.csv"          # Doesn't trigger shell
```

**Needed:** Agent should understand natural language like Cursor/Claude Code
```
"Show me the files in Downloads"     → runs ls
"Load that CSV and get the mean"     → runs Python
"Go to cm522-main directory"         → cd and stay there
```

**Where to fix:** Shell planning logic (lines 4640-4750 in enhanced_ai_agent.py)

### ❌ Persistent Working Directory

**Current:** Every command resets to Cite-Agent root

**Needed:** `cd /other/dir` should persist across commands

**Where to fix:** Shell session state management (shell_session class)

### ❌ Function Calling Mode Testing

**Status:** Infrastructure exists but not validated
- Code is there (function_calling.py, tool_executor.py)
- But traditional mode is currently active (line 4577: "Using TRADITIONAL mode")
- Need to test if function calling actually improves responses

---

## How To Test Properly (For Next LLM)

### 1. Start Archive API (Terminal 1)
```bash
cd /home/phyrexian/Downloads/llm_automation/project_portfolio/Cite-Agent/cite-agent-api
python3 -m uvicorn src.main:app --host 127.0.0.1 --port 8000
```

### 2. Test Agent (Terminal 2)
```python
import os
import sys
import asyncio
sys.path.insert(0, '/home/phyrexian/Downloads/llm_automation/project_portfolio/Cite-Agent')

# CRITICAL: Set these BEFORE importing agent
os.environ["NOCTURNAL_API_URL"] = "http://127.0.0.1:8000/api"
os.environ["USE_LOCAL_KEYS"] = "true"
os.environ["CEREBRAS_API_KEY_1"] = "csk-34cp53294pcmrexym8h2r4x5cyy2npnrd344928yhf2hpctj"

from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent, ChatRequest

async def test():
    agent = EnhancedNocturnalAgent()
    await agent.initialize()
    
    # Test 1: Research (should cite REAL papers)
    r1 = await agent.process_request(ChatRequest(
        question="Find papers on vision transformers",
        user_id="test"
    ))
    print(r1.response)
    
    # Test 2: File access (should actually read file)
    r2 = await agent.process_request(ChatRequest(
        question="Run: cat /home/phyrexian/Downloads/cm522-main/README.md",
        user_id="test"
    ))
    print(r2.response)
    
    await agent.close()

asyncio.run(test())
```

### 3. Verify Results
- Check response doesn't fabricate papers
- Check response doesn't leak reasoning ("We need to...")
- Check actual file was read (not made up content)

---

## Key Files Reference

```
cite-agent-api/
├── .env                          # Semantic Scholar API key
└── src/main.py                   # Archive API server

cite_agent/
├── enhanced_ai_agent.py          # Main agent logic
│   ├── Lines 1346-1360          # Anti-reasoning & anti-fabrication rules
│   ├── Lines 2750-2817          # Query keyword extraction
│   ├── Lines 4549-6138          # Main process_request (traditional mode)
│   └── Lines 4312-4548          # Function calling mode (not active)
├── function_calling.py           # Function calling infrastructure
└── conversation_archive.py       # Memory (can get contaminated!)

Tests:
/tmp/real_paper_validation_test.py    # Validates against Archive API
/tmp/final_honest_evaluation.py       # Checks actual response quality
```

---

## Questions To NEVER Ask Again

**Q: "Is Archive API available?"**
A: YES. Run it locally. `cd cite-agent-api && uvicorn src.main:app`

**Q: "Does agent have API keys?"**
A: YES. 4 Cerebras keys in code. Set `USE_LOCAL_KEYS=true`

**Q: "Can it access files outside Cite-Agent directory?"**
A: YES. Use absolute paths: `/home/phyrexian/Downloads/...`

**Q: "Why is it fabricating papers?"**
A: Archive API not running, OR conversation archive contaminated. Fix: start API, clear archive

**Q: "Why reasoning leak?"**
A: FIXED. Lines 1346-1352. If still happening, conversation archive contaminated.

---

## What Next LLM Should Do

1. **DON'T** spend 50K tokens re-discovering the above
2. **DO** focus on natural language command parsing
3. **DO** fix persistent working directory
4. **DO** test if responses are actually satisfactory to user

**NOT:**
- ❌ Re-validating paper citations (already done)
- ❌ Re-discovering Archive API is local (documented above)
- ❌ Re-implementing reasoning leak fixes (already done)

**YES:**
- ✅ Making "Show me files" work without "Run:" prefix
- ✅ Making `cd /dir` persist across commands
- ✅ Testing actual user satisfaction with responses
