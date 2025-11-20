# Cite-Agent Tool Capability Matrix (v1.5.6)

**TOTAL TOOLS: 39**

## 📚 Research & Literature (8 tools)

| Tool | Purpose | Inputs | Outputs | Sequences With |
|------|---------|--------|---------|---------------|
| `search_papers` | Search academic papers via Semantic Scholar | query (str), limit (int) | Paper list with titles, authors, abstracts | → find_related_papers, add_paper, export_to_zotero |
| `find_related_papers` | Find papers related to given paper ID | paper_id (str), limit (int) | Related papers list | → add_paper, export_to_zotero, synthesize_literature |
| `add_paper` | Add paper to local library | paper_id/DOI/title (str) | Paper metadata + PDF | → export_to_zotero, extract_lit_themes |
| `export_to_zotero` | Export papers to Zotero | paper_ids (list) | Zotero collection | → export_lit_review |
| `extract_lit_themes` | Extract themes from papers | paper_ids (list) | Theme list with frequencies | → synthesize_literature |
| `find_research_gaps` | Identify gaps in literature | paper_ids (list) | Gap analysis | → search_papers (new direction) |
| `synthesize_literature` | Synthesize papers into narrative | paper_ids (list), focus (str) | Literature review text | → export_lit_review, write_file |
| `export_lit_review` | Export formatted lit review | content (str), format (str) | Formatted document | (end of chain) |

**Real Workflow Example**:
```
search_papers("neural networks") 
→ add_paper(top 5) 
→ extract_lit_themes() 
→ find_research_gaps() 
→ synthesize_literature() 
→ export_lit_review("research_gaps.pdf")
```

---

## 💰 Financial Data (1 tool)

| Tool | Purpose | Inputs | Outputs | Sequences With |
|------|---------|--------|---------|---------------|
| `get_financial_data` | Get stock/financial data | ticker (str), start_date, end_date | Price/volume time series | → load_dataset, analyze_data, plot_data |

**Real Workflow Example**:
```
get_financial_data("AAPL", "2023-01-01", "2024-01-01") 
→ load_dataset() 
→ run_regression(price ~ volume) 
→ plot_data("timeseries")
```

---

## 🌐 Web Search (1 tool)

| Tool | Purpose | Inputs | Outputs | Sequences With |
|------|---------|--------|---------|---------------|
| `web_search` | General web search | query (str), num_results (int) | Search results with URLs, snippets | → read_file (if local), run_python_code (parse) |

**Real Workflow Example**:
```
web_search("latest AI research 2024") 
→ run_python_code(extract_arxiv_ids()) 
→ search_papers(arxiv_ids)
```

---

## 📂 File System (3 tools)

| Tool | Purpose | Inputs | Outputs | Sequences With |
|------|---------|--------|---------|---------------|
| `list_directory` | List directory contents | path (str) | File/folder list | → read_file, write_file, execute_shell_command |
| `read_file` | Read file contents | path (str) | File content string | → run_python_code, load_dataset, load_transcript |
| `write_file` | Write file contents | path (str), content (str) | Success/failure | (end of chain) |

**Real Workflow Example**:
```
list_directory("./data") 
→ read_file("survey_responses.csv") 
→ load_dataset() 
→ analyze_data()
```

---

## ⚙️ Shell Execution (1 tool)

| Tool | Purpose | Inputs | Outputs | Sequences With |
|------|---------|--------|---------|---------------|
| `execute_shell_command` | Run shell commands | command (str) | stdout/stderr | → read_file, list_directory, run_python_code |

**Real Workflow Example**:
```
execute_shell_command("git log --oneline -10") 
→ run_python_code(parse_commits()) 
→ write_file("commit_analysis.md")
```

---

## 📊 Data Analysis (13 tools)

