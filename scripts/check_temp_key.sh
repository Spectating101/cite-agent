#!/bin/bash
# Debug script to check temp API key status

SESSION_FILE="$HOME/.nocturnal_archive/session.json"

echo "🔍 Cite-Agent Temp API Key Diagnostic"
echo "======================================="
echo ""

# Check if session file exists
if [ ! -f "$SESSION_FILE" ]; then
    echo "❌ No session file found at $SESSION_FILE"
    echo ""
    echo "Solution: Login to cite-agent to create session"
    exit 1
fi

echo "✅ Session file exists: $SESSION_FILE"
echo ""

# Check if file is readable
if [ ! -r "$SESSION_FILE" ]; then
    echo "❌ Session file not readable (permission issue)"
    exit 1
fi

# Parse JSON and check for temp key
if command -v jq &> /dev/null; then
    # Use jq if available (cleaner)
    TEMP_KEY=$(jq -r '.temp_api_key // "missing"' "$SESSION_FILE")
    TEMP_EXPIRES=$(jq -r '.temp_key_expires // "missing"' "$SESSION_FILE")
    TEMP_PROVIDER=$(jq -r '.temp_key_provider // "missing"' "$SESSION_FILE")
    EMAIL=$(jq -r '.email // "unknown"' "$SESSION_FILE")
else
    # Fallback to python
    TEMP_KEY=$(python3 -c "import json; print(json.load(open('$SESSION_FILE')).get('temp_api_key', 'missing'))" 2>/dev/null || echo "error")
    TEMP_EXPIRES=$(python3 -c "import json; print(json.load(open('$SESSION_FILE')).get('temp_key_expires', 'missing'))" 2>/dev/null || echo "error")
    TEMP_PROVIDER=$(python3 -c "import json; print(json.load(open('$SESSION_FILE')).get('temp_key_provider', 'missing'))" 2>/dev/null || echo "error")
    EMAIL=$(python3 -c "import json; print(json.load(open('$SESSION_FILE')).get('email', 'unknown'))" 2>/dev/null || echo "error")
fi

echo "📧 Email: $EMAIL"
echo ""

# Check temp key status
if [ "$TEMP_KEY" == "missing" ] || [ "$TEMP_KEY" == "null" ] || [ -z "$TEMP_KEY" ]; then
    echo "❌ NO TEMP API KEY FOUND"
    echo ""
    echo "This means you're running in BACKEND MODE (slow)"
    echo ""
    echo "Why this happens:"
    echo "  1. Backend didn't issue temp key during login"
    echo "  2. Old session before temp key feature"
    echo "  3. Backend env vars not configured"
    echo ""
    echo "Solution:"
    echo "  1. Logout: rm $SESSION_FILE"
    echo "  2. Login again: cite-agent"
    echo "  3. Check if '✅ Using temporary local key' appears"
    echo ""
    exit 1
fi

echo "✅ Temp API key found: ${TEMP_KEY:0:10}..."
echo "📦 Provider: $TEMP_PROVIDER"
echo ""

# Check expiration
if [ "$TEMP_EXPIRES" == "missing" ] || [ "$TEMP_EXPIRES" == "null" ]; then
    echo "⚠️  No expiration date (key may not work)"
else
    echo "⏰ Expires: $TEMP_EXPIRES"
    echo ""

    # Check if expired (requires Python for datetime comparison)
    EXPIRED=$(python3 << EOF
from datetime import datetime, timezone
try:
    expires_at = datetime.fromisoformat('$TEMP_EXPIRES'.replace('Z', '+00:00'))
    now = datetime.now(timezone.utc)
    print('yes' if now >= expires_at else 'no')
except:
    print('unknown')
EOF
)

    if [ "$EXPIRED" == "yes" ]; then
        echo "❌ KEY EXPIRED"
        echo ""
        echo "Solution:"
        echo "  1. Logout: rm $SESSION_FILE"
        echo "  2. Login again: cite-agent"
        echo ""
        exit 1
    elif [ "$EXPIRED" == "no" ]; then
        # Calculate time remaining
        TIME_LEFT=$(python3 << EOF
from datetime import datetime, timezone
try:
    expires_at = datetime.fromisoformat('$TEMP_EXPIRES'.replace('Z', '+00:00'))
    now = datetime.now(timezone.utc)
    hours = (expires_at - now).total_seconds() / 3600
    print(f'{hours:.1f}')
except:
    print('unknown')
EOF
)
        echo "✅ KEY VALID ($TIME_LEFT hours remaining)"
        echo ""
        echo "🚀 You should be running in FAST LOCAL MODE"
        echo ""
        echo "Test it:"
        echo "  1. Run: export NOCTURNAL_DEBUG=1"
        echo "  2. Run: cite-agent"
        echo "  3. Look for: '✅ Using temporary local key'"
        echo ""
    else
        echo "⚠️  Could not determine expiration status"
    fi
fi

echo ""
echo "📋 Full session file:"
echo "---"
if command -v jq &> /dev/null; then
    jq '.' "$SESSION_FILE"
else
    cat "$SESSION_FILE"
fi
