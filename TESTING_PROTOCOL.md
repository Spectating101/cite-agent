# Testing Protocol for Cite-Agent
**Last Updated:** 2025-11-15
**Supervisor:** Claude Code (Architecture & Design)
**Operator:** CC Terminal (Hands-on Testing)

---

## 🎯 CRITICAL: Test the RIGHT Branch

### ❌ WRONG Branch (what you tested before):
```bash
git checkout production-latest  # OLD CODE - missing critical fixes!
```

### ✅ CORRECT Branch (has all the latest fixes):
```bash
git checkout claude/repo-cleanup-013fq1BicY8SkT7tNAdLXt3W
git pull origin claude/repo-cleanup-013fq1BicY8SkT7tNAdLXt3W
```

**Verify you're on the right code:**
```bash
# This file should exist with my improvements:
grep "Compact format: Title (FirstAuthor, Year)" cite_agent/function_calling.py

# If found = ✅ correct branch
# If not found = ❌ wrong branch
```

---

## 🎓 Design Vision: Conversational Research Assistant

### What "Conversational" Means:

**✅ YES - Natural Language:**
```
Found 5 papers on transformers:

1. Attention Is All You Need (Vaswani, 2017) - 104,758 citations [DOI: 10.48550/arXiv.1706.03762]
   This foundational paper introduced the transformer architecture, replacing recurrent layers with
   multi-head self-attention mechanisms...

2. BERT: Pre-training of Deep Bidirectional Transformers (Devlin, 2019) - 89,234 citations
   BERT revolutionized NLP by using masked language modeling for bidirectional pre-training...
```

**❌ NO - Raw Tool Output:**
```
{"query": "transformers", "limit": 5}{"papers": [{"id": "df2b0e26...", "title": "BERT: Pre-training..."}]}
```

**❌ NO - Just Listing Without Synthesis:**
```
- Paper 1
- Paper 2
- Paper 3

(No explanation, no context, no insights)
```

---

## 🔍 What to Test For

### 1. **No JSON Leaking** (CRITICAL)
**Test:**
```bash
echo "find papers on transformers" | python3 -m cite_agent.cli
```

**✅ PASS if:** Natural language response, no raw JSON
**❌ FAIL if:** You see `{"query":`, `{"papers":`, or `{\"id\":` anywhere

---

### 2. **Proper Citation Formatting** (CRITICAL)
**Test:**
```bash
echo "find papers on BERT" | python3 -m cite_agent.cli
```

**✅ PASS if:**
- Numbered list: `1. Paper Title (Author, Year)`
- Citation counts with commas: `104,758 citations`
- DOI included: `[DOI: 10.48550/...]`
- First author name shown

**❌ FAIL if:**
- Just title and year
- No author attribution
- No DOI
- No citation counts

---

### 3. **Intelligent Synthesis** (HIGH PRIORITY)
**Test:**
```bash
echo "Compare BERT and GPT-3 approaches to language modeling" | python3 -m cite_agent.cli
```

**✅ PASS if:**
- Explains architectural differences (bidirectional vs autoregressive)
- Discusses training objectives (masked LM vs next-token prediction)
- Cites both original papers
- Provides context and insights

**❌ FAIL if:**
- Just lists papers without comparison
- Generic descriptions without specifics
- No citations
- Missing key technical details

---

### 4. **Token Efficiency** (MEDIUM PRIORITY)
**Test:**
```bash
export NOCTURNAL_DEBUG=1
echo "hi" | python3 -m cite_agent.cli
```

**✅ PASS if:** <500 tokens (should skip synthesis)
**⚠️ ACCEPTABLE if:** 500-1000 tokens
**❌ FAIL if:** >1000 tokens (unnecessary synthesis)

---

### 5. **Multi-Step Reasoning** (HIGH PRIORITY)
**Test:**
```bash
echo "What are the main challenges in scaling vision transformers? Find papers and synthesize." | python3 -m cite_agent.cli
```

**✅ PASS if:**
- Finds multiple relevant papers
- Extracts key challenges from each
- Synthesizes into coherent summary
- Cites sources for each point

**❌ FAIL if:**
- Single paper response
- No synthesis across sources
- Vague/generic challenges without citations

---

## 📋 Quick Validation Checklist (Run This First)

```bash
#!/bin/bash
# Quick smoke test - run this before comprehensive testing

echo "=== SMOKE TEST ==="

# Test 1: Simple greeting (token efficiency)
echo ""
echo "TEST 1: Token efficiency on simple query"
export NOCTURNAL_DEBUG=1
result=$(echo "hi" | python3 -m cite_agent.cli 2>&1)
tokens=$(echo "$result" | grep "Tokens used:" | grep -oP '\d+')
if [ "$tokens" -lt 1000 ]; then
    echo "✅ PASS: $tokens tokens (target <1000)"
else
    echo "❌ FAIL: $tokens tokens (too high)"
fi

# Test 2: Paper search (JSON leaking check)
echo ""
echo "TEST 2: No JSON leaking"
result=$(echo "find papers on transformers" | python3 -m cite_agent.cli 2>&1)
if echo "$result" | grep -q '{"query":'; then
    echo "❌ FAIL: JSON leaked into response"
else
    echo "✅ PASS: No JSON leaking"
fi

# Test 3: Citation formatting
echo ""
echo "TEST 3: Citation formatting"
if echo "$result" | grep -qP '\d+\.\s+.+\(.+,\s+\d{4}\)'; then
    echo "✅ PASS: Proper citation format detected"
else
    echo "❌ FAIL: Citation format incorrect"
fi

echo ""
echo "=== SMOKE TEST COMPLETE ==="
echo "If all 3 tests PASS, proceed to comprehensive testing"
echo "If any FAIL, report to Claude Code immediately"
```

