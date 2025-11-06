# 🧪 Comprehensive Test Coverage Guide

## Overview

This guide explains what the comprehensive test suite covers and why each test is important for beta launch validation.

**Test File**: `test_comprehensive_agent.py`
**Total Categories**: 15
**Estimated Tests**: 100+ individual test cases
**Estimated Runtime**: 15-30 minutes (depending on API response times)

---

## 📊 Test Categories Breakdown

### 1. Basic Conversation & Understanding (5 tests)

**What it tests:**
- Basic conversational understanding
- Self-description and capabilities
- Domain knowledge (citation formats)
- Response to greetings and thanks

**Why it matters:**
- Ensures agent can handle casual conversations
- Tests if agent understands its own purpose
- Validates quick-reply logic for simple queries

**Edge cases:**
- Very short queries ("hi", "thanks")
- Open-ended questions ("what can you do?")
- Domain-specific knowledge tests

---

### 2. Academic Research - Archive API (5 tests)

**What it tests:**
- Basic paper search functionality
- Specific topic searches (e.g., "transformer architecture")
- Author-based searches
- Empty result handling (anti-hallucination)
- Year-specific queries

**Why it matters:**
- Core feature for academic users
- Tests API integration and error handling
- Validates anti-hallucination safeguards

**Edge cases:**
- Nonexistent topics (should return empty, not hallucinate)
- Ambiguous author names
- Very broad vs very narrow searches

**API calls tested:**
```python
search_academic_papers(query, limit)
# Tests: semantic_scholar, openalex, pubmed fallback chain
```

---

### 3. Financial Analysis - FinSight API (5 tests)

**What it tests:**
- Single company revenue queries
- Multiple metric requests (revenue + profit + market cap)
- Company comparisons (Tesla vs Ford)
- Ticker symbol resolution (company name → ticker)
- Vague query detection ("tell me about Tesla")

**Why it matters:**
- Core feature for financial analysts
- Tests intelligent query analysis
- Validates vagueness detection

**Edge cases:**
- Invalid tickers (XYZABC123)
- Private companies (not in SEC filings)
- Ambiguous company names

**API calls tested:**
```python
get_financial_metrics(ticker, metrics)
get_financial_data(ticker, metric, limit)
```

---

### 4. File Operations (7 tests)

**What it tests:**
- Read Python files
- Read CSV/JSON files
- Find TODOs with grep
- Search for patterns (BUG keyword)
- Write new files
- Edit existing files

**Why it matters:**
- Essential for code analysis workflows
- Tests file operation safety
- Validates command interception

**Edge cases:**
- Binary files
- Empty files
- Files with special characters
- Permission errors

**Operations tested:**
```python
read_file(path, offset, limit)
write_file(path, content)
edit_file(path, old_string, new_string)
grep_search(pattern, path, file_pattern)
glob_search(pattern, path)
```

---

### 5. Directory Exploration & Navigation (5 tests)

**What it tests:**
- List current directory contents
- Show current working directory
- Find files by name pattern
- Find files by extension (*.py)
- Navigate to subdirectories

**Why it matters:**
- Essential for workspace exploration
- Tests context tracking (file_context)
- Validates shell command routing

**Edge cases:**
- Deeply nested directories
- Hidden files
- Symlinks
- Permission-restricted directories

---

### 6. Code Analysis & Bug Detection (4 tests)

**What it tests:**
- Identify bugs in code (division by zero, index errors)
- Explain function behavior
- Count functions in file
- Suggest bug fixes

**Why it matters:**
- High-value feature for developers
- Tests sophisticated code understanding
- Validates LLM reasoning quality

**Edge cases:**
- Syntax errors
- Logic bugs vs runtime bugs
- Security vulnerabilities
- Performance issues

---

### 7. Web Search & Fallback (3 tests)

**What it tests:**
- Current events queries
- General knowledge fallback
- Private company data (not in FinSight)

**Why it matters:**
- Fallback for queries outside Archive/FinSight scope
- Tests intelligent tool selection
- Validates web search integration

**Edge cases:**
- Conflicting information across sources
- Very recent events (last 24 hours)
- Queries that should NOT trigger web search

---

### 8. Multi-Turn Context & Pronoun Resolution (4 scenarios × 3 turns = 12 tests)

