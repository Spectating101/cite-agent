# Pre-Ship Critical Path Testing Plan
**Version**: 1.5.7 Pre-Release Testing  
**Date**: November 20, 2024  
**Objective**: Test previously untested tool categories before Windows testing and PyPI ship

---

## Executive Summary

### Coverage Status (Before This Testing)
- **Total Tools**: 39
- **Tested**: 11 (28%)
- **Untested**: 28 (72%)

### Critical Gaps Identified
1. **Qualitative Analysis**: 0/5 tools tested (0%) - **UNIQUE DIFFERENTIATOR**
2. **Literature Synthesis**: 1/8 tools tested (12.5%) - **CORE RESEARCH FEATURE**
3. **Advanced Statistics**: 4/13 tools tested (31%)
4. **Web Search**: 0/1 tools tested (0%) - **FALLBACK MECHANISM**
5. **R Code Execution**: 0/1 tools tested (0%)

### Why This Matters
- **Qualitative analysis suite** is cite-agent's unique selling point (competitors don't offer this)
- **Literature synthesis tools** are critical for academic researchers (core use case)
- **Advanced stats** are differentiators for serious research work
- If these break, users lose the primary value propositions

---

## Test Plan Overview

### Phase 1: Qualitative Analysis Tools (15-20 min)
**Tools to test**: `load_transcript`, `create_code`, `code_segment`, `list_codes`, `extract_themes`

**Why critical**: This is the **only AI research assistant** that offers qualitative coding. If broken, cite-agent loses its unique competitive advantage.

### Phase 2: Literature Synthesis Tools (15-20 min)
**Tools to test**: `find_related_papers`, `add_paper`, `export_to_zotero`, `extract_lit_themes`, `find_research_gaps`, `synthesize_literature`, `export_lit_review`

**Why critical**: Core academic workflow. Researchers use cite-agent specifically for literature review automation.

### Phase 3: Advanced Statistics (10-15 min)
**Tools to test**: `run_mediation`, `run_moderation`, `run_pca`, `run_factor_analysis`, `calculate_sample_size`, `calculate_power`, `calculate_mde`

**Why critical**: Differentiates from basic calculator apps. PhD students need these for dissertations.

### Phase 4: Web Search & R Execution (5-10 min)
**Tools to test**: `web_search`, `run_r_code`

**Why critical**: Web search is the fallback when Archive API is down. R execution is promised feature.

### Phase 5: Cross-Domain Workflows (15-20 min)
**Test combinations**: Qualitative → Stats, Literature → Analysis, Multi-tool workflows

**Why critical**: Real users don't use single tools—they chain them together. Workflow engine must handle complex sequences.

---

## Detailed Test Cases

### PHASE 1: Qualitative Analysis Tools

#### Test 1.1: Load and Code Transcript
```bash
# Create sample transcript
cd ~/Downloads/data
cat > interview_transcript.txt << 'EOF'
Interviewer: Can you tell me about your experience with remote work?

Participant 1: I find remote work very isolating. I miss the casual conversations with colleagues at the office.

Participant 2: For me, remote work has been liberating. I can focus without constant interruptions and have more time with my family.

Participant 1: But the lack of clear boundaries between work and home life is really stressful. I'm working longer hours now.

Participant 3: I agree about the boundaries issue. However, I've learned to set strict schedules, and it's improved my work-life balance significantly.

Interviewer: How do you handle team collaboration remotely?

Participant 2: Video calls help, but they're exhausting. I prefer async communication like emails or Slack.

Participant 3: I think the key is having the right tools and establishing clear communication norms with your team.
EOF

# Test load and extract themes
cite-agent "Load the transcript from interview_transcript.txt and extract the main themes"
```

**Expected behavior**:
- ✅ Successfully loads transcript file
- ✅ Identifies themes (e.g., "isolation", "work-life boundaries", "communication challenges", "productivity")
- ✅ Clean formatting (no LaTeX, no stray backticks)
- ✅ Actionable output for researcher

**Red flags**:
- ❌ File not found errors
- ❌ Transcript not processed
- ❌ No themes extracted
- ❌ Workflow fails to complete

---

#### Test 1.2: Create Codes and Apply to Segments
```bash
cite-agent "Create a qualitative code called 'work-life-balance' with description 'Statements about boundaries between work and personal life'. Then code the segments in interview_transcript.txt that match this theme."
```