---

## 🚀 Testing Workflow

### Step 1: Environment Setup
```bash
# 1. Switch to correct branch
git checkout claude/repo-cleanup-013fq1BicY8SkT7tNAdLXt3W
git pull origin claude/repo-cleanup-013fq1BicY8SkT7tNAdLXt3W

# 2. Verify you have the fixes
grep "Compact format: Title" cite_agent/function_calling.py

# 3. Set debug mode
export NOCTURNAL_DEBUG=1
```

### Step 2: Run Smoke Test
```bash
# Save the smoke test script above as smoke_test.sh
chmod +x smoke_test.sh
./smoke_test.sh
```

### Step 3: Run Comprehensive Tests (only if smoke test passes)
```bash
./test_realistic_quick.sh
```

### Step 4: Report Results
**Format:**
```markdown
## Test Results - [Date/Time]

**Branch:** claude/repo-cleanup-013fq1BicY8SkT7tNAdLXt3W
**Commit:** [git rev-parse HEAD]

### Smoke Test:
- Token efficiency: ✅/❌ ([tokens] tokens)
- JSON leaking: ✅/❌
- Citation format: ✅/❌

### Comprehensive Tests:
- Paper search: ✅/❌ (notes)
- Comparative analysis: ✅/❌ (notes)
- Financial queries: ✅/❌ (notes)
- Multi-step reasoning: ✅/❌ (notes)

### Issues Found:
1. [Issue description]
2. [Issue description]

### Examples of Good Output:
[Paste example]

### Examples of Bad Output:
[Paste example]
```

---

## 🎯 Success Criteria (What We're Aiming For)

### Must Have (Launch Blockers if Missing):
- ✅ Zero JSON leaking
- ✅ Proper citations with DOI
- ✅ Intelligent synthesis (not just listing)
- ✅ Token efficiency (<2000 avg for research queries)

### Should Have (Polish Items):
- ✅ Multi-step reasoning works
- ✅ Graceful error handling
- ✅ Context-aware responses

### Nice to Have (Future Enhancements):
- Tables for comparisons
- BibTeX generation
- Advanced filtering

---

## 📞 Communication Protocol

### When to Report to Claude Code:

**IMMEDIATELY (Stop Testing):**
- JSON leaking detected
- Responses are truncated/incomplete
- Agent hallucinating papers/data
- Critical errors/crashes

**AFTER SMOKE TEST:**
- Smoke test results (pass/fail for each)
- Any unexpected behavior

**AFTER COMPREHENSIVE TESTING:**
- Full test results with examples
- Pass rate percentage
- Token usage statistics

### Report Format:
```
@Claude Code - [URGENT/NORMAL/FYI]

Branch: claude/repo-cleanup-013fq1BicY8SkT7tNAdLXt3W
Commit: [hash]

Issue: [brief description]
Test: [what you ran]
Expected: [what should happen]
Actual: [what happened]
Output: [relevant output snippet]
```

---

## 🧠 Remember: The Full Vision

We're building a **professor-ready research assistant** that:
1. **Understands context** - Not just keywords, but intent
2. **Synthesizes intelligently** - Connects ideas across papers
3. **Cites properly** - Academic-grade citations
4. **Explains clearly** - Natural language, not technical jargon
5. **Saves time** - Token efficient without sacrificing quality

Every test should ask: **"Would a professor trust this response?"**

If the answer is no, report it. If yes, document why it's good.

---

## 📚 Reference: Example of Perfect Output

**Query:** "Compare BERT and GPT-3 approaches"

**Expected Output:**
```
BERT and GPT-3 represent two distinct approaches to language modeling, each with unique strengths:

**Architectural Differences:**

1. **Directionality**
   - BERT (Devlin et al., 2019): Bidirectional encoder using masked language modeling
   - GPT-3 (Brown et al., 2020): Unidirectional decoder using next-token prediction

2. **Model Scale**
   - BERT: 340M parameters (BERT-Large)
   - GPT-3: 175B parameters (515x larger)

3. **Training Objectives**
   - BERT: Masked tokens + next sentence prediction
   - GPT-3: Autoregressive generation

4. **Use Cases**
   - BERT: Excels at understanding tasks (classification, QA, NER)
   - GPT-3: Excels at generation tasks (summarization, translation, creative writing)

5. **Fine-tuning Approach**
   - BERT: Requires task-specific fine-tuning
   - GPT-3: Few-shot in-context learning

**Citations:**
- Devlin, J., et al. (2019). "BERT: Pre-training of Deep Bidirectional Transformers for Language Understanding." NAACL. [DOI: 10.18653/v1/N19-1423]
- Brown, T., et al. (2020). "Language Models are Few-Shot Learners." NeurIPS. [arXiv:2005.14165]

Both models revolutionized NLP, but serve different purposes: BERT for understanding, GPT-3 for generation.
```

**Why This is Good:**
✅ Clear structure with headings
✅ Point-by-point comparison
✅ Technical accuracy
✅ Proper citations with DOI
✅ Synthesis/conclusion
✅ Natural language throughout
✅ No JSON or raw output

---

**Remember:** You're testing if this can replace a grad student doing literature review. That's the bar.
