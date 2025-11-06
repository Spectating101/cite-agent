# 🚀 Quick Start - Running Comprehensive Tests

## TL;DR (30 seconds)

```bash
cd /home/user/cite-agent

# Option 1: Using backend (requires auth setup)
python test_comprehensive_agent.py

# Option 2: Using direct API keys (bypass backend)
USE_LOCAL_KEYS=true CEREBRAS_API_KEY=csk_xxx python test_comprehensive_agent.py
```

---

## Prerequisites

### Option A: Backend Mode (Full Production Test)

**Requirements:**
1. ✅ Backend API running (127.0.0.1:8000)
2. ✅ PostgreSQL database set up
3. ✅ User registered with auth token
4. ✅ Auth token in `~/.nocturnal_archive/session.json`

**Setup Steps:**
```bash
# 1. Start backend
cd cite-agent-api
nohup python -m uvicorn src.main:app --host 127.0.0.1 --port 8000 &

# 2. Register user (if not done)
curl -X POST http://127.0.0.1:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "you@university.edu", "password": "yourpass"}'

# 3. Save auth token
mkdir -p ~/.nocturnal_archive
echo '{"auth_token": "YOUR_TOKEN", "account_id": "YOUR_ID"}' > ~/.nocturnal_archive/session.json

# 4. Run tests
cd /home/user/cite-agent
python test_comprehensive_agent.py
```

### Option B: Direct API Mode (Quick Test)

**Requirements:**
1. ✅ Cerebras or Groq API key

**Setup Steps:**
```bash
cd /home/user/cite-agent

# With Cerebras
USE_LOCAL_KEYS=true CEREBRAS_API_KEY=csk_your_key_here python test_comprehensive_agent.py

# With Groq
USE_LOCAL_KEYS=true GROQ_API_KEY=gsk_your_key_here python test_comprehensive_agent.py

# With both (Groq as fallback)
USE_LOCAL_KEYS=true \
  CEREBRAS_API_KEY=csk_xxx \
  GROQ_API_KEY=gsk_xxx \
  python test_comprehensive_agent.py
```

**Pros:**
- ✅ Faster setup (no database needed)
- ✅ Direct LLM testing (proves API works)
- ✅ Good for development

**Cons:**
- ❌ Doesn't test backend auth flow
- ❌ Doesn't test database integration
- ❌ Not the full production path

---

## Running Tests

### Full Test Suite (15 categories, ~100 tests)

```bash
python test_comprehensive_agent.py
```

**Expected runtime**: 15-30 minutes
**Expected pass rate**: 80-90%

### Run Specific Categories

Edit `test_comprehensive_agent.py` and comment out categories you don't want:

```python
test_categories = [
    self.test_basic_conversation,        # Quick (5 tests, 1 min)
    # self.test_academic_research,       # Slow (5 tests, 3 min)
    # self.test_financial_analysis,      # Slow (5 tests, 3 min)
    self.test_file_operations,           # Fast (7 tests, 2 min)
    # ...
]
```

### Quick Smoke Test (Basic Features Only)

```python
# In test_comprehensive_agent.py, keep only:
test_categories = [
    self.test_basic_conversation,
    self.test_file_operations,
    self.test_command_safety,
]
```

**Runtime**: ~5 minutes
**Tests**: ~20

---

## Understanding Test Output

### Real-Time Progress

```
🧪 COMPREHENSIVE AGENT TEST SUITE
================================================================================

🔧 Initializing comprehensive test environment...
   Test directory: /tmp/agent_test_abc123
   Created 5 test files
✅ Test environment ready

📋 Category 1: Basic Conversation & Understanding
   ✅ Basic: Greeting (0.45s)
   ✅ Basic: Self-description (1.23s)
   ✅ Basic: Capabilities (1.56s)
   ✅ Basic: Citation formats (2.34s)
   ✅ Basic: Thanks (0.38s)

📚 Category 2: Academic Research (Archive API)
   ✅ Research: Basic paper search (3.45s)
   ✅ Research: Specific topic search (4.23s)
   ❌ Research: Author search (5.67s)
      Error: Archive API timeout
   ...
```

### Final Summary

```
================================================================================
📊 COMPREHENSIVE TEST SUMMARY
================================================================================

✨ Overall Results:
   Total Tests: 97
   Passed: 82 ✅
   Failed: 15 ❌
   Pass Rate: 84.5%
   Avg Duration: 2.34s
   Max Duration: 8.92s

📋 Results by Category:
   ✅ Basic Conversation: 5/5 (100%)
   ✅ File Operations: 7/7 (100%)
   ⚠️  Academic Research: 4/5 (80%)
   ⚠️  Multi-Turn Context: 9/12 (75%)
   ❌ Web Search: 1/3 (33%)

❌ Failed Tests:
   • Research: Author search
     Error: Archive API timeout after 30s
   • Web: Current events
     Error: Web search not configured
   ...

================================================================================
✅ AGENT IS READY with minor issues to address
================================================================================
```

