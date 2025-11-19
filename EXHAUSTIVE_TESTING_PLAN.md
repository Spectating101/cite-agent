# EXHAUSTIVE TESTING PLAN - Every Tool, Every Edge Case
**Date:** November 19, 2025  
**Goal:** 100% tool coverage with real multi-turn conversations

---

## ALL TOOLS TO TEST

### File Operations (6 tools)
1. ✅ list_directory
2. ✅ read_file
3. ⏳ write_file
4. ⏳ create_directory
5. ⏳ delete_file
6. ⏳ move_file

### Shell Operations (1 tool)
7. ✅ execute_shell_command

### Data Analysis (10 tools)
8. ⏳ load_dataset - JUST FIXED!
9. ⏳ analyze_data
10. ⏳ filter_data
11. ⏳ aggregate_data
12. ⏳ sort_data
13. ⏳ merge_datasets
14. ⏳ export_data
15. ⏳ visualize_data
16. ⏳ compute_stats
17. ⏳ handle_missing_data

### Research Tools (3 tools)
18. ⏳ search_papers
19. ⏳ get_paper_details
20. ⏳ web_search

### Financial Tools (2 tools)
21. ⏳ get_financial_data
22. ⏳ analyze_financial_metrics

### Workflow Tools (5 tools)
23. ⏳ save_conversation
24. ⏳ load_conversation
25. ⏳ export_report
26. ⏳ summarize_conversation
27. ⏳ create_citation

**TOTAL: 27+ TOOLS** (not just 11!)

---

## REAL MULTI-TURN SCENARIOS

### Scenario 1: Data Analysis Workflow
```
ME: load sample_data.csv
AGENT: [loads data]
ME: what columns are in there?
AGENT: [lists columns]
ME: show me statistics for the first column
AGENT: [shows stats]
ME: now filter rows where that column > 50
AGENT: [filters data]
ME: export the filtered results
AGENT: [exports]
```

### Scenario 2: Research Workflow  
```
ME: search for papers on transformers
AGENT: [searches]
ME: tell me more about the first one
AGENT: [details]
ME: save this conversation
AGENT: [saves]
```

### Scenario 3: File Manipulation
```
ME: create a directory called test_dir
AGENT: [creates]
ME: write "hello world" to test_dir/test.txt
AGENT: [writes]
ME: read it back
AGENT: [reads]
ME: delete that file
AGENT: [deletes]
```

---

## Starting comprehensive testing NOW...
