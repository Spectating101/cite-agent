# 🧪 Beta Launch Test Guide

**Consolidated testing guide for cite-agent beta launch validation**

---

## Quick Start (30 seconds)

```bash
cd /home/user/cite-agent

# Option 1: Using backend (requires auth setup)
python test_beta_launch.py

# Option 2: Using direct API keys (bypass backend)
USE_LOCAL_KEYS=true CEREBRAS_API_KEY=csk_xxx python test_beta_launch.py
```

**Expected runtime**: 15-30 minutes
**Expected pass rate**: 80-90%
**Total tests**: 120+ across 18 categories

---

## What This Test Suite Validates

### ✅ Sophistication
- **Multi-turn context retention**: Remembers files, papers, and conversations across turns
- **Pronoun resolution**: Understands "it", "that file", "those papers"
- **Intelligent tool selection**: Doesn't waste API calls on vague queries
- **Command interception**: Translates unsafe shell → safe file operations

### ✅ Comprehensiveness
- **7 major features tested**: Research, finance, files, directories, code analysis, web search, workflows
- **Integration workflows**: Features work together (research + file ops, finance + code analysis)
- **Edge cases**: Long queries, special characters, empty inputs, mixed languages

### ✅ Intelligence
- **Anti-hallucination**: Admits when data unavailable, doesn't invent papers/companies
- **Vague query detection**: Asks for clarification instead of guessing
- **Code understanding**: Finds bugs, explains functions, suggests fixes
- **Context tracking**: Maintains session state, resolves references

### ✅ Production Readiness
- **Error handling**: Graceful degradation, helpful error messages, retry logic
- **Security**: Dangerous commands blocked, API keys not exposed
- **Performance**: <2s for simple queries, <30s for complex queries
- **CLI interface**: End-to-end user experience validation

---

## Test Categories (18 Total)

### Part 1: API Testing (Internal Logic - 15 categories)

| # | Category | Tests | Time | Critical? | What It Proves |
|---|----------|-------|------|-----------|----------------|
| 1 | Basic Conversation | 5 | 1-2 min | ✅ Yes | Agent understands casual conversation |
| 2 | Academic Research | 5 | 3-5 min | ✅ Yes | Archive API integration works |
| 3 | Financial Analysis | 5 | 3-5 min | ✅ Yes | FinSight API integration works |
| 4 | File Operations | 5 | 1-2 min | ✅ Yes | Read/write/edit/search files safely |
| 5 | Directory Exploration | 4 | 1-2 min | ⚠️ Important | Navigate and explore workspace |
| 6 | Code Analysis | 4 | 2-3 min | ⚠️ Important | Find bugs, explain code, suggest fixes |
| 7 | Web Search | 2 | 2-4 min | ⚠️ Optional | Fallback for out-of-scope queries |
| 8 | Multi-Turn Context | 9 | 5-8 min | ✅ Yes | **Most important**: Context retention |
| 9 | Command Safety | 4 | 1-2 min | ✅ Yes | **Security**: Block dangerous commands |
| 10 | Error Handling | 4 | 2-3 min | ✅ Yes | Graceful degradation on failures |
| 11 | Workflow Management | 3 | 1-2 min | ⚠️ Optional | Save/list/retrieve workflows |
| 12 | Edge Cases | 5 | 2-3 min | ⚠️ Important | Boundary conditions, unusual inputs |
| 13 | Performance | 3 | 1-2 min | ✅ Yes | Response time targets met |
| 14 | Anti-Hallucination | 3 | 2-3 min | ✅ Yes | **Trust**: Admit "don't know" |
| 15 | Integration | 6 | 5-8 min | ⚠️ Important | Multi-API workflows |

### Part 2: CLI & Backend Testing (3 categories)

| # | Category | Tests | Time | Critical? | What It Proves |
|---|----------|-------|------|-----------|----------------|
| 16 | CLI Interface | 4 | 2-3 min | ✅ Yes | `nocturnal` command works end-to-end |
| 17 | Backend API | 3 | 1-2 min | ✅ Yes | HTTP endpoints respond correctly |
| 18 | Security Audit | 2 | <1 min | ✅ Yes | No exposed secrets, proper gitignore |

---

## Prerequisites

### Option A: Backend Mode (Full Production Test)

**Requirements:**
1. ✅ Backend API running (127.0.0.1:8000)
2. ✅ PostgreSQL database set up
3. ✅ User registered with auth token
4. ✅ Auth token in `~/.nocturnal_archive/session.json`

**Setup:**
```bash
# 1. Start backend
cd cite-agent-api
nohup python -m uvicorn src.main:app --host 127.0.0.1 --port 8000 &

# 2. Verify backend is running
curl http://127.0.0.1:8000/readyz

# 3. Run tests
cd /home/user/cite-agent
python test_beta_launch.py
```

### Option B: Direct API Mode (Quick Test)

**Requirements:**
1. ✅ Cerebras or Groq API key

**Setup:**
```bash
cd /home/user/cite-agent

# With Cerebras
USE_LOCAL_KEYS=true CEREBRAS_API_KEY=csk_your_key_here python test_beta_launch.py

# With Groq
USE_LOCAL_KEYS=true GROQ_API_KEY=gsk_your_key_here python test_beta_launch.py
```

