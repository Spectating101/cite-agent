# File Integration Plan - Building Complete Research Assistant

## Analysis Summary
- **Total files in cite_agent/:** 40 Python files
- **Currently used:** 13 files (33%)
- **Unused but valuable:** 11 files (27%)
- **Redundant/Low value:** 16 files (40%)

---

## 🎯 PRIORITY 1: Research Assistant Core (INTEGRATE IMMEDIATELY)

### 1. adaptive_providers.py (413 lines) ⭐⭐⭐⭐⭐
**Why Critical:**
- Has `DATA_ANALYSIS` query type built in!
- `AdaptiveProviderSelector` - chooses best LLM for task
- Performance profiling for each provider

**Features:**
```python
class QueryType(Enum):
    ACADEMIC_PAPER = "academic_paper"
    FINANCIAL_DATA = "financial_data"
    DATA_ANALYSIS = "data_analysis"      # ← WE NEED THIS!
    CODE_GENERATION = "code_generation"
    SHELL_EXECUTION = "shell_execution"
```

**Integration:**
- Add to `enhanced_ai_agent.py` imports
- Use `AdaptiveProviderSelector` to route queries
- Replace current simple routing with adaptive selection

**Impact:** Automatically chooses best LLM for statistical analysis vs paper search

---

### 2. ascii_plotting.py (296 lines) ⭐⭐⭐⭐⭐
**Why Critical:**
- Visualize data in terminal!
- Bar charts, line plots, scatter plots
- Perfect for data analysis output

**Features:**
```python
class ASCIIPlotter:
    def plot_line(x, y, title)      # Line charts
    def plot_bar(categories, values) # Bar charts
    def plot_scatter(x, y)          # Scatter plots
```

**Integration:**
- Add to tool_executor.py as new tools
- Use when showing regression results, correlations
- Auto-generate plots for dataset analysis

**Impact:** Professor asks "plot hours vs test scores" → shows ASCII scatter plot

---

### 3. execution_safety.py (329 lines) ⭐⭐⭐⭐⭐
**Why Critical:**
- Safety validator for R/Python code execution
- Pre-approval for dangerous commands
- Audit logging

**Features:**
```python
class CommandClassification(Enum):
    SAFE = "safe"          # read files, queries
    WRITE = "write"        # write files
    DANGEROUS = "dangerous" # rm -rf, format disk
    BLOCKED = "blocked"    # never execute

class CommandExecutionValidator:
    def classify_command(cmd: str)
    def require_approval(cmd: str)
```

**Integration:**
- Wrap all shell_command executions
- Validate before executing R scripts
- Log all data modifications

**Impact:** Prevents accidental `rm -rf /` in R scripts

---

### 4. project_detector.py (148 lines) ⭐⭐⭐⭐
**Why Important:**
- Detects if user is in R project, Jupyter notebook, etc.
- Provides context about current environment
- Helpful for research workflow

**Features:**
```python
class ProjectDetector:
    def detect_project() -> Dict:
        # Detects: R projects, Python venvs, Jupyter notebooks
        # Returns: {"type": "r_project", "files": [...]}
```

**Integration:**
- Run on initialization in enhanced_ai_agent
- Use to provide smart suggestions
- Auto-detect .Rproj files

**Impact:** Agent knows "you're in an R project" → suggests R solutions

---

## 🔧 PRIORITY 2: Production Quality (INTEGRATE NEXT)

### 5. self_healing.py (418 lines) ⭐⭐⭐⭐
**Features:**
- Auto-recovery from provider failures
- Fallback to backup providers
- Failure tracking and learning

**Integration:**
- Replace manual error handling
- Add to enhanced_ai_agent initialization
- Auto-switch providers on rate limits

**Impact:** When Cerebras hits 429, auto-switches to backup key

---

### 6. rate_limiter.py (298 lines) ⭐⭐⭐
**Features:**
- Better rate limiting than current
- Per-tier configurations
- Token and request tracking

**Integration:**
- Replace basic rate limiting
- Track usage per API key
- Prevent quota exhaustion

---