**Expected behavior**:
- ✅ Creates code with label and description
- ✅ Applies code to relevant text segments
- ✅ Shows which segments were coded
- ✅ Maintains context between steps (workflow sequencing)

**Red flags**:
- ❌ Code creation fails
- ❌ Segments not identified
- ❌ Context lost between create_code and code_segment steps
- ❌ Workflow engine doesn't sequence properly

---

#### Test 1.3: List Codes and Generate Codebook
```bash
cite-agent "List all qualitative codes created so far, then generate a comprehensive codebook summarizing the coding scheme"
```

**Expected behavior**:
- ✅ Lists all codes with descriptions
- ✅ Generates structured codebook
- ✅ Professional formatting for academic use
- ✅ Workflow handles multi-step process

**Red flags**:
- ❌ No codes found (state management issue)
- ❌ Codebook not generated
- ❌ Unprofessional output formatting

---

### PHASE 2: Literature Synthesis Tools

#### Test 2.1: Find Related Papers
```bash
cite-agent "Search for papers related to 'Attention Is All You Need' and show me 3 related papers"
```

**Expected behavior**:
- ✅ Uses Archive API to find related papers
- ✅ Returns relevant transformer/attention papers
- ✅ Shows titles, authors, years
- ✅ Clean formatting

**Red flags**:
- ❌ API connection fails
- ❌ No papers returned
- ❌ Irrelevant results
- ❌ Tool not recognized

---

#### Test 2.2: Build Paper Library and Synthesize
```bash
cite-agent "Search for 5 papers about 'neural machine translation', add them to my library, then synthesize them into a literature review covering key methods and findings"
```

**Expected behavior**:
- ✅ Searches papers (search_papers)
- ✅ Adds to library (add_paper × 5)
- ✅ Synthesizes into coherent review (synthesize_literature)
- ✅ Professional academic writing
- ✅ Workflow sequences correctly: search → add → synthesize

**Red flags**:
- ❌ Papers not added to library
- ❌ Synthesis doesn't use library papers
- ❌ Context lost between steps
- ❌ Output is just concatenated abstracts (not synthesis)
- ❌ Workflow doesn't sequence properly

---

#### Test 2.3: Extract Themes and Find Gaps
```bash
cite-agent "From the papers in my library about neural machine translation, extract the main research themes and identify research gaps that haven't been addressed"
```

**Expected behavior**:
- ✅ Accesses library from previous test (state persistence)
- ✅ Extracts themes (extract_lit_themes)
- ✅ Identifies research gaps (find_research_gaps)
- ✅ Actionable insights for researcher
- ✅ Workflow handles multi-step analysis

**Red flags**:
- ❌ Library empty (state lost)
- ❌ Themes not extracted
- ❌ Gaps not identified
- ❌ Generic output (not specific to papers)

---

#### Test 2.4: Export to Zotero
```bash
cite-agent "Export my paper library to Zotero format and save it to a file"
```

**Expected behavior**:
- ✅ Exports library in valid Zotero format
- ✅ File created successfully
- ✅ All papers included with metadata
- ✅ Ready for import to Zotero

**Red flags**:
- ❌ Export fails
- ❌ Invalid format
- ❌ Missing papers
- ❌ File not created

---

### PHASE 3: Advanced Statistics Tools

#### Test 3.1: Mediation Analysis
```bash
# Create mediation test data
cd ~/Downloads/data
cat > mediation_data.csv << 'EOF'
X,M,Y
1,2,3
2,3,5
3,5,7
4,6,9
5,8,11
6,9,13
7,11,15
8,12,17
9,14,19
10,15,21
EOF

cite-agent "Run a mediation analysis with mediation_data.csv where X is the predictor, M is the mediator, and Y is the outcome. Show me the direct, indirect, and total effects."
```

**Expected behavior**:
- ✅ Loads CSV data
- ✅ Runs mediation analysis (statsmodels or similar)
- ✅ Reports direct effect, indirect effect, total effect
- ✅ Significance tests included
- ✅ Clean number formatting (no excessive decimals)

**Red flags**:
- ❌ Tool not recognized
- ❌ Analysis fails
- ❌ Results incomplete (missing effects)
- ❌ Formatting issues (LaTeX notation, excessive decimals)

---