**What it tests:**
- File pronoun resolution ("it", "that file")
- Paper context retention ("which one is most cited?")
- Financial comparison context ("how does that compare to...")
- Directory context ("read the first one")

**Why it matters:**
- **MOST IMPORTANT FOR UX** - Natural conversations require context
- Tests conversation_history tracking
- Validates file_context management
- Proves agent is "intelligent" vs "stateless"

**Edge cases:**
- Long conversations (>50 turns)
- Switching contexts rapidly
- Ambiguous pronouns ("it" could refer to multiple things)
- Nested contexts (file in directory, paper in list)

**What's being tracked:**
```python
self.file_context = {
    'last_file': None,
    'last_directory': None,
    'recent_files': [],  # Last 5
    'recent_dirs': [],
}
self.conversation_history  # Last N messages
self._session_topics  # Per-user context
```

---

### 9. Command Safety & Interception (4 tests)

**What it tests:**
- Safe command interception (cat → read_file)
- Find interception (find → glob_search)
- Grep interception (grep → grep_search)
- Dangerous command blocking (rm -rf)

**Why it matters:**
- **CRITICAL FOR SECURITY** - Prevents system damage
- Validates command safety classifier
- Tests shell command interception layer

**Edge cases:**
- Commands with pipes
- Commands with redirection
- Chained commands (&&, ||)
- Commands with sudo

**Safety levels:**
```python
SAFE: read-only (ls, cat, find, grep, pwd)
CAUTIOUS: state-changing but recoverable (cd, mkdir, touch)
DANGEROUS: requires confirmation (rm, mv destructive ops)
BLOCKED: system-threatening (rm -rf /, :(){:|:&};:)
```

---

### 10. Error Handling & Recovery (4 tests)

**What it tests:**
- Nonexistent file errors
- Invalid company ticker errors
- Ambiguous query handling
- Empty search results

**Why it matters:**
- **CRITICAL FOR UX** - Graceful degradation
- Tests error message quality
- Validates fallback chains work

**Edge cases:**
- Network timeouts
- API rate limits
- Malformed queries
- Partial failures (2/3 APIs succeed)

**Retry logic tested:**
```python
# Exponential backoff
retry_delays = [5, 15, 30]  # seconds
max_attempts = 3

# Timeout handling
custom_timeout = 90  # seconds
custom_max_attempts = 2
```

---

### 11. Workflow Management (3 tests)

**What it tests:**
- Save papers to workflow
- List saved papers
- View query history

**Why it matters:**
- Productivity feature for power users
- Tests state persistence
- Validates workflow integration

**Edge cases:**
- Save duplicate papers
- Save with custom names
- Retrieve after restart

---

### 12. Edge Cases & Boundary Conditions (7 tests)

**What it tests:**
- Very long queries (100+ words)
- Single word queries
- Numbers-only queries
- Special character queries
- Empty queries ("...")
- Mixed language queries (English + Chinese)
- Code in queries

**Why it matters:**
- **REVEALS HIDDEN BUGS** - Real users do unexpected things
- Tests input validation
- Validates tokenization and parsing

**Why these matter:**
- Long queries: Token limit handling
- Single words: Context requirement
- Special chars: Escaping and injection
- Mixed language: Language detection
- Code snippets: Syntax highlighting, execution safety

---

### 13. Performance & Timeout Handling (3 tests)

**What it tests:**
- Fast response for simple queries (<2s)
- Quick lookups (<5s)
- Reasonable response times for complex queries (<30s)

**Why it matters:**
- **CRITICAL FOR UX** - Slow = unusable
- Tests timeout configuration
- Validates circuit breaker behavior

**Performance targets:**
```
Simple queries (2+2, define X): <2 seconds
Medium queries (search papers): <10 seconds
Complex queries (multi-API): <30 seconds
Timeout threshold: 60 seconds (with retry)
```

---

### 14. Anti-Hallucination Safeguards (3 tests)

