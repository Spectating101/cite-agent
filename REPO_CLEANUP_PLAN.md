# Repository Cleanup Plan

## Files to KEEP (Essential)

### Core Application
- ✅ `cite_agent/` - Main application code
- ✅ `cite-agent-api/` - API backend
- ✅ `data/` - Data files
- ✅ `docs/` - Documentation

### Essential Documentation
- ✅ `README.md` - Project overview
- ✅ `ARCHITECTURE.md` - System architecture
- ✅ `FEATURES.md` - Feature list
- ✅ `INSTALL.md` - Installation guide
- ✅ `GETTING_STARTED.md` - Quick start
- ✅ `DEPLOY.md` - Deployment guide
- ✅ `CHANGELOG.md` - Version history
- ✅ **`PRODUCTION_CAPABILITY_MAP.md`** - Authoritative capability reference (NEWEST)

### Essential Test Files
- ✅ **`test_production_edge_cases.py`** - Comprehensive production testing
- ✅ **`test_core_research_functionality.py`** - Core functionality validation
- ✅ `test_beta_launch.py` - Beta testing suite
- ✅ `test_real_functionality.py` - Real functionality tests

---

## Files to ARCHIVE (Move to `archive/` or `docs/archive/`)

### Iteration Documentation (Historical Value)
- 📦 `EXCELLENCE_ITERATION_SUMMARY.md` - Iteration 1 details
- 📦 `ITERATION_2_SUMMARY.md` - Iteration 2 details
- 📦 `FINAL_EXCELLENCE_SUMMARY.md` - 3-iteration summary
- 📦 `REAL_STATUS_SUMMARY.md` - Reality check doc
- 📦 `MAKING_RESPONSES_MAGICAL.md` - Process documentation

These are superseded by `PRODUCTION_CAPABILITY_MAP.md` but have historical value.

### Session/Investigation Reports (Historical)
- 📦 `FINAL_SESSION_SUMMARY.md` - Session summary
- 📦 `INTELLIGENCE_VALIDATION_RESULTS.md` - Validation results
- 📦 `CRITICAL_GAP_ANALYSIS.md` - Gap analysis
- 📦 `LLM_TIMEOUT_ROOT_CAUSE_ANALYSIS.md` - Timeout investigation
- 📦 `FOR_HAIKU_SESSION_RESULTS.md` - Haiku session notes

### Cleanup/Process Reports (Historical)
- 📦 `ACTUAL_CODE_VERIFICATION_REPORT.md` - Verification report
- 📦 `CLEANUP_COMPLETION_REPORT.md` - Cleanup report
- 📦 `COMPLETE_CLEANUP_REPORT.md` - Complete cleanup
- 📦 `PHASE2_CLEANUP_RECOMMENDATIONS.md` - Phase 2 cleanup
- 📦 `DUAL_AGENT_SYNC_PROTOCOL.md` - Sync protocol
- 📦 `COMPLETION_SUMMARY.md` - Completion summary
- 📦 `FIXES_IMPLEMENTATION_REPORT.md` - Fixes report
- 📦 `INFRASTRUCTURE_INVESTIGATION_REPORT.md` - Infrastructure investigation

### Beta/Launch Reports (Historical)
- 📦 `BETA_READINESS_FINAL.md` - Beta readiness
- 📦 `BETA_TEST_GUIDE.md` - Beta testing guide
- 📦 `AGENT_FUNCTIONALITY_REPORT.md` - Functionality report
- 📦 `FUNCTIONALITY_QUICK_SUMMARY.md` - Quick summary

---

## Files to REMOVE (Obsolete)

### Old Test Files (Superseded)
- ❌ `test_comprehensive_excellence.py` - Superseded by production tests
- ❌ `test_magical_improvements.py` - Early iteration tests
- ❌ `test_comprehensive_mock.py` - Mock tests
- ❌ `test_agent_quick.py` - Quick tests
- ❌ `test_intelligence_features.py` - Superseded
- ❌ `test_lm_timeout_diagnostic.py` - Diagnostic test

### Test Result Files (Transient Data)
- ❌ `production_test_results.txt` - Can be regenerated
- ❌ `test_results_baseline.txt` - Historical data
- ❌ `test_results_iteration2.txt` - Historical data
- ❌ `test_core_results.txt` - Can be regenerated

### Marketing/Pitch (Move to separate folder)
- 📦 `PITCH.md` - Marketing pitch document

---

## Connector Status

**Searched for**: Zotero, Stata connectors
**Result**: ❌ NOT FOUND in repository

**Conclusion**: Connectors mentioned in conversation history but not currently implemented in this codebase. May have been discussed for future work or exist in separate repository.

**Recommendation**: Document as "Planned Integrations" rather than "Available Integrations"

---

## Proposed Directory Structure

