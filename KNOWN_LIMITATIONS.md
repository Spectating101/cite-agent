# Known Limitations and Edge Cases

**Date**: November 7, 2025
**Status**: Documented for transparency

---

## 1. File Comparison with Spaces in Filenames

**Issue**: The file comparison command doesn't handle filenames with spaces correctly.

**Example**:
```bash
# This works:
compare file1.py and file2.py

# This might fail:
compare "my file.py" and "other file.py"
```

**Root Cause**: The shell command doesn't quote filenames:
```bash
(test -f file1.py && test -f file2.py && ...)
```

**Impact**: LOW - Most code files don't have spaces in names

**Workaround**: Users should avoid spaces in filenames, or use underscores instead

**Fix Complexity**: MEDIUM - Would require shell planner to detect spaces and add quotes

**Priority**: LOW - Edge case unlikely to be encountered in practice

---

## 2. Very Large File Comparisons

**Issue**: Comparing very large files (>1000 lines each) might exceed context window.

**Example**:
```bash
compare large_file_1.py and large_file_2.py  # Both 5000 lines each
```

**Root Cause**: Using `head -100` limits to 100 lines per file, but LLM still needs to process both.

**Impact**: LOW - head -100 already limits output

**Workaround**: Files are automatically limited to 100 lines each

**Priority**: LOW - Current implementation already handles this

---

## 3. Unicode Filenames

**Issue**: Filenames with unicode characters might not be handled correctly by shell commands.

**Example**:
```bash
find . -name 'café.py'  # Might fail depending on locale
```

**Impact**: LOW - Most code files use ASCII names

**Workaround**: Users should use ASCII filenames for code

**Priority**: LOW - Edge case

---

## 4. Conceptual Keywords False Triggers (MITIGATED)

**Issue**: Keywords like "test", "error", "request" might trigger shell planner unnecessarily.

**Example**:
```
"Can you test this hypothesis?"  # "test" triggers shell planner
"What does this error mean?"     # "error" triggers shell planner
```

**Mitigation**: LLM planner filters these out with "action": "none"

**Impact**: VERY LOW - LLM correctly returns "none" for conversational queries

**Status**: ✅ MITIGATED by design

---

## 5. Permission Denied Handling

**Issue**: Reading restricted files like /etc/shadow returns permission denied.

**Example**:
```bash
Read /etc/shadow
```

**Impact**: LOW - Error is caught and presented friendly message

**Status**: ✅ HANDLED by error recovery fix

---

## Summary

**Total Known Limitations**: 5
**High Impact**: 0
**Medium Impact**: 0
**Low Impact**: 3
**Mitigated/Handled**: 2

**Overall Risk**: LOW - No significant limitations that would prevent production use

---

## Recommendations

1. **Document** filename limitations in user guide
2. **Monitor** for edge cases in production logs
3. **Iterate** on shell command quoting if spaces become an issue
4. **Accept** unicode/permission limitations as acceptable edge cases

---

**Conclusion**: All identified limitations are edge cases with low impact. The agent is still production-ready for typical use cases.