| Tool | Purpose | Inputs | Outputs | Sequences With |
|------|---------|--------|---------|---------------|
| `load_dataset` | Load CSV/Excel/JSON data | file_path (str) | DataFrame object | → analyze_data, auto_clean_data, scan_data_quality |
| `analyze_data` | Descriptive statistics | df, columns (list) | Summary statistics | → plot_data, run_regression |
| `auto_clean_data` | Auto data cleaning | df | Cleaned DataFrame | → handle_missing_values, analyze_data |
| `handle_missing_values` | Handle missing data | df, strategy (str) | DataFrame with imputed values | → analyze_data, run_regression |
| `scan_data_quality` | Data quality report | df | Quality metrics + warnings | → auto_clean_data, handle_missing_values |
| `run_regression` | Linear/logistic regression | df, formula (str) | Regression results | → plot_data, write_file |
| `run_mediation` | Mediation analysis | df, X, M, Y | Mediation effects | → write_file, plot_data |
| `run_moderation` | Moderation analysis | df, X, W, Y | Moderation effects | → plot_data, write_file |
| `run_pca` | Principal component analysis | df, n_components (int) | PCA results + loadings | → plot_data, write_file |
| `run_factor_analysis` | Factor analysis | df, n_factors (int) | Factor loadings | → plot_data, write_file |
| `plot_data` | Data visualization | df, plot_type (str) | Plot image file | (end of chain) |
| `calculate_sample_size` | Sample size calculation | effect_size, power, alpha | Required N | → run_python_code (simulation) |
| `calculate_power` | Statistical power | N, effect_size, alpha | Power value | → calculate_sample_size (iterate) |
| `calculate_mde` | Minimum detectable effect | N, power, alpha | MDE value | → calculate_power |

**Real Workflow Example**:
```
load_dataset("experiment.csv") 
→ scan_data_quality() 
→ auto_clean_data() 
→ handle_missing_values("mean") 
→ run_regression("outcome ~ treatment + age + gender") 
→ plot_data("regression_diagnostics") 
→ write_file("results.txt")
```

---

## 💻 Code Execution (2 tools)

| Tool | Purpose | Inputs | Outputs | Sequences With |
|------|---------|--------|---------|---------------|
| `run_python_code` | Execute Python code | code (str) | Execution result | → write_file, load_dataset, plot_data |
| `run_r_code` | Execute R code | code (str) | Execution result | → write_file, plot_data |

**Real Workflow Example**:
```
run_python_code("factorial(10) / 5") 
→ run_python_code(f"result * 2 = {result * 2}") 
→ run_python_code(f"is_prime({result})")
```

---

## 🗂️ Qualitative Analysis (5 tools)

| Tool | Purpose | Inputs | Outputs | Sequences With |
|------|---------|--------|---------|---------------|
| `load_transcript` | Load interview/text data | file_path (str) | Transcript object | → code_segment, extract_themes |
| `create_code` | Create qualitative code | code_name (str), description | Code object | → code_segment |
| `code_segment` | Apply code to text segment | transcript_id, segment, codes | Coded segment | → list_codes, extract_themes |
| `list_codes` | List all codes used | transcript_id (optional) | Code list with frequencies | → generate_codebook |
| `extract_themes` | Extract themes from codes | transcript_ids (list) | Theme hierarchy | → synthesize_literature, write_file |
| `generate_codebook` | Generate codebook | codes (list) | Formatted codebook | → write_file, export_lit_review |

**Real Workflow Example**:
```
load_transcript("interviews/participant_1.txt") 
→ create_code("technology_barrier") 
→ code_segment(line_5_12, ["technology_barrier"]) 
→ extract_themes() 
→ generate_codebook() 
→ write_file("codebook.pdf")
```

---

## 🔍 Project Intelligence (3 tools)

| Tool | Purpose | Inputs | Outputs | Sequences With |
|------|---------|--------|---------|---------------|
| `detect_project` | Detect project type | directory (str) | Project metadata | → check_assumptions, list_directory |
| `check_assumptions` | Validate assumptions | project_type, assumptions (list) | Validation results | → run_python_code (fix), write_file |
| `chat` | Conversational fallback | message (str) | AI response | (any tool) |

**Real Workflow Example**:
```
detect_project("./my_project") 
→ check_assumptions(["has_tests", "uses_git"]) 
→ execute_shell_command("pytest") 
→ write_file("project_assessment.md")
```

---

## 🔗 Cross-Domain Workflow Examples

