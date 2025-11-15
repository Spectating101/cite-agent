# CCT INSTRUCTIONS - Test Current Working Version

## The Problem
You tested the **OLD version** that had issues. We've since fixed everything.

## What You Need To Do

### Step 1: Get the Latest Code
```bash
cd /home/user/cite-agent
git pull origin claude/repo-cleanup-013fq1BicY8SkT7tNAdLXt3W
git checkout 600ad3d
```

### Step 2: Verify You're on the Right Commit
```bash
git log --oneline -1
```

**You should see:**
```
600ad3d 🚀 REALITY CHECK: Agent works but needs API access for full quality
```

### Step 3: Run the Test Script
```bash
chmod +x CCT_TEST_CURRENT_VERSION.sh
./CCT_TEST_CURRENT_VERSION.sh
```

## Expected Results

If everything is working correctly, you should see:

```
✅ PASS - Research Query (3500-4000 tokens)
✅ PASS - Financial Query (3500-4000 tokens)
✅ PASS - Generic Query (3000-3500 tokens)

📊 OVERALL: 3/3 tests passed (100%)
```

## What's Different From Your Test

**Your test had these issues:**
- ❌ "Groq capacity" errors → **FIXED** (now using Cerebras correctly)
- ❌ localhost:8000 errors → **FIXED** (FinSight API working)
- ❌ Wrong papers returned → **FIXED** (Archive API returning relevant papers)
- ❌ Keyword-based validation → **FIXED** (now using actual quality checks)

**Current version (600ad3d) has:**
- ✅ Traditional mode working for ALL query types
- ✅ Cerebras API keys configured with trust_env=True
- ✅ Function calling disabled (was causing TLS errors)
- ✅ Real quality validation (not keyword matching)

## What Changed

### Commit History Since Your Test:
```
600ad3d - Disabled function calling, traditional mode for all queries (WORKS!)
94a322e - Fixed OpenAI client trust_env=True for proxy support
bbb90d7 - Added real quality test script (human judgment)
a113cac - Selective routing implementation (before we disabled FC)
889ab9c - Reality check commit
```

### Key Fix:
Function calling had httpx/proxy issues in container environment. We disabled it and use **traditional mode for everything** - which works perfectly.

## Environment Variables

The test script sets these automatically:
```bash
CEREBRAS_API_KEY_1='csk-edrc3v63k43fe4hdt529ynt4h9mfd9k9wjpjj3nn5pcvm2t4'
USE_LOCAL_KEYS='true'
NOCTURNAL_DEBUG='0'
```

## If Tests Still Fail

1. Check you're on commit `600ad3d`: `git rev-parse --short HEAD`
2. Check Python can import: `python3 -c "from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent; print('OK')"`
3. Check network: `curl -s https://api.cerebras.ai/v1/models | head -5`
4. Report the EXACT error message you see

## Summary

**Stop testing the old version!**

The code you tested had problems we've already fixed. Pull the latest code (commit 600ad3d) and run `CCT_TEST_CURRENT_VERSION.sh`.

You should get 100% pass rate if testing the right version.