```
cite-agent/
├── README.md                                  # Main project overview
├── ARCHITECTURE.md                            # System design
├── PRODUCTION_CAPABILITY_MAP.md               # ⭐ AUTHORITATIVE REFERENCE
├── FEATURES.md                                # Feature list
├── INSTALL.md                                 # Installation
├── DEPLOY.md                                  # Deployment
├── CHANGELOG.md                               # Version history
├── GETTING_STARTED.md                         # Quick start
├── cite_agent/                                # Application code
├── cite-agent-api/                            # API backend
├── data/                                      # Data files
├── docs/                                      # Documentation
│   ├── archive/                               # 📦 Historical docs
│   │   ├── iterations/                        # Improvement iterations
│   │   ├── investigations/                    # Root cause analyses
│   │   └── session-reports/                   # Session summaries
│   └── guides/                                # User guides
├── tests/                                     # Test suite
│   ├── test_production_edge_cases.py          # ⭐ Comprehensive production tests
│   ├── test_core_research_functionality.py    # ⭐ Core capability tests
│   ├── test_beta_launch.py                    # Beta testing
│   └── test_real_functionality.py             # Real-world tests
└── scripts/                                   # Utility scripts
```

---

## Cleanup Commands

### Step 1: Create Archive Directory
```bash
mkdir -p docs/archive/{iterations,investigations,session-reports}
```

### Step 2: Move Historical Documentation
```bash
# Iterations
mv EXCELLENCE_ITERATION_SUMMARY.md docs/archive/iterations/
mv ITERATION_2_SUMMARY.md docs/archive/iterations/
mv FINAL_EXCELLENCE_SUMMARY.md docs/archive/iterations/
mv REAL_STATUS_SUMMARY.md docs/archive/iterations/
mv MAKING_RESPONSES_MAGICAL.md docs/archive/iterations/

# Investigations
mv CRITICAL_GAP_ANALYSIS.md docs/archive/investigations/
mv LLM_TIMEOUT_ROOT_CAUSE_ANALYSIS.md docs/archive/investigations/
mv INFRASTRUCTURE_INVESTIGATION_REPORT.md docs/archive/investigations/

# Session Reports
mv FINAL_SESSION_SUMMARY.md docs/archive/session-reports/
mv FOR_HAIKU_SESSION_RESULTS.md docs/archive/session-reports/
mv INTELLIGENCE_VALIDATION_RESULTS.md docs/archive/session-reports/

# Cleanup Reports
mv *CLEANUP*.md docs/archive/
mv DUAL_AGENT_SYNC_PROTOCOL.md docs/archive/
mv COMPLETION_SUMMARY.md docs/archive/
mv FIXES_IMPLEMENTATION_REPORT.md docs/archive/

# Beta/Launch
mv BETA_*.md docs/archive/
mv AGENT_FUNCTIONALITY_REPORT.md docs/archive/
mv FUNCTIONALITY_QUICK_SUMMARY.md docs/archive/
mv ACTUAL_CODE_VERIFICATION_REPORT.md docs/archive/
```

### Step 3: Remove Obsolete Test Files
```bash
rm -f test_comprehensive_excellence.py
rm -f test_magical_improvements.py
rm -f test_comprehensive_mock.py
rm -f test_agent_quick.py
rm -f test_intelligence_features.py
rm -f test_lm_timeout_diagnostic.py
```

### Step 4: Remove Test Result Files
```bash
rm -f production_test_results.txt
rm -f test_results_*.txt
rm -f test_core_results.txt
```

### Step 5: Organize Test Files
```bash
mkdir -p tests
mv test_production_edge_cases.py tests/
mv test_core_research_functionality.py tests/
mv test_beta_launch.py tests/
mv test_real_functionality.py tests/
```

---

## Post-Cleanup Validation

### Essential Files Checklist:
- [ ] `README.md` exists
- [ ] `PRODUCTION_CAPABILITY_MAP.md` exists (primary reference)
- [ ] `cite_agent/enhanced_ai_agent.py` exists
- [ ] `tests/test_production_edge_cases.py` exists
- [ ] `tests/test_core_research_functionality.py` exists
- [ ] `docs/archive/` directory created
- [ ] Historical docs moved to archive
- [ ] Obsolete tests removed

### Repo Size Check:
```bash
# Before cleanup
du -sh .

# After cleanup
du -sh .

# Archive size
du -sh docs/archive/
```

---

## Benefits of Cleanup

1. **Clarity**: Single authoritative reference (`PRODUCTION_CAPABILITY_MAP.md`)
2. **Maintainability**: Fewer files to navigate
3. **Performance**: Smaller repo, faster clones
4. **Organization**: Clear structure (app code, tests, docs, archive)
5. **Historical Preservation**: Old docs archived, not lost

---

## Connector Integration Plan (Future)

### Zotero Integration (Not Yet Implemented)
**Potential Features**:
- Export citations to Zotero library
- Import research questions from Zotero collections
- Sync paper recommendations with Zotero

**Status**: 🔮 Future work

---

### Stata Integration (Not Yet Implemented)
**Potential Features**:
- Generate Stata .do files from analysis recommendations
- Parse Stata output for interpretation
- Suggest Stata commands for statistical tests

**Status**: 🔮 Future work

---

*Cleanup Plan Created: 2025-11-06*
*Status: Ready for execution*