#### Test 3.2: PCA (Principal Component Analysis)
```bash
# Create PCA test data
cat > pca_data.csv << 'EOF'
var1,var2,var3,var4
2.5,2.4,3.5,3.7
0.5,0.7,1.2,1.5
2.2,2.9,3.1,3.6
1.9,2.2,2.8,3.1
3.1,3.0,4.0,4.2
2.3,2.7,3.3,3.5
2.0,1.6,2.5,2.8
1.0,1.1,1.8,2.1
1.5,1.6,2.2,2.4
1.1,0.9,1.5,1.8
EOF

cite-agent "Run PCA on pca_data.csv and show me the explained variance by each component and the loadings"
```

**Expected behavior**:
- ✅ Runs PCA successfully
- ✅ Shows explained variance percentages
- ✅ Shows component loadings
- ✅ Clean formatting with proper decimals

**Red flags**:
- ❌ Analysis fails
- ❌ Results incomplete
- ❌ Formatting poor

---

#### Test 3.3: Power Analysis
```bash
cite-agent "Calculate the required sample size for a study with expected effect size of 0.5, power of 0.8, and alpha of 0.05 for a two-sample t-test"
```

**Expected behavior**:
- ✅ Runs power analysis (statsmodels.stats.power or similar)
- ✅ Returns required sample size
- ✅ Shows calculation parameters
- ✅ Actionable for researcher

**Red flags**:
- ❌ Tool not found
- ❌ Calculation incorrect
- ❌ No sample size returned

---

### PHASE 4: Web Search & R Execution

#### Test 4.1: Web Search
```bash
cite-agent "Search the web for latest AI breakthroughs in 2024 and summarize the top 3 findings"
```

**Expected behavior**:
- ✅ Performs web search
- ✅ Returns relevant recent results
- ✅ Summarizes findings
- ✅ Clean formatting

**Red flags**:
- ❌ Tool fails
- ❌ No results returned
- ❌ Results irrelevant or outdated

---

#### Test 4.2: R Code Execution
```bash
cite-agent "Write R code to calculate the mean and standard deviation of the vector c(10, 20, 30, 40, 50) and run it to show me the results"
```

**Expected behavior**:
- ✅ Generates R code
- ✅ Executes R code successfully
- ✅ Shows output (mean: 30, sd: 15.81)
- ✅ Clean formatting

**Red flags**:
- ❌ R not available
- ❌ Code doesn't execute
- ❌ Execution errors
- ❌ No output returned

---

### PHASE 5: Cross-Domain Workflow Combinations

#### Test 5.1: Qualitative → Quantitative Pipeline
```bash
cite-agent "Load interview_transcript.txt, extract themes, then create a frequency count of how many times each theme appears across all participants. Visualize this as a bar chart concept (describe the chart)."
```

**Expected behavior**:
- ✅ Loads transcript (load_transcript)
- ✅ Extracts themes (extract_themes)
- ✅ Counts frequencies (run_python_code or analyze_data)
- ✅ Describes visualization (plot_data)
- ✅ Workflow sequences: qualitative → analysis → visualization
- ✅ Context maintained throughout

**Red flags**:
- ❌ Context lost between qualitative and quantitative steps
- ❌ Theme data not passed to analysis step
- ❌ Workflow breaks at tool boundaries
- ❌ No visualization description

---

#### Test 5.2: Literature → Data → Analysis Pipeline
```bash
cite-agent "Search for papers about 'student performance prediction', find the most cited one, then create a mock dataset with 50 students having variables (study_hours, attendance, gpa) and run a regression to predict GPA from study hours and attendance"
```

**Expected behavior**:
- ✅ Searches papers (search_papers)
- ✅ Identifies most cited
- ✅ Generates mock data (run_python_code or create dataset)
- ✅ Runs regression (run_regression)
- ✅ Reports R², coefficients, p-values
- ✅ Complex workflow sequences correctly: research → data generation → analysis
- ✅ Context flows through entire pipeline

**Red flags**:
- ❌ Steps disconnected (agent treats as separate queries)
- ❌ Data not generated
- ❌ Regression doesn't use generated data
- ❌ Workflow engine fails on complex sequences
- ❌ Context window limitations cause information loss

---

#### Test 5.3: Multi-Domain Research Workflow
```bash
cite-agent "I'm researching remote work impact on productivity. First, search for 3 papers on this topic. Then, create a qualitative code for 'productivity factors' and apply it to interview_transcript.txt. Finally, search web for latest 2024 statistics on remote work productivity and synthesize all findings into a short research brief."
```