**Pros:** Faster setup, direct LLM testing, good for development
**Cons:** Doesn't test backend auth flow, database integration, full production path

---

## Understanding Test Output

### Real-Time Progress

```
🧪 CONSOLIDATED BETA LAUNCH TEST SUITE
════════════════════════════════════════════════════════════════════════════════
Started: 2025-11-06 10:30:00

🔧 Initializing test environment...
   Test directory: /tmp/agent_test_abc123
   Created 5 test files
✅ Test environment ready

📋 Category 1: Basic Conversation & Understanding
   ✅ Basic: Greeting (0.45s)
   ✅ Basic: Self-description (1.23s)
   ✅ Basic: Capabilities (1.56s)
   ✅ Basic: Citation formats (2.34s)
   ✅ Basic: Thanks (0.38s)

💰 Category 3: Financial Analysis (FinSight API)
   ✅ Finance: Single company revenue (3.45s)
   ❌ Finance: Invalid ticker (4.67s)
      Error: API timeout after 30s
   ...
```

### Final Summary

```
════════════════════════════════════════════════════════════════════════════════
📊 COMPREHENSIVE TEST SUMMARY
════════════════════════════════════════════════════════════════════════════════

✨ Overall Results:
   Total Tests: 118
   Passed: 97 ✅
   Failed: 21 ❌
   Pass Rate: 82.2%
   Total Duration: 1234.56s

📋 Results by Category:
   ✅ Basic Conversation: 5/5 (100%)
   ✅ File Operations: 5/5 (100%)
   ⚠️  Academic Research: 4/5 (80%)
   ⚠️  Multi-Turn Context: 7/9 (78%)
   ❌ Web Search: 1/2 (50%)

❌ Failed Tests:
   • Finance: Invalid ticker
     Error: API timeout after 30s
   • Web: Current events
     Error: Web search not configured
   ...

📄 Detailed report saved to: CONSOLIDATED_TEST_REPORT.json

════════════════════════════════════════════════════════════════════════════════
✅ AGENT IS READY with minor issues to address
════════════════════════════════════════════════════════════════════════════════
```

---

## Interpreting Results

### ✅ 90-100% Pass Rate
**Verdict**: 🎉 ALL TESTS PASSED! Ready for beta launch!

**What this means:**
- Core features work perfectly
- Edge cases handled well
- Context retention works
- Security verified

**Action**: Launch beta with confidence

### ✅ 80-89% Pass Rate
**Verdict**: ✅ AGENT IS READY with minor issues to address

**What this means:**
- Core features work
- Some edge cases fail (acceptable)
- Multi-turn context may have gaps
- Some API integrations flaky

**Action**: Review failed tests, fix critical ones, launch beta

