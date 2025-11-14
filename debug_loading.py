#!/usr/bin/env python3
"""
Diagnostic script to check which enhanced_ai_agent.py is being loaded
"""
import sys
import os

# Add repo to path (same as PYTHONPATH)
repo_path = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, repo_path)

print(f"Repo path: {repo_path}")
print(f"sys.path[0]: {sys.path[0]}")
print()

# Import the module
import cite_agent.enhanced_ai_agent as mod

print(f"Module loaded from: {mod.__file__}")
print()

# Check line 203
with open(mod.__file__) as f:
    lines = f.readlines()

print(f"Line 202: {lines[201].rstrip()}")
print(f"Line 203: {lines[202].rstrip()}")
print(f"Line 204: {lines[203].rstrip()}")
print()

# Check if line 203 has the OVERRIDES message
if "OVERRIDES" in lines[202]:
    print("✅ Line 203 has OVERRIDES message - file is correct!")
else:
    print("❌ Line 203 missing OVERRIDES message - file is WRONG!")
    print(f"   Content: {lines[202][:100]}")
