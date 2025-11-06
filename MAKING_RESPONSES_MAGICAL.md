# Making Agent Responses Intuitive and Magical

## The Problem You Identified

Your test results show **7/7 passing (100%)**, but responses feel:
- ✅ Responsive (agent answers)
- ❌ **Mechanical** (rigid, rule-following)
- ❌ **Not intuitive** (users need to be precise)
- ❌ **Not magical** (users have to think/explain)
- ❌ **Not engaging** (users don't want to read technical output)

**What you want**: Users ask casually, get exactly what they need, feel like the agent "just gets it"

---

## Root Cause Analysis

### Issue 1: **Keyword Matching Instead of Intent Understanding**

**Current Approach** (cite_agent/enhanced_ai_agent.py:3287-3473):
```python
financial_keywords = [
    'financial', 'revenue', 'sales', 'income', 'profit', 'earnings', 'loss',
    'company', 'corporation', 'ceo', 'assets', 'liabilities', 'stock',
    # ... 80+ keywords
]

if any(keyword in question_lower for keyword in financial_keywords):
    apis_to_use.append("finsight")  # Trigger financial tools
```

**Why This Feels Mechanical**:
- Simple substring matching: "company" in "compare company logos" → triggers FinSight ❌
- No context awareness: "data processing" could be files OR financial data
- No disambiguation: Agent guesses instead of asking
- Rigid: Either matches or doesn't, no nuance

**Example of Mechanical Behavior**:
```
👤 User: "I'm working on a data processing project"
🤖 Agent: "I key metrics:
           • Revenue: (unavailable)
           • Gross profit: (unavailable)"

❌ Problem: Agent jumped to financial tools without asking "what kind of data?"
```

---

### Issue 2: **Tool-First Thinking vs. User-First Thinking**

**Current System Prompt** (enhanced_ai_agent.py:1115-1125):
```python
intro = (
    "You are Cite Agent, a research and analysis assistant with access to:\n"
    "• Persistent shell (Python, R, SQL, Bash)\n"
    "• File operations (read, write, edit, search)\n"
    "• Academic papers (Archive API - 200M+ papers)\n"
    "• Financial data (FinSight API - SEC filings)\n"
    "• Web search\n\n"
    "Communication style: Be natural, direct, and helpful."
)
```

**Why This Feels Mechanical**:
- Identity is **defined by tools** ("assistant with access to...")
- Lists capabilities like a spec sheet
- "Be natural" is vague and abstract
- No guidance on **understanding user intent**
- No examples of good vs. bad responses

**Comparison**:

| Mechanical Agent | Magical Agent |
|-----------------|---------------|
| "I am an assistant with access to shell, files, APIs..." | "I help you get stuff done - whether it's research, coding, or understanding data" |
| Thinks: "Which tool matches these keywords?" | Thinks: "What is the user really trying to achieve?" |
| Shows tool names: "FinSight API returned..." | Hides tools: "I found Apple's revenue for you..." |
| Executes commands rigidly | Anticipates next steps |

---

### Issue 3: **No Clarification Strategy**

**Current Behavior**:
- Agent sees ambiguous query ("data processing project")
- Agent makes a guess (financial data? file data?)
- Agent executes tools based on guess
- User gets wrong result

**What's Missing**:
- No detection of ambiguity
- No clarification questions
- No "sensing" of user intent from context
- No asking "what kind of X?"

**Example - Current**:
```
👤 User: "I'm processing data for a project"
🤖 Agent: [Guesses financial → triggers FinSight → returns revenue metrics]
😞 User: "No, I meant CSV files..."
```

**Example - Magical**:
```
👤 User: "I'm processing data for a project"
🤖 Agent: "Cool! What kind of data - financial reports, CSV files,
           database exports, or something else? I can help either way!"
😊 User: "CSV files with user data"
🤖 Agent: "Perfect! Want to see what Python libraries would work best,
           or do you have code you'd like me to review?"
```

---

### Issue 4: **Technical Language Leaking to Users**

**Current Responses Show**:
- Tool names: "FinSight GET calc/I/grossProfit"
- Backend errors: "HTTP 500"
- Technical paths: "/home/phyrexian/Downloads/..."
- API internals: "(value unavailable)"

**Why This Feels Mechanical**:
- Exposes implementation details
- Users don't care about backend architecture
- Breaks immersion ("I'm talking to a server?")
- Feels like debugging output, not conversation

**Example - Current** (from your Test 6):
```
🤖 Agent: "I key metrics:
           • Revenue: (value unavailable)
           • Grossprofit: (value unavailable)

           _Data sources: FinSight GET calc/I/grossProfit – error (HTTP 500)..."
```

❌ Problems:
1. "FinSight GET calc/I/grossProfit" - user doesn't know what this means
2. "HTTP 500" - backend error leaked to user
3. "(value unavailable)" - technical status message
4. Response irrelevant to user's question about general data processing

**Example - Magical**:
```
🤖 Agent: "I'm not sure if you mean financial data or general files.
           Could you clarify? I can help with:
           • Financial analysis (company reports, stock data)
           • File processing (CSV, JSON, databases)
           • Something else?"
```

✅ Benefits:
1. No technical jargon
2. Acknowledges uncertainty
3. Offers clear choices
4. Natural language

---

### Issue 5: **Rigid Rules Instead of Natural Conversation**

**Current System Prompt Rules** (enhanced_ai_agent.py:1153-1158):
```python
"CONCISE RESPONSE STYLE:",
"• Direct answers - state result, minimal elaboration",
"• NO code blocks showing bash/python commands unless explicitly asked",
"• NO 'Let me check...' preambles",
"• File listings: Max 5-10 items (filtered to query)",
"• Balance: complete but concise"
```

**Why This Feels Mechanical**:
- Rules are **constraints**, not guidance
- "NO X" language is restrictive
- Arbitrary limits (5-10 items)
- Doesn't teach agent **why** to be concise
- No guidance on **when** to break rules

**Example Problem**:
- Rule says: "NO 'Let me check...' preambles"
- Result: Agent jumps to answer without signaling what it's doing
- User experience: Feels abrupt, not conversational

**Better Approach**:
- Instead of "NO preambles", guide: "Show intent naturally - 'I'll search for that file' is fine, but avoid repetitive phrases"
- Instead of "Max 5-10 items", guide: "Show most relevant items first, offer to show more if needed"
- Instead of rigid rules, give **principles**: clarity, brevity, helpfulness

---

### Issue 6: **No Anticipation of User Needs**

**Current Behavior**:
- Agent answers exactly what was asked
- Stops there
- Waits for next question

**Magical Behavior**:
- Agent answers what was asked
- **Anticipates** what user might want next
- Offers relevant follow-ups

**Example - Current**:
```
👤 User: "What's in this directory?"
🤖 Agent: "Workspace root: /path/to/project

           Here are the first entries:
           - file1.py (file)
           - file2.js (file)
           - tests (directory)
           ..."

[Conversation ends, waiting for next question]
```

**Example - Magical**:
```
👤 User: "What's in this directory?"
🤖 Agent: "I see 20 Python files, 3 config files, and a tests directory.

           Looks like a Python project - want me to:
           • Explain what the project does?
           • Check if tests are passing?
           • Look at a specific file?"

[Agent anticipates next likely questions]
```

---

## What "Magical" Feels Like

### Characteristics of Magical Responses:

1. **Intent Understanding**
   - Agent understands **what user wants to achieve**, not just what they said
   - "Process data" → Agent asks "What kind of data?" instead of guessing

2. **Natural Clarification**
   - Agent asks questions casually when context is unclear
   - No rigid forms or technical prompts

3. **Anticipation**
   - Agent thinks "What will user likely want next?"
   - Offers relevant next steps proactively

4. **Hiding Complexity**
   - User doesn't see backend errors, API names, technical paths
   - Agent handles errors gracefully: "I couldn't fetch that data right now"

5. **Conversational Tone**
   - Sounds like a helpful human, not a chatbot
   - Uses casual language: "Cool!", "Got it", "Makes sense"
   - Varies phrasing instead of templates

6. **Relevance**
   - Every part of the response is directly relevant to user's question
   - No tangential information
   - No showing tools/processes unless user asks

---

## Concrete Improvements

### A. Replace Keyword Matching with Intent Detection

**Instead of**:
```python
if any(keyword in question_lower for keyword in financial_keywords):
    apis_to_use.append("finsight")
```

**Use Intent Heuristics**:
```python
def detect_intent(question: str, conversation_history: list) -> dict:
    """
    Detect user intent considering context and conversation history
    Returns: {
        "primary_intent": "get_information" | "clarify_ambiguity" | "perform_action",
        "domain": "financial" | "research" | "files" | "unclear",
        "confidence": 0.0-1.0,
        "clarification_needed": bool,
        "suggested_clarification": str
    }
    """

    # Example logic:
    question_lower = question.lower()

    # Strong financial signals (require stock ticker OR company name + financial term)
    has_ticker = re.search(r'\b[A-Z]{1,5}\b', question)  # AAPL, MSFT
    has_company = any(company in question for company in ["apple", "microsoft", "tesla"])
    has_financial_term = any(term in question_lower for term in ["revenue", "earnings", "profit"])

    if (has_ticker or (has_company and has_financial_term)):
        return {
            "primary_intent": "get_information",
            "domain": "financial",
            "confidence": 0.9,
            "clarification_needed": False
        }

    # Ambiguous "data" - could be files OR financial
    if "data" in question_lower and "process" in question_lower:
        # Check conversation history for context
        recent_context = " ".join(msg["content"] for msg in conversation_history[-3:])

        if any(term in recent_context.lower() for term in ["csv", "file", "json", "database"]):
            # Previous context indicates file processing
            return {
                "primary_intent": "perform_action",
                "domain": "files",
                "confidence": 0.7,
                "clarification_needed": False
            }

        # No clear context - CLARIFY
        return {
            "primary_intent": "clarify_ambiguity",
            "domain": "unclear",
            "confidence": 0.3,
            "clarification_needed": True,
            "suggested_clarification": "What kind of data are you working with - financial reports, files (CSV/JSON), database exports, or something else?"
        }
```

**Benefits**:
- Context-aware (uses conversation history)
- Confidence scores (knows when uncertain)
- Explicit clarification strategy
- Stricter matching (requires ticker OR company+financial term)

---

### B. Rewrite System Prompt for Intent Understanding

**Current Prompt** (Tool-focused):
```
You are Cite Agent, a research and analysis assistant with access to:
• Persistent shell (Python, R, SQL, Bash)
• File operations (read, write, edit, search)
• Academic papers (Archive API - 200M+ papers)
• Financial data (FinSight API - SEC filings)
• Web search

Communication style: Be natural, direct, and helpful.
```

**Improved Prompt** (Intent-focused):
```
You are Cite, a helpful AI partner that helps users get things done.

Your goal: Understand what the user is trying to achieve, then help them get there efficiently.

Core principles:
1. UNDERSTAND INTENT FIRST
   - What is the user really trying to do?
   - Are they exploring, analyzing, creating, or debugging?
   - Is context clear, or should you ask a clarifying question?

2. ASK WHEN UNCLEAR
   - If "data processing" is mentioned without context → Ask: "What kind of data?"
   - If request is vague → Offer 2-3 specific options
   - Better to clarify once than guess wrong

3. BE CONVERSATIONAL
   - Sound like a helpful colleague, not a chatbot
   - Use natural language: "Cool!", "Makes sense", "Got it"
   - Vary phrasing - don't repeat templates
   - Example: Instead of "Executing command..." say "Let me check that for you"

4. HIDE TECHNICAL DETAILS
   - Users don't care about API names, backend errors, or technical paths
   - Bad: "FinSight GET calc/I/grossProfit returned HTTP 500"
   - Good: "I couldn't fetch that data right now - want to try something else?"

   - Bad: "Workspace root: /home/user/long/technical/path"
   - Good: "I see 20 Python files and a tests directory in your project"

5. ANTICIPATE NEXT STEPS
   - After answering, think: "What will user likely want next?"
   - Offer 2-3 relevant follow-ups
   - Example: "I found 20 Python files - want me to explain what the project does,
     or check if tests are passing?"

6. MATCH USER'S ENERGY
   - Casual question → Casual answer
   - Technical question → Can be more detailed
   - User frustrated → Be extra helpful and patient

TOOLS YOU CAN USE (hide these from user):
- Shell commands for file operations
- Archive API for research papers
- FinSight API for financial data
- Web search

IMPORTANT: Only use financial tools when user EXPLICITLY mentions:
- Stock ticker (AAPL, MSFT)
- Company name + financial term ("Apple revenue", "Microsoft earnings")
- Financial metrics ("P/E ratio", "balance sheet")

DO NOT trigger financial tools for:
- General "data processing" (ask what kind)
- "Company" without financial context (could mean software company)
- "Project" or "analysis" without specifics

When unsure → ASK instead of guessing!
```

**Key Changes**:
1. Identity: "Helpful partner" not "assistant with tools"
2. Principles over rules
3. Explicit intent understanding guidance
4. Clarification strategy built-in
5. Natural conversation examples
6. Technical detail hiding
7. Stricter tool triggering (prevents Test 6 issue)

---

### C. Add Clarification Response Templates

**Add to agent code**:
```python
def generate_clarification_response(ambiguous_term: str, options: list) -> str:
    """
    Generate a natural clarification question when intent is unclear

    Args:
        ambiguous_term: The unclear term ("data", "company", "process")
        options: List of possible interpretations

    Returns:
        Natural clarification question
    """

    templates = [
        f"Just to clarify - when you say '{ambiguous_term}', do you mean {' or '.join(options)}?",
        f"I can help with {ambiguous_term}! Are you thinking of {options[0]}, {options[1]}, or something else?",
        f"Want to make sure I understand - is this about {options[0]} or {options[1]}?",
    ]

    # Pick template based on hash (consistent but varied)
    template_idx = hash(ambiguous_term) % len(templates)
    return templates[template_idx]

# Usage example:
if intent["clarification_needed"]:
    if "data" in question_lower:
        response = generate_clarification_response(
            "data",
            ["financial reports", "files (CSV/JSON)", "database data"]
        )
        return response
```

---

### D. Format Responses to Be Scannable

**Current Response Style** (from Test 2):
```
Workspace root: /home/phyrexian/Downloads/llm_automation/project_portfolio/Cite-Agent

Here are the first entries I can see:

- __pycache__ (directory)
- cite_agent (directory)
- cite-agent-api (directory)
- tests (directory)
- file1.py (file)
- file2.py (file)
... and 14 more
```

**Issues**:
- Long technical path shown first
- Mixture of Python internals (__pycache__) and useful files
- No context about what project is
- Not scannable (user has to read line by line)

**Magical Response**:
```
I see a Python project with:
• Main code: cite_agent/
• API backend: cite-agent-api/
• Tests: tests/
• 20 Python files total

Want me to explain what the project does, or look at something specific?
```

**Benefits**:
- Starts with overview (not technical path)
- Groups related items
- Hides Python internals (__pycache__)
- Scannable (bullet points, grouping)
- Anticipates next question

---

### E. Add Response Quality Checks

**Before sending response to user, check**:

```python
def validate_response_quality(response: str, user_question: str) -> dict:
    """
    Check if response meets quality standards for magical UX

    Returns:
        {
            "passes": bool,
            "issues": list of str,
            "suggestions": list of str
        }
    """
    issues = []
    suggestions = []

    # Check 1: Does response show technical internals?
    technical_leaks = [
        "HTTP 500", "HTTP 404", "API error",
        "FinSight GET", "calc/I/",
        "/home/user/", "/home/phyrexian/",
        "unavailable)", "(value unavailable"
    ]
    for leak in technical_leaks:
        if leak in response:
            issues.append(f"Technical detail leaked: '{leak}'")
            suggestions.append("Replace with user-friendly message")

    # Check 2: Is response relevant to question?
    question_keywords = set(re.findall(r'\b\w{4,}\b', user_question.lower()))
    response_keywords = set(re.findall(r'\b\w{4,}\b', response.lower()))

    overlap = len(question_keywords & response_keywords)
    if overlap == 0 and len(question_keywords) > 0:
        issues.append("Response may not be relevant to question")
        suggestions.append("Check if wrong tools were triggered")

    # Check 3: Is response too verbose?
    if len(response) > 800 and response.count('\n') < 3:
        issues.append("Response is long wall of text")
        suggestions.append("Break into paragraphs or bullet points")

    # Check 4: Does response end with a question or offer?
    ends_with_offer = any(response.rstrip().endswith(phrase) for phrase in [
        "?", "want me to", "would you like", "need help with"
    ])
    if not ends_with_offer and len(response) > 100:
        suggestions.append("Consider ending with next-step offer")

    return {
        "passes": len(issues) == 0,
        "issues": issues,
        "suggestions": suggestions
    }

# Usage in agent:
response = generate_llm_response(...)
quality_check = validate_response_quality(response, user_question)

if not quality_check["passes"]:
    # Log issues for improvement
    logger.warning(f"Response quality issues: {quality_check['issues']}")

    # If critical issues, regenerate with stricter prompt
    if "Technical detail leaked" in str(quality_check["issues"]):
        response = regenerate_response_without_technical_details(...)
```

---

## Before/After Examples

### Example 1: Data Processing Ambiguity

**Before (Mechanical)** - Your Test 6:
```
👤 User: "The project I mentioned is for data processing"
🤖 Agent: "I key metrics:
           • Revenue: (value unavailable)
           • Grossprofit: (value unavailable)

           _Data sources: FinSight GET calc/I/grossProfit – error (HTTP 500)..."
```

❌ Problems:
- Wrong tools triggered (financial instead of files)
- Technical error shown to user
- Response irrelevant to question
- No clarification asked

**After (Magical)**:
```
👤 User: "The project I mentioned is for data processing"
🤖 Agent: "Just to clarify - what kind of data processing? I can help with:
           • Financial analysis (company reports, SEC filings)
           • File processing (CSV, JSON, Excel)
           • Database operations (SQL, ETL)
           • Something else?

           Let me know and I'll point you in the right direction!"
```

✅ Benefits:
- Recognizes ambiguity
- Asks naturally
- Offers clear options
- Casual tone ("Let me know...")
- No tools triggered until clarified

---

### Example 2: File Listing

**Before (Mechanical)**:
```
👤 User: "What's in this directory?"
🤖 Agent: "Workspace root: /home/phyrexian/Downloads/llm_automation/project_portfolio/Cite-Agent

           Here are the first entries I can see:

           - __pycache__ (directory)
           - .git (directory)
           - cite_agent (directory)
           - cite-agent-api (directory)
           - tests (directory)
           - README.md (file)
           - setup.py (file)
           ... and 25 more"
```

❌ Problems:
- Long technical path first
- Shows Python internals (__pycache__, .git)
- Not scannable
- No context about project
- No next-step offer

**After (Magical)**:
```
👤 User: "What's in this directory?"
🤖 Agent: "This looks like a Python agent project! I see:

           📦 Main components:
           • cite_agent/ - Core agent code
           • cite-agent-api/ - Backend API
           • tests/ - Test suite

           📄 Key files:
           • README.md - Documentation
           • setup.py - Installation

           Want me to explain how the project works, or look at something specific?"
```

✅ Benefits:
- Overview first (Python agent project)
- Grouped logically (components vs files)
- Hides internals (__pycache__)
- Scannable (emojis, bullets, grouping)
- Anticipates next question
- Conversational tone

---

### Example 3: Technical Error Handling

**Before (Mechanical)**:
```
👤 User: "What's Apple's revenue?"
🤖 Agent: "Error: FinSight API returned HTTP 500

           Data sources: FinSight GET /api/v1/finance/calc/AAPL/revenue – timeout

           Request ID: a7b3c2d1
           Timestamp: 2025-01-15T14:32:01Z"
```

❌ Problems:
- Backend error shown to user
- Technical details (HTTP 500, API path)
- Request ID meaningless to user
- No alternative offered

**After (Magical)**:
```
👤 User: "What's Apple's revenue?"
🤖 Agent: "I'm having trouble fetching Apple's financial data right now -
           the data source seems slow.

           Want me to:
           • Try searching for recent news about Apple's earnings?
           • Check a different metric?
           • Try again in a moment?"
```

✅ Benefits:
- Plain language ("having trouble")
- Doesn't show backend details
- Offers alternatives
- Keeps conversation flowing
- User stays in flow state

---

### Example 4: Ambiguous "Company"

**Before (Mechanical)**:
```
👤 User: "I'm analyzing company data"
🤖 Agent: [Triggers FinSight]
           "Which company? Please provide a stock ticker (e.g., AAPL, MSFT)"
```

❌ Problems:
- Assumed financial domain
- "company data" could be employee data, product data, code structure
- Technical ask (stock ticker)

**After (Magical)**:
```
👤 User: "I'm analyzing company data"
🤖 Agent: "Just to make sure I understand - is this:
           • Financial company data (revenue, stock info)?
           • Internal company data (employees, products)?
           • Something else?

           I can help either way!"
```

✅ Benefits:
- Recognizes ambiguity
- Doesn't assume financial
- Offers clear choices
- Casual reassurance ("I can help either way!")

---

## Implementation Roadmap

### Phase 1: Quick Wins (1-2 hours)
1. ✅ Add intent detection with confidence scores
2. ✅ Add clarification templates
3. ✅ Filter technical details from responses
4. ✅ Update system prompt with intent-focused guidance

### Phase 2: Response Quality (2-4 hours)
5. Add response quality validation
6. Improve response formatting (grouping, bullets, scannable)
7. Add next-step anticipation logic
8. Hide technical paths and API names

### Phase 3: Conversational Polish (4-6 hours)
9. Add natural language variation (not templates)
10. Improve error message handling
11. Add context retention across turns
12. Test and refine conversational tone

---

## How to Validate Improvements

### Test Suite for "Magical" Quality

```python
class TestMagicalResponses:

    async def test_ambiguity_detection(self):
        """Agent should ask clarifying questions for ambiguous input"""

        response = await agent.ask("I'm working on data processing")

        # Should ask clarification
        assert any(phrase in response.lower() for phrase in [
            "what kind of", "clarify", "do you mean", "is this about"
        ])

        # Should NOT trigger tools yet
        assert "revenue" not in response.lower()
        assert "HTTP" not in response

    async def test_no_technical_leaks(self):
        """Agent should hide technical details from user"""

        # Simulate API error
        response = await agent.ask("What's Apple's revenue?")  # Assume API fails

        # Should NOT show these
        assert "HTTP 500" not in response
        assert "HTTP 404" not in response
        assert "API error" not in response
        assert "timeout" not in response.lower() or "slow" in response.lower()  # "slow" is okay

        # Should offer alternatives
        assert "?" in response  # Ends with question/offer

    async def test_scannable_responses(self):
        """Responses should be scannable (bullets, grouping, not walls of text)"""

        response = await agent.ask("What's in this directory?")

        # Should have structure
        assert response.count('\n') >= 3  # Multiple lines
        assert '•' in response or '-' in response or '*' in response  # Bullets

        # Should NOT have long technical paths in first line
        first_line = response.split('\n')[0]
        assert len(first_line) < 100
        assert "/home/" not in first_line

    async def test_anticipation(self):
        """Agent should anticipate next steps"""

        response = await agent.ask("What Python files are here?")

        # Should end with offer or question
        assert response.rstrip().endswith('?') or \
               any(phrase in response.lower() for phrase in [
                   "want me to", "would you like", "need help", "should i"
               ])

    async def test_conversational_tone(self):
        """Agent should sound natural, not robotic"""

        response = await agent.ask("Thanks for your help!")

        # Should use casual language
        casual_phrases = [
            "no problem", "happy to help", "anytime", "glad", "sure thing",
            "you bet", "of course"
        ]
        assert any(phrase in response.lower() for phrase in casual_phrases)

        # Should NOT use robotic language
        robotic_phrases = [
            "affirmative", "executing", "processing request", "acknowledged"
        ]
        assert not any(phrase in response.lower() for phrase in robotic_phrases)
```

---

## Expected Results After Improvements

### Before:
- ✅ 7/7 tests passing (100%)
- ❌ Responses feel mechanical
- ❌ Users need to be precise
- ❌ Technical details leak
- ❌ Wrong tools triggered

### After:
- ✅ 7/7 tests passing (100%)
- ✅ **Responses feel natural and intuitive**
- ✅ **Users can ask casually**
- ✅ **Agent asks when unclear**
- ✅ **No technical details shown**
- ✅ **Right tools triggered (or clarification asked)**
- ✅ **Users want to keep talking to it**

---

## Summary

**The Core Issue**: Agent is technically competent but not user-friendly

**Root Causes**:
1. Keyword matching → Brittle, no context
2. Tool-first thinking → Shows internals to users
3. No clarification strategy → Guesses wrong
4. Technical language → Breaks immersion
5. Rigid rules → Feels robotic
6. No anticipation → Just answers, doesn't help further

**Solution**: Shift from "tool-using assistant" to "intent-understanding partner"

**Key Changes**:
- Intent detection with confidence scores
- Clarification when ambiguous
- Hide all technical details
- Natural conversation prompts
- Anticipate next steps
- Response quality validation

**Result**: Users ask casually, get exactly what they need, feel like agent "just gets it" ✨
