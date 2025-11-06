#!/usr/bin/env python3
"""
Quick Validation & Test Execution Guide
Run this to verify your Cite-Agent codebase
"""

import subprocess
import sys
from pathlib import Path

def run_command(cmd, description):
    """Run a command and report results"""
    print(f"\n{'='*70}")
    print(f"🔍 {description}")
    print(f"{'='*70}")
    print(f"Command: {cmd}\n")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=False, text=True)
        return result.returncode == 0
    except Exception as e:
        print(f"Error: {e}")
        return False

def main():
    print("\n" + "="*70)
    print("✅ CITE-AGENT VALIDATION & TEST EXECUTION")
    print("="*70)
    print(f"Working directory: {Path.cwd()}")
    print("="*70)
    
    # List of validation steps
    steps = [
        ("python3 validate_integration.py", "1️⃣  Structural Validation (no dependencies needed)"),
        ("python3 -m pytest tests/test_end_to_end_integration.py -v", "2️⃣  End-to-End Integration Tests"),
        ("python3 -m pytest tests/enhanced/ -v --tb=short", "3️⃣  Enhanced Test Suite"),
    ]
    
    results = []
    
    for cmd, description in steps:
        success = run_command(cmd, description)
        results.append((description, success))
    
    # Summary
    print(f"\n\n{'='*70}")
    print("📊 VALIDATION SUMMARY")
    print(f"{'='*70}\n")
    
    for description, success in results:
        symbol = "✅" if success else "⚠️"
        print(f"{symbol} {description}")
    
    print(f"\n{'='*70}")
    print("✅ VALIDATION COMPLETE")
    print(f"{'='*70}\n")
    print("Next steps:")
    print("  1. Review VALIDATION_REPORT.md for detailed results")
    print("  2. Install dependencies: pip install -r requirements.txt")
    print("  3. Configure .env file with API keys")
    print("  4. Run: pytest tests/ -v for full test suite")
    print("  5. Deploy: ./deploy.sh or docker-compose up\n")

if __name__ == "__main__":
    main()