**Expected behavior**:
- ✅ Literature search (search_papers)
- ✅ Qualitative coding (create_code, code_segment)
- ✅ Web search (web_search) for current data
- ✅ Synthesis across all sources
- ✅ Coherent research brief output
- ✅ **ULTIMATE WORKFLOW TEST**: sequences across all major tool categories
- ✅ Context maintained across 5+ tool invocations

**Red flags**:
- ❌ Agent treats as separate queries (no workflow sequencing)
- ❌ Steps don't connect (e.g., synthesis ignores qualitative coding)
- ❌ Context lost partway through
- ❌ Workflow engine can't handle this complexity
- ❌ Output is disjointed (not synthesized)

---

## Success Criteria

### Minimum Acceptable (Ship Blocker if Not Met)
- ✅ **Qualitative tools**: At least 3/5 tools working (load_transcript, create_code, extract_themes)
- ✅ **Literature tools**: At least 4/7 untested tools working (find_related, add_paper, synthesize, find_gaps)
- ✅ **Workflow sequencing**: Cross-domain workflows complete successfully
- ✅ **No regressions**: Previously working tools still work
- ✅ **Output quality**: Clean formatting (no LaTeX, no stray backticks, smart number formatting)

### Ideal Outcome (High Confidence Ship)
- ✅ **All qualitative tools working** (5/5)
- ✅ **All literature tools working** (7/7 untested)
- ✅ **Advanced stats**: At least 3/7 working (mediation, PCA, power)
- ✅ **Web search**: Working as fallback
- ✅ **R execution**: Working (Python already verified)
- ✅ **Complex workflows**: Multi-domain sequences work flawlessly

### Ship-With-Documentation (Acceptable)
- ✅ Core qualitative + literature + workflow sequencing works
- 📝 Document which advanced stats tools are untested
- 📝 Note R execution may need additional testing
- 📝 Known limitations clearly stated in README

---

## Risk Assessment

### High Risk (Must Test)
1. **Qualitative analysis suite** - Unique differentiator, no fallback
2. **Literature synthesis workflows** - Core academic use case
3. **Cross-domain sequencing** - Real users chain tools together

### Medium Risk (Should Test)
4. **Advanced statistics** - PhD students need these, but basic stats verified
5. **Web search** - Fallback mechanism, but Archive API is primary

### Low Risk (Can Document)
6. **R execution** - Python works, R likely similar
7. **Individual advanced stats** - Can document untested tools

---

## Testing Timeline

**Estimated total**: 60-90 minutes

| Phase | Time | Priority |
|-------|------|----------|
| Phase 1: Qualitative | 15-20 min | 🔴 CRITICAL |
| Phase 2: Literature | 15-20 min | 🔴 CRITICAL |
| Phase 3: Advanced Stats | 10-15 min | 🟡 HIGH |
| Phase 4: Web + R | 5-10 min | 🟡 MEDIUM |
| Phase 5: Cross-Domain | 15-20 min | 🔴 CRITICAL |

**CRITICAL PATH**: Phases 1, 2, 5 (45-60 min)  
**FULL COVERAGE**: All phases (60-90 min)

---

## Post-Testing Actions

### If All Tests Pass
1. ✅ Update test coverage report (28% → 70%+)
2. ✅ Proceed to Windows testing
3. ✅ Ship v1.5.7 to PyPI with confidence
4. ✅ Update README with verified capabilities

### If Issues Found
1. 🔧 Document specific failures
2. 🔧 Assess severity (ship-blocker vs. known limitation)
3. 🔧 Fix critical issues or document limitations
4. 🔧 Re-test affected functionality
5. 🔧 Update KNOWN_ISSUES.md

### If Major Failures
1. ⚠️ Delay ship
2. ⚠️ Debug and fix broken functionality
3. ⚠️ Full regression testing
4. ⚠️ Re-assess v1.5.7 readiness

---

## Notes

- **Why these tests matter**: These are the features that differentiate cite-agent from generic AI assistants
- **Why now**: v1.5.7 includes critical formatting fixes; want to ship with confidence across all major features
- **Why comprehensive**: Real users don't use tools in isolation—they build complex workflows
- **Time investment**: 60-90 minutes of testing prevents hours of user-reported bugs and reputation damage

**Bottom line**: If qualitative analysis or literature synthesis is broken, cite-agent loses its core value proposition. Better to find out now than after PyPI ship.