### 1. **Academic Research Pipeline**
```
search_papers("machine learning bias") 
→ add_paper(top_10) 
→ extract_lit_themes() 
→ find_research_gaps() 
→ web_search("datasets for bias research") 
→ load_dataset("bias_data.csv") 
→ auto_clean_data() 
→ run_regression("bias_score ~ model_type + dataset") 
→ plot_data("regression_results") 
→ synthesize_literature() 
→ export_lit_review("bias_research_paper.pdf")
```

### 2. **Financial Analysis + Code Execution**
```
get_financial_data("TSLA", "2023-01-01", "2024-01-01") 
→ load_dataset() 
→ run_python_code("calculate_volatility()") 
→ run_python_code("detect_trends()") 
→ plot_data("candlestick") 
→ write_file("tsla_analysis.md")
```

### 3. **Qualitative + Quantitative Mixed Methods**
```
load_transcript("interviews/*.txt") 
→ extract_themes() 
→ generate_codebook() 
→ run_python_code("convert_codes_to_numeric()") 
→ load_dataset("coded_data.csv") 
→ run_factor_analysis(n_factors=3) 
→ plot_data("factor_loadings") 
→ synthesize_literature() 
→ write_file("mixed_methods_results.pdf")
```

### 4. **Project Analysis + Data Validation**
```
detect_project("./research_project") 
→ list_directory("./data") 
→ load_dataset("experiment_results.csv") 
→ scan_data_quality() 
→ auto_clean_data() 
→ calculate_power(effect_size=0.5) 
→ run_regression("outcome ~ treatment") 
→ plot_data("power_analysis") 
→ write_file("statistical_report.txt")
```

### 5. **Shell + Analysis + Visualization**
```
execute_shell_command("find . -name '*.py' | wc -l") 
→ execute_shell_command("git log --oneline | head -20") 
→ run_python_code("parse_commits()") 
→ load_dataset("commit_data.csv") 
→ analyze_data() 
→ plot_data("commit_timeline") 
→ write_file("project_activity_report.md")
```

---

## 🧪 Comprehensive Test Scenarios (REAL, NOT SHALLOW)

### Test 1: Full Academic Research Workflow
**Query**: "Find papers about neural network interpretability, analyze the main themes, identify research gaps, then suggest experimental designs to address the gaps."

**Expected Tool Sequence**:
1. `search_papers("neural network interpretability")`
2. `add_paper(top_5_papers)`
3. `extract_lit_themes(paper_ids)`
4. `find_research_gaps(paper_ids)`
5. `calculate_sample_size(effect_size=0.5, power=0.8)`
6. `synthesize_literature(focus="research gaps")`
7. `write_file("research_proposal.md")`

---

### Test 2: Financial Data + Statistical Analysis
**Query**: "Get Apple stock data for 2023, clean it, run regression to predict price from volume, test assumptions, and visualize results."

**Expected Tool Sequence**:
1. `get_financial_data("AAPL", "2023-01-01", "2023-12-31")`
2. `load_dataset(financial_data)`
3. `scan_data_quality()`
4. `auto_clean_data()`
5. `run_regression("close ~ volume + open + high + low")`
6. `check_assumptions(["linearity", "normality", "homoscedasticity"])`
7. `plot_data("regression_diagnostics")`
8. `write_file("aapl_analysis.txt")`

---

### Test 3: Qualitative Coding + Theme Extraction
**Query**: "Load interview transcripts, create codes for 'technology barriers' and 'user adoption', apply them, extract themes, and generate a codebook."

**Expected Tool Sequence**:
1. `load_transcript("interviews/participant_*.txt")`
2. `create_code("technology_barriers", "...")`
3. `create_code("user_adoption", "...")`
4. `code_segment(transcript_1, segments, ["technology_barriers"])`
5. `code_segment(transcript_2, segments, ["user_adoption"])`
6. `extract_themes(all_transcripts)`
7. `generate_codebook()`
8. `write_file("qualitative_codebook.pdf")`

---

### Test 4: Shell + Code + Analysis
**Query**: "Count Python files in this project, analyze git commit history, calculate code churn rate, and generate a project health report."

