# DUAL-AGENT SYNCHRONIZATION PROTOCOL
**Date:** November 5, 2025  
**Status:** ACTIVE  
**Agents:** Claude (terminal/repo) + Claude Code (web/GitHub)

---

## 🔄 Synchronization Rules

### Core Principle
**GitHub = Single Source of Truth**
- Claude terminal pushes ALL changes to GitHub immediately after completion
- Claude Code pulls from GitHub before starting new work
- No divergent branches - always work from latest main

---

## 📋 Workflow Protocol

### Before Starting Any Work
```
Claude Terminal:
1. git pull origin main              (Get latest)
2. [Do work]
3. git add / commit / push           (Push immediately)
4. Notify: "Pushed to GitHub: [commit hash]"

Claude Code:
1. Pull latest from GitHub
2. Check commit history for context
3. Start work from main branch
```

### During Development

**IF Claude Terminal is working:**
- Clearly label commits with: `🤖 Terminal: [what was done]`
- Push every 5-10 minutes or after logical chunks
- Update GitHub status in conversation

**IF Claude Code is working:**
- Pull latest before making changes
- Commit with: `💻 Code: [what was done]`
- Push to GitHub immediately

**NEVER:**
- ❌ Commit locally without pushing
- ❌ Create side branches
- ❌ Work on same file without pulling first
- ❌ Assume other agent knows what you did

---

## 🔐 File Ownership & Conflict Prevention

### Claude Terminal Manages (don't modify without pulling):
```
/tests/verification_infrastructure_fixes.py    (just created)
/cite_agent/enhanced_ai_agent.py               (complex - coordinate!)
/cite_agent/cli.py                             (working files)
```

### Claude Code Manages (don't modify without pulling):
```
(Web-based files)
GitHub UI commits
Issues/PRs documentation
```

### Shared/Coordinated Files (ALWAYS sync):
```
README.md
INSTALL.md
GETTING_STARTED.md
requirements.txt
setup.py
.env.local (DON'T commit this!)
.gitignore (DO sync this!)
```

---

## 📤 Push Protocol

**When to push to GitHub:**
1. ✅ After completing a test suite
2. ✅ After fixing a bug
3. ✅ After adding a feature
4. ✅ After updating documentation
5. ✅ Every 10-15 minutes during active development

**How to push:**
```bash
git status                     # Check what changed
git add [files]               # Stage specific files
git commit -m "🤖 [message]"  # Use emoji to identify agent
git push origin main          # Always to main, never to branches
```

**Commit Message Format:**
```
🤖 Terminal: [Description] - [What changed]
💻 Code: [Description] - [What changed]
```

Examples:
```
🤖 Terminal: test: Add verification suite - 8/8 tests passing
💻 Code: docs: Update README with new features
🤖 Terminal: fix: Resolve planning JSON leak - Lines 3663-3678
```

---

## 🚨 Conflict Resolution

**IF you see different versions:**

1. **Identify the conflict:**
   - `git log --oneline | head -10` (see recent commits)
   - Check who made which changes

2. **Pull latest:**
   ```bash
   git fetch origin
   git pull origin main
   ```

3. **Resolve:**
   - Look at the diff: `git diff HEAD~1 HEAD`
   - If Claude Terminal's change: keep it, merge cleanly
   - If Claude Code's change: integrate it
   - If both changed same file: communicate first!

4. **Never force push:**
   ```bash
   # ❌ DON'T DO THIS:
   git push --force
   
   # ✅ DO THIS:
   git pull (resolve conflicts) then git push
   ```

---

## 📊 Status Check (Do This Before Starting Work)

```bash
# Terminal command to check status:
echo "=== Last 3 commits ===" && git log --oneline -3
echo "=== Files modified ===" && git status
echo "=== Compare to remote ===" && git log HEAD..origin/main --oneline
```

**Before starting work, ALWAYS check:**
- Are we on latest? `git log HEAD..origin/main` (should be empty)
- Any uncommitted changes? `git status` (should be clean)
- What did other agent do? `git log --oneline -5 | grep -E '🤖|💻'`

---

## 💬 Communication Pattern

**At start of session:**
```
"Pulling latest from GitHub and checking sync status..."
[Run git status checks]
"Latest commit: [hash] - [message]"
"Working directory: CLEAN / x files modified"
"Ready to proceed"
```

**During work:**
```
"Working on: [file/feature]"
"Pushing progress: [commit hash]"
"GitHub status: updated"
```

**At end of session:**
```
"All changes committed: [hash]"
"GitHub status: IN SYNC ✅"
"Ready for Claude Code to pull and continue"
```

---

## ✅ Sync Checklist (Do Before Handing Off)

- [ ] All work committed locally
- [ ] All commits pushed to GitHub (`git push origin main`)
- [ ] No uncommitted changes (`git status` is clean)
- [ ] Latest commit visible on GitHub
- [ ] Clearly documented what was done
- [ ] Other agent knows what to pull/continue

---

## 🎯 Right Now Status

**Current State:**
- ✅ Repo: `main` branch
- ✅ Latest commit: `80905bf` - Verification test added
- ✅ Status: CLEAN (all pushed)
- ✅ Ready for Claude Code to pull

**What Claude Code should do:**
1. `git pull origin main` (get verification test)
2. Check: `git log --oneline -3` (see what terminal did)
3. Understand: Verification tests are passing
4. Continue from here knowing: All infrastructure fixes verified

---

## 🚨 Emergency Protocol (If Out of Sync)

**If you're unsure:**
```bash
git fetch origin                    # Get latest from GitHub
git log --oneline HEAD..origin/main # See if you're behind
git status                          # Check local changes
git diff origin/main                # See what's different
```

**If truly diverged:**
```bash
# ONLY if absolutely necessary:
git reset --hard origin/main        # Reset to GitHub version (loses local work)
```

**Better: Always communicate first!**
- Check: `git log -p --max-count=1 origin/main`
- Understand what changed
- Merge cleanly instead of forcing

---

## 📝 Current Action Items

### For Claude Terminal (you):
- ✅ Push verification test (DONE - commit 80905bf)
- ⏭️ Before next work: `git pull origin main`
- ⏭️ Always push after work
- ⏭️ Document what you're doing

### For Claude Code (web):
- ⏭️ Pull latest: `git pull origin main`
- ⏭️ See: Verification test in tests/
- ⏭️ Check: `git log --oneline -5`
- ⏭️ Understand: Infrastructure fixes are verified
- ⏭️ Continue from verified state

---

**GOLDEN RULE:** If you're not sure if you're in sync, run `git pull origin main` and check the status. It takes 5 seconds and prevents hours of confusion.

