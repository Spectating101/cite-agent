#!/usr/bin/env python3
"""
Login and run intelligence test
"""
import asyncio
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from cite_agent.auth import AuthManager

def login():
    """Login with credentials"""
    auth = AuthManager()

    print("Logging in...")
    try:
        session = auth.login(
            email="s1133958@mail.yzu.edu.tw",
            password="s1133958"
        )
        print(f"✅ Login successful!")
        print(f"   User: {session.get('email')}")
        print(f"   Token: {session.get('access_token', 'N/A')[:20]}...")
        print(f"   Expires: {session.get('expires_at', 'N/A')}")
        return True
    except Exception as e:
        print(f"❌ Login failed: {e}")
        return False

if __name__ == "__main__":
    success = login()
    sys.exit(0 if success else 1)