**Typical issues:**
- Archive/FinSight API timeouts (not agent's fault)
- Web search disabled (acceptable if not core feature)
- Some context resolution failures (can improve over time)

### ⚠️ 60-79% Pass Rate
**Verdict**: ⚠️  AGENT NEEDS WORK before beta launch

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

### ❌ <60% Pass Rate
**Verdict**: ❌ AGENT NOT READY - significant issues found

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

## Success Criteria for Beta Launch

### ✅ Required (Must Pass)
- [ ] Basic conversation: 95%+
- [ ] File operations: 90%+
- [ ] Command safety: 95%+
- [ ] Error handling: 85%+
- [ ] Anti-hallucination: 90%+
- [ ] Overall pass rate: 80%+

### ✅ Important (Should Pass)
- [ ] Academic research: 80%+
- [ ] Financial analysis: 80%+
- [ ] Multi-turn context: 70%+
- [ ] CLI interface: 85%+
- [ ] Performance: 85%+

### ✅ Nice to Have
- [ ] Code analysis: 75%+
- [ ] Web search: 70%+
- [ ] Workflow: 75%+
- [ ] Edge cases: 70%+
- [ ] Integration: 65%+

---

## Debugging Failed Tests

### Step 1: Check Console Output

Look at the "Failed Tests" section:

```
❌ Failed Tests:
   • Research: Author search
     Error: Archive API timeout after 30s
```

### Step 2: Check Detailed Report

```bash
cat CONSOLIDATED_TEST_REPORT.json | jq '.all_results[] | select(.passed == false)'
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
# Backend logs
tail -100 /tmp/backend.log | grep -i error

# Debug mode
NOCTURNAL_DEBUG=1 python test_beta_launch.py 2>&1 | tee debug.log
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
- Test Archive API health: `curl -s http://127.0.0.1:8000/api/health`
- Increase timeout in enhanced_ai_agent.py
- This is acceptable if only a few tests fail (not agent's fault)

### Issue 3: "Backend not running"

**Error:**
```
❌ Error: HTTP session not initialized
```

**Fix:**
```bash
# Start backend
cd cite-agent-api
python -m uvicorn src.main:app --host 127.0.0.1 --port 8000

# Verify it's up
curl http://127.0.0.1:8000/readyz
```

### Issue 4: Tests hang forever

**Fix:**
```bash
# Kill hanging test
pkill -f test_beta_launch

# Run with timeout (10 minute max)
timeout 600 python test_beta_launch.py
```

---

## Performance Benchmarks

Expected test durations:

| Test Type | Expected Time |
|-----------|---------------|
| Simple queries (greeting, thanks) | <2s |
| Quick lookups (file read, directory list) | <5s |
| Medium queries (paper search, finance lookup) | <10s |
| Complex queries (multi-API, integration) | <30s |
| Full test suite | 15-30 min |

---

## Output Files

After running tests:

1. **CONSOLIDATED_TEST_REPORT.json**
   - Detailed results for every test
   - Pass/fail status, response times, error messages
   - Tools used, token counts

2. **Console output**
   - Real-time progress
   - Summary by category
   - Failed test details

3. **Test files created** (in `/tmp/agent_test_XXXXX/`)
   - sample_code.py (with intentional bugs)
   - data.csv (sample data)
   - README.md (documentation)
   - config.json (configuration)
   - nested/deep/test.txt (nested file)

---

## What This Test Suite Proves

When tests pass (>80%), you can confidently say:

### ✅ "The agent is sophisticated"
**Proof:**
- Multi-turn context tests pass (remembers across turns)
- Intelligent tool selection (doesn't waste API calls)
- Command interception (translates unsafe → safe)

### ✅ "The agent is comprehensive"
**Proof:**
- All 7 major features tested and working
- Integration tests show features work together
- Edge cases handled gracefully

### ✅ "The agent is intelligent"
**Proof:**
- Pronoun resolution works (understands "it", "that")
- Vague query detection (asks for clarification)
- Anti-hallucination safeguards (admits don't know)
- Code analysis works (finds bugs, suggests fixes)

### ✅ "The agent is ready for beta"
**Proof:**
- 80%+ pass rate on comprehensive test suite
- Error handling works (graceful degradation)
- Performance acceptable (<30s for complex queries)
- Security verified (dangerous commands blocked)

---

## Next Steps After Testing

### If Tests Pass (>80%)

1. ✅ **Document test results**
   ```bash
   # Save report
   cp CONSOLIDATED_TEST_REPORT.json beta_launch_results_$(date +%Y%m%d).json

   # Note failures
   cat CONSOLIDATED_TEST_REPORT.json | jq '.all_results[] | select(.passed == false)' > failures.txt
   ```

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
   ```bash
   python test_beta_launch.py > retest_results.txt 2>&1
   ```

3. ❌ **Consider limited beta**
   - Launch with working features only
   - Clearly document limitations
   - Fix remaining issues based on feedback

---

## Tips for Successful Testing

### Before Running

1. ✅ **Ensure backend is running**
   ```bash
   curl http://127.0.0.1:8000/readyz
   ```

2. ✅ **Check API keys are valid**
   ```bash
   # Test Cerebras
   curl -X POST https://api.cerebras.ai/v1/chat/completions \
     -H "Authorization: Bearer YOUR_KEY" \
     -d '{"model":"gpt-oss-120b","messages":[{"role":"user","content":"test"}]}'
   ```

3. ✅ **Clear old state**
   ```bash
   rm -rf ~/.nocturnal_archive/session_archives/*
   rm -f CONSOLIDATED_TEST_REPORT.json
   ```

### While Running

1. 📊 Monitor progress in real-time
2. ⏱️ Be patient (15-30 minutes)
3. 🔍 Note unusual failures

### After Running

1. 📊 Review summary first
2. 🔍 Investigate failures
3. 📝 Document findings

---

## Quick Reference

```bash
# Full test (backend mode)
python test_beta_launch.py

# Full test (direct API mode)
USE_LOCAL_KEYS=true CEREBRAS_API_KEY=csk_xxx python test_beta_launch.py

# Save output
python test_beta_launch.py > test_results.txt 2>&1

# With timeout (10 min max)
timeout 600 python test_beta_launch.py

# Debug mode
NOCTURNAL_DEBUG=1 python test_beta_launch.py

# View results
cat CONSOLIDATED_TEST_REPORT.json | jq '.summary'

# Check failed tests
cat CONSOLIDATED_TEST_REPORT.json | jq '.all_results[] | select(.passed == false)'
```

---

## Bottom Line

This consolidated test suite answers the question:

> **"Is the agent truly good, sophisticated, comprehensive, and most importantly intelligent in assisting?"**

**When tests pass (>80%)**, you have **proof**:

✅ Sophisticated: Multi-turn context + intelligent routing
✅ Comprehensive: All 7 features tested and working
✅ Intelligent: Context tracking + anti-hallucination + code understanding
✅ Ready for beta: Error handling + security + performance validated

**To prove it:**
```bash
python test_beta_launch.py
```

**Expected result:**
```
✅ AGENT IS READY with minor issues to address
Pass Rate: 82-87%
```

Then you can confidently launch beta! 🚀

---

**Created**: November 6, 2025
**Status**: Consolidated from multiple test suites
**Test File**: `test_beta_launch.py`
**Report Output**: `CONSOLIDATED_TEST_REPORT.json`