---

## Interpreting Results

### ✅ **90-100% Pass Rate**
```
🎉 ALL TESTS PASSED! Agent is ready for beta launch!
```

**What this means:**
- Core features work perfectly
- Edge cases handled well
- Context retention works
- Error recovery works
- Security verified

**Action**: Launch beta with confidence

---

### ✅ **75-89% Pass Rate**
```
✅ AGENT IS READY with minor issues to address
```

**What this means:**
- Core features work
- Some edge cases fail
- Multi-turn context may have gaps
- Some API integrations flaky

**Action**: Review failed tests, fix critical ones, launch beta

**Typical issues:**
- Archive/FinSight API timeouts (not agent's fault)
- Web search disabled (acceptable if not core feature)
- Some context resolution failures (improve over time)

---

### ⚠️ **60-74% Pass Rate**
```
⚠️  AGENT NEEDS WORK before beta launch
```

**What this means:**
- Core features mostly work
- Many edge cases fail
- Context retention weak
- Error handling incomplete

**Action**: Fix critical issues before launching

**Focus on:**
1. Basic conversation must work (95%+)
2. File operations must work (90%+)
3. Command safety must work (95%+)
4. Error handling must work (85%+)

---

### ❌ **<60% Pass Rate**
```
❌ AGENT NOT READY - significant issues found
```

**What this means:**
- Core features broken
- Many crashes or timeouts
- Context not working
- Security concerns

**Action**: Do NOT launch. Debug thoroughly.

**Common causes:**
1. Backend not running
2. LLM API keys invalid
3. Database not configured
4. Network connectivity issues

---

## Debugging Failed Tests

### Step 1: Check What Failed

Look at the "Failed Tests" section in output:

```
❌ Failed Tests:
   • Research: Author search
     Error: Archive API timeout after 30s
```

### Step 2: Check Detailed Report

```bash
cat COMPREHENSIVE_TEST_REPORT.json | jq '.failed_tests'
```

Output:
```json
[
  {
    "name": "Research: Author search",
    "category": "Academic Research",
    "error": "Archive API timeout after 30s",
    "details": {
      "api_results": {},
      "tools_used": ["archive_api"],
      "exception": "TimeoutError"
    }
  }
]
```

### Step 3: Test Isolated Component

```python
# Test Archive API directly
from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent
import asyncio

async def test():
    agent = EnhancedNocturnalAgent()
    await agent.initialize()

    result = await agent.search_academic_papers("machine learning", limit=3)
    print(result)

    await agent.close()

asyncio.run(test())
```

### Step 4: Check Logs

```bash
# If using backend
tail -100 /tmp/backend.log | grep -i error

# If using direct keys
NOCTURNAL_DEBUG=1 python test_comprehensive_agent.py 2>&1 | tee debug.log
```

---

## Common Issues & Fixes

### Issue 1: "Authentication required"

**Error:**
```
❌ Backend error (HTTP 401): Authentication required
```

**Fix:**
```bash
# Register user and save token
curl -X POST http://127.0.0.1:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "you@university.edu", "password": "pass"}'

# Save token to session.json
mkdir -p ~/.nocturnal_archive
echo '{"auth_token": "token_here", "account_id": "id_here"}' > ~/.nocturnal_archive/session.json
```

### Issue 2: "Archive API timeout"

**Error:**
```
❌ Research: Basic paper search
   Error: Archive API timeout after 30s
```

**Cause:** Archive API is slow or down

**Fix:**
```bash
# Test Archive API health
curl -s http://127.0.0.1:8000/api/health

# Increase timeout (in enhanced_ai_agent.py)
async with self.session.post(url, timeout=60) as response:  # Was 30
```

### Issue 3: "Web search not configured"

**Error:**
```
❌ Web: Current events
   Error: Web search not configured
```

**Cause:** Web search module missing or disabled

**Fix:**
- This is acceptable if web search is not a core feature
- Or configure web search API keys

### Issue 4: "Backend not running"

**Error:**
```
❌ Error: HTTP session not initialized
```

**Cause:** Backend API not running

**Fix:**
```bash
# Start backend
cd cite-agent-api
python -m uvicorn src.main:app --host 127.0.0.1 --port 8000

# Verify it's up
curl http://127.0.0.1:8000/readyz
```

### Issue 5: Tests hang forever

**Cause:** Timeout not configured or too long

**Fix:**
```bash
# Kill hanging test
pkill -f test_comprehensive_agent

# Run with shorter timeout
timeout 600 python test_comprehensive_agent.py  # 10 minute max
```

---

## Performance Benchmarks

Expected test durations:

| Category | Tests | Expected Time |
|----------|-------|---------------|
| Basic Conversation | 5 | 1-2 min |
| Academic Research | 5 | 3-5 min |
| Financial Analysis | 5 | 3-5 min |
| File Operations | 7 | 1-2 min |
| Directory Exploration | 5 | 1-2 min |
| Code Analysis | 4 | 2-3 min |
| Web Search | 3 | 2-4 min |
| Multi-Turn Context | 12 | 5-8 min |
| Command Safety | 4 | 1-2 min |
| Error Handling | 4 | 2-3 min |
| Workflow Management | 3 | 1-2 min |
| Edge Cases | 7 | 2-3 min |
| Performance | 3 | 1-2 min |
| Anti-Hallucination | 3 | 2-3 min |
| Integration | 9 | 5-8 min |
| **TOTAL** | **~100** | **15-30 min** |

---

## What to Do After Tests Pass

### 1. Review Results

```bash
# Quick summary
tail -50 test_results.txt

# Detailed report
cat COMPREHENSIVE_TEST_REPORT.json | jq '.summary'
```

### 2. Check Pass Rate by Category

```bash
cat COMPREHENSIVE_TEST_REPORT.json | jq '.by_category |
  to_entries |
  map({category: .key, pass_rate: (.value.passed / .value.total * 100 | floor)}) |
  sort_by(.pass_rate)'
```

### 3. Commit Results

```bash
git add COMPREHENSIVE_TEST_REPORT.json
git commit -m "✅ Comprehensive test results: 85% pass rate

- 82/97 tests passed
- Core features working
- Minor issues in web search and context retention
- Ready for beta launch"
```

### 4. Share Results

Send the report to your team:
```bash
# Create summary
cat COMPREHENSIVE_TEST_REPORT.json | jq '.summary' > test_summary.txt

# Or share full console output
cat test_results.txt
```

---

## Next Steps After Testing

### If Tests Pass (>80%)

1. ✅ **Document test results**
   - Save `COMPREHENSIVE_TEST_REPORT.json`
   - Note any failed tests and reasons
   - Create issue tickets for failures

2. ✅ **Prepare for beta launch**
   - Update documentation
   - Create user onboarding guide
   - Set up monitoring
   - Prepare support channels

3. ✅ **Launch beta**
   - Invite initial users
   - Monitor error rates
   - Collect feedback
   - Iterate based on usage

### If Tests Fail (<80%)

1. ❌ **Fix critical failures**
   - Basic conversation must work
   - File operations must work
   - Command safety must work
   - Error handling must work

2. ❌ **Retest after fixes**
   - Run full suite again
   - Verify fixes didn't break other features
   - Aim for >80% pass rate

3. ❌ **Consider limited beta**
   - Launch with working features only
   - Clearly document limitations
   - Fix remaining issues based on feedback

---

## Tips for Successful Testing

### 1. Test in Clean Environment

```bash
# Clear old session data
rm -rf ~/.nocturnal_archive/session_archives/*

# Clear old test results
rm -f COMPREHENSIVE_TEST_REPORT.json

# Fresh agent instance
python test_comprehensive_agent.py
```

### 2. Test with Real Queries

After automated tests pass, manually test with real queries:
- "Find papers by Yann LeCun on CNNs"
- "What's Apple's revenue growth over last 5 years?"
- "Analyze bugs in my code"

### 3. Test Multi-Turn Conversations

```
User: "Find papers about transformers"
Agent: [shows papers]

User: "Which one has the most citations?"
Agent: [analyzes the papers from turn 1]

User: "Tell me more about that paper"
Agent: [expands on the specific paper from turn 2]
```

### 4. Test Edge Cases Manually

- Very long queries (200+ words)
- Rapid context switching
- Ambiguous pronouns
- Mixed requests ("find papers and also check my code")

---

## Expected Test Output Files

After running tests:

```
/home/user/cite-agent/
├── COMPREHENSIVE_TEST_REPORT.json  ← Detailed results (100+ tests)
├── test_comprehensive_agent.py     ← Test suite (your code)
├── TEST_COVERAGE_GUIDE.md         ← This guide
└── RUN_TESTS_GUIDE.md             ← Quick start

/tmp/agent_test_XXXXX/             ← Temporary test directory
├── sample_code.py                 ← Test Python file
├── data.csv                       ← Test CSV file
├── README.md                      ← Test markdown
├── config.json                    ← Test JSON
└── nested/deep/test.txt           ← Test nested file
```

---

## Quick Reference

```bash
# Full test (backend mode)
python test_comprehensive_agent.py

# Full test (direct API mode)
USE_LOCAL_KEYS=true CEREBRAS_API_KEY=csk_xxx python test_comprehensive_agent.py

# Save output
python test_comprehensive_agent.py > test_results.txt 2>&1

# With timeout (10 min max)
timeout 600 python test_comprehensive_agent.py

# Debug mode
NOCTURNAL_DEBUG=1 python test_comprehensive_agent.py

# View results
cat COMPREHENSIVE_TEST_REPORT.json | jq '.summary'

# Check failed tests
cat COMPREHENSIVE_TEST_REPORT.json | jq '.failed_tests'
```

---

**Ready to run tests?** Execute:

```bash
cd /home/user/cite-agent
python test_comprehensive_agent.py
```

Then share the results! 🚀