**Expected Tool Sequence**:
1. `execute_shell_command("find . -name '*.py' | wc -l")`
2. `execute_shell_command("git log --oneline --since='6 months ago' | wc -l")`
3. `execute_shell_command("git log --oneline --all --pretty=tformat: --numstat")`
4. `run_python_code("parse_git_stats()")`
5. `load_dataset("git_stats.csv")`
6. `analyze_data(columns=['additions', 'deletions'])`
7. `plot_data("code_churn_timeline")`
8. `write_file("project_health_report.md")`

---

### Test 5: Mixed Methods Research
**Query**: "Search papers about user experience in AI tools, load our user interviews, code them with themes from literature, run factor analysis on coded data, and synthesize findings into a research paper."

**Expected Tool Sequence**:
1. `search_papers("user experience AI tools")`
2. `extract_lit_themes(paper_ids)`
3. `load_transcript("user_interviews/*.txt")`
4. `create_code(themes_from_literature)`
5. `code_segment(apply_codes_to_all_transcripts)`
6. `run_python_code("convert_codes_to_numeric_matrix()")`
7. `load_dataset("coded_matrix.csv")`
8. `run_factor_analysis(n_factors=4)`
9. `plot_data("factor_loadings")`
10. `synthesize_literature(papers + qualitative_themes)`
11. `export_lit_review("mixed_methods_paper.pdf")`

---

## 🎯 Tool Sequencing Rules

### Compatible Sequences (✅ Good Chains)
- **Research → Research**: `search_papers` → `find_related_papers` → `add_paper` → `export_to_zotero`
- **Data Load → Clean → Analyze**: `load_dataset` → `scan_data_quality` → `auto_clean_data` → `analyze_data`
- **Analysis → Visualization**: `run_regression` → `plot_data`
- **Code → Analysis**: `run_python_code` → `load_dataset` → `run_regression`
- **Qualitative → Quantitative**: `extract_themes` → `run_python_code(encode)` → `run_factor_analysis`
- **Shell → File → Analysis**: `execute_shell_command` → `read_file` → `load_dataset`

### Incompatible Sequences (❌ Bad Chains)
- **Plot → Analysis**: `plot_data` should be END of chain, not middle
- **Export → Continue**: `export_lit_review`, `export_to_zotero` are terminal operations
- **Write → Read Same File**: `write_file` → `read_file` (same file) - race condition
- **Chat → Tool**: `chat` is fallback, shouldn't chain to specific tools

---

## 📈 Testing Strategy

### Shallow Tests (❌ DON'T DO THIS)
```python
# BAD: Toy example
def test_simple_math():
    result = agent.query("What is 7 times 8?")
    assert "56" in result
```

### Comprehensive Tests (✅ DO THIS)
```python
# GOOD: Real workflow with tool sequencing
def test_academic_research_pipeline():
    """
    Test full research workflow: search → analyze → synthesize
    """
    result = agent.query(
        "Find papers about transformer models, "
        "extract main themes, identify research gaps, "
        "and suggest experimental designs."
    )
    
    # Verify tool sequence executed
    assert "search_papers" in result.tools_used
    assert "extract_lit_themes" in result.tools_used
    assert "find_research_gaps" in result.tools_used
    assert "calculate_sample_size" in result.tools_used
    
    # Verify context passed between steps
    assert result.num_steps >= 4
    assert "transformer" in result.final_answer.lower()
    assert "research gap" in result.final_answer.lower()
```

---

## 🚀 Next Steps

1. **Validate Tool Capabilities**: Read tool_executor.py to confirm each tool's actual implementation
2. **Create Comprehensive Test Suite**: Implement all 5+ test scenarios above
3. **Fix Context Passing**: Ensure all tools receive outputs from previous steps
4. **Fix Research Formatting**: Stop outputting Python code for research queries
5. **Add Final Synthesis**: Answer original question after multi-step workflow
6. **Windows Testing**: Validate on Windows before v1.5.7
7. **Ship v1.5.7**: Only after comprehensive tests pass

---

**Status**: Tool inventory complete ✅  
**Next**: Map tool sequencing matrix and create comprehensive tests
