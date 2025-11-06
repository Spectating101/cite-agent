# Hardcoding Audit Report - REAL ISSUES FOUND
**Date:** November 6, 2025  
**Status:** ⚠️ ISSUES IDENTIFIED & READY TO FIX  
**Author:** Verification scan

---

## Executive Summary

Found **2 REAL hardcoded values** that will break on professors' machines:

| Issue | File | Line | Problem | Impact |
|-------|------|------|---------|--------|
| 1 | `cite_agent/streaming_ui.py` | 196 | `/home/researcher/project` | Example code will fail |
| 2 | `tests/test_cli_direct.py` | 11 | `/home/phyrexian/.local/share/...` | Test will fail on any machine |

---

## Issue #1: Hardcoded Path in streaming_ui.py

**File:** `cite_agent/streaming_ui.py`  
**Line:** 196  
**Current Code:**
```python
working_dir="/home/researcher/project"
```

**Problem:**
- This is in example usage code
- Path `/home/researcher/project` doesn't exist on professors' machines
- If run, will use hardcoded directory instead of current working directory

**Fix:**
```python
working_dir=os.getcwd()
```

**Severity:** ⚠️ MEDIUM (example code, but could be copy-pasted)

---

## Issue #2: Hardcoded Python Path in test_cli_direct.py

**File:** `tests/test_cli_direct.py`  
**Line:** 11  
**Current Code:**
```python
sys.path.insert(0, "/home/phyrexian/.local/share/pipx/venvs/cite-agent/lib/python3.13/site-packages")
```

**Problem:**
- YOUR machine-specific path
- Different on every installation
- Different on Windows, Mac, Linux
- Will cause test to fail or not find imports
- This is a machine-specific venv path that won't exist elsewhere

**Fix:**
```python
# Remove this line entirely - Python already has proper import paths
# The installed package should be in sys.path already
```

**Severity:** ⚠️ HIGH (test file, will break on professors' machines)

---

## Issue #3: Developer Name (Intentional Feature)

**Files:** 
- `cite_agent/enhanced_ai_agent.py` line 1636
- `cite-agent-api/src/routes/query.py` line 298

**Current Code:**
```python
"I was built by Phyrexian."
```

**Assessment:** ✅ **INTENTIONAL - DO NOT FIX**
- This is a feature, not a bug
- When user asks "who built you?", the chatbot identifies the developer
- Should stay as-is (unless you want to make it configurable via environment variable)
- Not a portability issue since it's just a string response

---

## Verified SAFE (Already Dynamic)

These were checked and are already safe:

✅ **All paths use dynamic resolution:**
- PDF cache: `Path.home() / ".cite_agent" / "pdf_cache"`
- Working directories: `os.getcwd()`
- Config paths: `Path.home() / ".config"`

✅ **All API endpoints configurable:**
- Backend URLs: Environment variables with sensible defaults
- Ports: All configurable via env vars
- Database paths: Use `Path.home()` or env vars

✅ **OS detection correct:**
- Windows check: `os.name == "nt"` ✓
- Path handling: Uses `pathlib` ✓
- Cross-platform: Tested ✓

---

## Commits to Make

### Commit 1: Fix streaming_ui.py example path
```bash
git commit -m "fix: Replace hardcoded path with dynamic resolution in streaming_ui.py example"
```

**Changes:**
- Line 196: `/home/researcher/project` → `os.getcwd()`

### Commit 2: Fix test_cli_direct.py hardcoded venv path
```bash
git commit -m "fix: Remove machine-specific sys.path hardcoding in test_cli_direct.py"
```

**Changes:**
- Line 11: Remove entire sys.path.insert line

---

## Testing After Fix

```bash
# Test 1: Verify streaming_ui example uses dynamic path
grep -n "working_dir=" cite_agent/streaming_ui.py

# Test 2: Verify test file doesn't have hardcoded paths
grep -n "/home/" tests/test_cli_direct.py

# Test 3: Run the tests
python -m pytest tests/test_cli_direct.py -v
```

---

## Professor-Ready Checklist

After fixes:
- ✅ No `/home/phyrexian` paths
- ✅ No `/home/researcher` paths
- ✅ No machine-specific venv paths
- ✅ All tests use dynamic paths
- ✅ All examples use dynamic paths
- ✅ Cross-platform compatible

---

## Status: Ready to Fix

Both issues are identified and straightforward to fix. Ready to proceed with commits!