**What it tests:**
- Empty research results (explicit warning)
- Vague query clarification requests
- Nonexistent company data (don't invent)

**Why it matters:**
- **CRITICAL FOR TRUST** - Hallucinated data destroys credibility
- Tests explicit markers (EMPTY_RESULTS, warning)
- Validates vagueness detection

**Safeguards tested:**
```python
# Archive API
if not results:
    payload["EMPTY_RESULTS"] = True
    payload["warning"] = "DO NOT GENERATE FAKE PAPERS"

# Query analysis
if self._is_query_too_vague_for_apis(query):
    api_results["query_analysis"] = {
        "is_vague": True,
        "suggestion": "Ask clarifying questions"
    }
```

---

### 15. Integration Tests (3 scenarios × 3 turns = 9 tests)

**What it tests:**
- Research + File operations (search → save → read)
- Financial + Code analysis (revenue → create script → check bugs)
- Directory + Research + Save (list files → search papers → save workflow)

**Why it matters:**
- **PROVES REAL-WORLD UTILITY** - Users combine features
- Tests cross-API coordination
- Validates end-to-end workflows

**Example workflow:**
```
User: "Find papers about deep learning"
Agent: [calls Archive API]

User: "Save the results to papers.txt"
Agent: [writes file with paper list]

User: "Now show me what's in that file"
Agent: [reads file using context from turn 1]
```

---

## 🎯 What Makes This Test Suite Comprehensive

### 1. **Feature Coverage** (100%)
Every major feature is tested:
- ✅ Archive API (research)
- ✅ FinSight API (financial)
- ✅ File operations
- ✅ Directory exploration
- ✅ Code analysis
- ✅ Web search
- ✅ Workflow management

### 2. **Edge Case Coverage** (Deep)
- Empty results
- Invalid inputs
- Timeout scenarios
- Error conditions
- Boundary values
- Special characters
- Mixed languages
- Very long/short inputs

### 3. **Sophistication Testing** (Advanced)
- **Context retention** - Can agent remember across turns?
- **Pronoun resolution** - Does "it" work correctly?
- **Intelligent routing** - Does agent choose right tool?
- **Command safety** - Does interception work?
- **Anti-hallucination** - Does agent admit when it doesn't know?

### 4. **Real-World Scenarios** (Practical)
- Multi-turn conversations (not just single Q&A)
- Mixed API calls (research + file ops)
- Error recovery (retry logic)
- Context switching (file → paper → financial)

### 5. **Performance Validation** (Production)
- Response time tracking
- Timeout handling
- Circuit breaker behavior
- Retry logic verification

---

## 📈 Expected Results

### Realistic Pass Rates

| Category | Expected Pass Rate | Notes |
|----------|-------------------|-------|
| Basic Conversation | 95-100% | Should always work |
| Academic Research | 85-95% | Depends on API availability |
| Financial Analysis | 85-95% | Depends on API availability |
| File Operations | 95-100% | Local operations, very reliable |
| Directory Exploration | 95-100% | Local operations, very reliable |
| Code Analysis | 80-90% | Depends on LLM quality |
| Web Search | 70-85% | May be disabled or rate-limited |
| Multi-Turn Context | 75-90% | **Most challenging feature** |
| Command Safety | 95-100% | Should always work |
| Error Handling | 90-100% | Should always work |
| Workflow Management | 80-90% | Depends on state persistence |
| Edge Cases | 70-85% | Some expected failures |
| Performance | 85-95% | Depends on backend speed |
| Anti-Hallucination | 90-100% | Critical safeguard |
| Integration | 70-85% | Complex, many dependencies |

**Overall Expected**: 80-90% pass rate

### What "Pass" Means

A test **passes** if:
1. ✅ Agent responds without crashing
2. ✅ Response is relevant to the query
3. ✅ Expected tools are used (if specified)
4. ✅ Custom validation passes (if specified)
5. ✅ No error messages (unless expected)

A test **fails** if:
1. ❌ Agent crashes or times out
2. ❌ Response is completely irrelevant
3. ❌ Wrong tools used
4. ❌ Hallucinated data when should admit "don't know"
5. ❌ Security violation (dangerous command executed)

---

## 🚀 How to Run

### Quick Start (All Tests)

```bash
cd /home/user/cite-agent
python test_comprehensive_agent.py
```

### Run Specific Category

```python
# Modify test_comprehensive_agent.py, comment out categories:
test_categories = [
    # self.test_basic_conversation,
    self.test_academic_research,  # Only this one
    # self.test_financial_analysis,
    # ...
]
```

### Run with USE_LOCAL_KEYS (Bypass Backend)

```bash
USE_LOCAL_KEYS=true CEREBRAS_API_KEY=csk_xxx python test_comprehensive_agent.py
```

---

## 📊 Interpreting Results

### Excellent (90-100% pass)
```
✅ Agent is production-ready
✅ All core features work
✅ Edge cases handled well
→ Ready for beta launch
```

### Good (75-89% pass)
```
✅ Core features work
⚠️  Some edge cases fail
⚠️  Multi-turn context may be weak
→ Ready for beta with caveats
```

### Needs Work (60-74% pass)
```
⚠️  Core features mostly work
❌ Many edge cases fail
❌ Context retention weak
→ Fix critical issues before beta
```

### Not Ready (<60% pass)
```
❌ Core features broken
❌ Many failures across categories
❌ Not safe for users
→ Do NOT launch beta
```

---

## 🔍 Debugging Failed Tests

### 1. Check Test Output
```
❌ Research: Basic paper search (2.34s)
   Error: Archive API timeout
   Details: Connection to api.example.com timed out after 30s
```

**Diagnosis**: Archive API is down or slow
**Fix**: Check API status, increase timeout, or test with local keys

### 2. Check Agent Response
```python
print(result.response.response)  # What did agent say?
print(result.response.tools_used)  # What tools did it use?
print(result.response.api_results)  # What API data was fetched?
```

### 3. Check Logs
```bash
# Backend logs
tail -f /tmp/backend.log | grep ERROR

# Agent debug mode
NOCTURNAL_DEBUG=1 python test_comprehensive_agent.py
```

### 4. Test Isolated API Call
```python
# Test Archive API directly
result = await agent.search_academic_papers("machine learning", limit=3)
print(json.dumps(result, indent=2))
```

---

## 📁 Output Files

After running tests:

1. **`COMPREHENSIVE_TEST_REPORT.json`**
   - Detailed results for every test
   - Pass/fail status
   - Response times
   - Error messages
   - Tools used

2. **Console output**
   - Real-time progress
   - Summary by category
   - Failed test details

3. **Test files created** (in temp directory)
   - `sample_code.py` (with bugs)
   - `data.csv` (sample data)
   - `README.md` (documentation)
   - `config.json` (configuration)
   - `nested/deep/test.txt` (nested file)

---

## 🎯 Success Criteria for Beta Launch

Based on test results:

### ✅ Required (Must Pass)
- [ ] Basic conversation: 95%+
- [ ] File operations: 90%+
- [ ] Command safety: 95%+
- [ ] Error handling: 85%+
- [ ] Anti-hallucination: 90%+

### ✅ Important (Should Pass)
- [ ] Academic research: 80%+
- [ ] Financial analysis: 80%+
- [ ] Directory exploration: 85%+
- [ ] Multi-turn context: 70%+
- [ ] Performance: 85%+

### ✅ Nice to Have
- [ ] Code analysis: 75%+
- [ ] Web search: 70%+
- [ ] Workflow: 75%+
- [ ] Edge cases: 70%+
- [ ] Integration: 65%+

**Overall Minimum**: 80% pass rate across all tests

---

## 💡 What This Test Suite Proves

When tests pass, you can confidently say:

✅ **"The agent is sophisticated"**
- Proof: Multi-turn context tests pass (remembers across turns)
- Proof: Intelligent tool selection (doesn't waste API calls)
- Proof: Command interception (translates unsafe → safe)

✅ **"The agent is comprehensive"**
- Proof: All 7 major features tested and working
- Proof: Integration tests show features work together
- Proof: Edge cases handled gracefully

✅ **"The agent is intelligent"**
- Proof: Pronoun resolution works (understands "it", "that")
- Proof: Vague query detection (asks for clarification)
- Proof: Anti-hallucination safeguards (admits don't know)
- Proof: Code analysis works (finds bugs, suggests fixes)

✅ **"The agent is ready for beta"**
- Proof: 80%+ pass rate on comprehensive test suite
- Proof: Error handling works (graceful degradation)
- Proof: Performance acceptable (<30s for complex queries)
- Proof: Security verified (dangerous commands blocked)

---

**Next Steps**: Run the tests and share results!

```bash
python test_comprehensive_agent.py > test_results.txt 2>&1
```