### 7. prometheus_metrics.py (376 lines) ⭐⭐⭐
**Features:**
- Production monitoring
- Metrics export for Grafana
- Query performance tracking

**Integration:**
- Add metrics collection to key operations
- Optional feature (can disable)
- Useful for production deployment

---

### 8. workflow_integration.py (274 lines) ⭐⭐⭐
**Features:**
- Paper library management
- Save papers to local library
- Reduce context switching

**Integration:**
- Merge with existing workflow.py
- Add library management tools
- Auto-save interesting papers

---

## 🤔 PRIORITY 3: Review Before Integration

### 9. function_tools.py (409 lines)
**Check:** Might have tool definitions we're missing
**Action:** Compare with current TOOLS in tool_executor.py

### 10. unified_observability.py (373 lines)
**Check:** Consolidates observability, circuit breaker, metrics
**Action:** If better than separate files, replace them

---

## 🗑️ PRIORITY 4: Consolidate or Remove

### Redundant CLI Files (pick one best, remove others):
- cli.py (1122 lines) - feature-rich
- cli_enhanced.py (207 lines) - minimal
- cli_conversational.py (404 lines) - conversational
- cli_workflow.py (275 lines) - workflow focused

**Action:** Keep cli_workflow.py (most features), remove others

### Redundant Auth/Backend:
- account_client.py - account provisioning
- auth.py - authentication manager
- backend_only_client.py - backend-only mode
- agent_backend_only.py - duplicate of above

**Action:** Keep account_client.py + auth.py, remove backend_only versions

### UI Files:
- ui.py (174 lines) - terminal UI
- streaming_ui.py (256 lines) - streaming chat UI
- dashboard.py (339 lines) - web dashboard

**Action:** Keep streaming_ui.py for chat, dashboard.py for analytics, remove ui.py

### Low Priority:
- session_manager.py - basic session management (we have session_memory_manager)
- function_calling_integration.py - disabled anyway

**Action:** Remove

---

## 📋 Integration Order

### Phase 1: Data Analysis Core (TODAY)
1. ✅ Read adaptive_providers.py
2. ✅ Read ascii_plotting.py
3. ✅ Read execution_safety.py
4. ✅ Integrate into enhanced_ai_agent.py
5. ✅ Add new tools to tool_executor.py
6. ✅ Test with: "Load /tmp/data.csv and plot the correlation"

### Phase 2: Production Quality (TOMORROW)
7. ✅ Integrate self_healing.py
8. ✅ Integrate rate_limiter.py
9. ✅ Test failover and rate limiting

### Phase 3: Research Workflow (DAY 3)
10. ✅ Integrate project_detector.py
11. ✅ Merge workflow_integration.py with workflow.py
12. ✅ Test full research workflow

### Phase 4: Cleanup (DAY 4)
13. ✅ Consolidate CLI files
14. ✅ Remove redundant files
15. ✅ Update imports and dependencies
16. ✅ Test everything still works

---

## Expected Outcome

**Before Integration:**
- 40 files, 13 used (33%)
- Missing: Data analysis, plotting, safety validation
- Research readiness: 60%

**After Integration:**
- ~25 files (consolidated)
- All valuable features integrated
- Research readiness: 95%+

**New Capabilities:**
1. ✅ Load CSV/Excel datasets
2. ✅ ASCII plotting for data visualization
3. ✅ Safe R/Python code execution
4. ✅ Auto-detect research project type
5. ✅ Smart provider selection per task
6. ✅ Self-healing on failures
7. ✅ Better rate limiting
8. ✅ Production monitoring

---

## Test Queries After Integration

Professor should be able to ask:

1. "Load /data/study.csv and show me a scatter plot of hours vs scores"
   → Loads data, creates ASCII scatter plot

2. "Run this R regression: lm(score ~ hours, data=df)"
   → Safety validates, executes R code, shows results

3. "I'm working in an R project. What packages do I have installed?"
   → Detects R project, lists packages

4. "Analyze correlations in my dataset and visualize them"
   → Runs correlation, plots as heatmap (ASCII)

5. "Compare performance of 3 different regression models"
   → Runs all 3, shows comparison table + plots

All should work after integration!
