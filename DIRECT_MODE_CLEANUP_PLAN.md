# Direct Mode Cleanup Plan

## Objective
Simplify architecture to use ONLY direct Cerebras API calls with temp keys from backend.

## Current Architecture (Complex)
```
┌─────────────────────────────────────────────────┐
│ Two Modes (USE_LOCAL_KEYS flag):               │
│                                                  │
│ 1. Backend Mode (USE_LOCAL_KEYS=false)         │
│    → call_backend_query()                       │
│    → backend /query/ endpoint                   │
│    → backend calls Cerebras                     │
│    → slow, backend bottleneck                   │
│                                                  │
│ 2. Local Mode (USE_LOCAL_KEYS=true)            │
│    → self.client.chat.completions.create()     │
│    → direct to Cerebras                         │
│    → fast, no backend in request path           │
└─────────────────────────────────────────────────┘
```

## New Architecture (Simple)
```
┌─────────────────────────────────────────────────┐
│ Single Mode - Direct with Temp Keys:           │
│                                                  │
│ Auth:                                           │
│   → /auth/login → temp Cerebras key (24h)      │
│   → Store in session.json                       │
│                                                  │
│ Queries:                                        │
│   → self.client.chat.completions.create()     │
│   → direct to Cerebras                          │
│   → fast, scalable, secure                      │
└─────────────────────────────────────────────────┘
```

## Code to Remove

### 1. Delete Files (✅ DONE)
- [x] `cite_agent/backend_only_client.py`
- [x] `cite_agent/agent_backend_only.py`

### 2. Remove from enhanced_ai_agent.py

#### Lines 1763-1932: `call_backend_query()` method
```python
async def call_backend_query(self, query: str, ...):
    # 170 lines of backend HTTP calling code
    # REMOVE ENTIRELY
```

#### Lines 1615-1650: Backend mode initialization
```python
if not use_local_keys:
    self.api_keys = []
    self.client = None  # Will use HTTP client instead
    self.backend_api_url = ...
    # GET auth_token from session
    # REMOVE THIS BRANCH
```

#### Lines 1588-1614: USE_LOCAL_KEYS logic
```python
use_local_keys_env = os.getenv("USE_LOCAL_KEYS", "").lower()
if use_local_keys_env == "true":
    use_local_keys = True
# ... complex logic
# REMOVE ENTIRELY
```

#### Lines 3691, 4307, 4344, 5083: Backend query calls
Replace these 4 calls to `call_backend_query()` with direct Cerebras calls.

### 3. Simplify Initialization

**New flow:**
```python
async def initialize(self):
    # 1. Get temp key from session (set by auth.py)
    session_file = Path.home() / ".nocturnal_archive" / "session.json"
    if session_file.exists():
        session_data = json.load(open(session_file))
        temp_key = session_data.get('temp_cerebras_key')
    else:
        # Fallback: dev mode with env keys
        temp_key = os.getenv('CEREBRAS_API_KEY')

    # 2. Initialize Cerebras client
    from openai import OpenAI
    self.client = OpenAI(
        api_key=temp_key,
        base_url="https://api.cerebras.ai/v1"
    )

    # 3. Done! Simple and fast.
```

## Code to Keep

✅ All workspace inspection features
✅ Data analysis with sampling
✅ Multi-platform support
✅ Memory optimization
✅ Direct Cerebras calling (lines 3680, 4293)
✅ Function calling implementation (for multilingual)

## Changes to auth.py

Update backend `/auth/login` response to include:
```json
{
  "auth_token": "...",  // Keep for backend API calls
  "temp_cerebras_key": "...",  // NEW: 24h temp key
  "account_id": "..."
}
```

## Benefits

1. **Performance**: Queries go direct to Cerebras (sub-second)
2. **Scalability**: No backend bottleneck
3. **Security**: Users still need to auth, temp keys expire
4. **Simplicity**: Remove ~300 lines of complex backend logic
5. **Cost**: Backend only handles auth (cheap)

## Testing Plan

1. Update session.json with temp key
2. Run workspace stress tests (should still pass 10/10)
3. Test direct query: "What is 2+2?"
4. Test workspace query: "Show workspace objects"
5. Test multilingual: "什麼是機器學習？"

## Rollback Plan

If anything breaks:
```bash
git checkout backup-before-direct-mode-cleanup
```

All code is safely backed up on GitHub.
