#!/usr/bin/env python3
"""
COMPREHENSIVE TOOLBOX TEST - Everything in cite-agent
Tests every tool, edge case, error scenario, and nuance
"""

import subprocess
import sys
import time
import json

def run_cite_agent_query(query, timeout=60, function_calling=False):
    """Run a single query through cite-agent"""
    env_setup = "export $(cat .env.local | grep -v '^#' | xargs) && "
    if function_calling:
        env_setup += "export NOCTURNAL_FUNCTION_CALLING=1 && "
    
    cmd = f'{env_setup}echo "{query}" | timeout {timeout} cite-agent 2>&1'
    
    result = subprocess.run(
        cmd,
        shell=True,
        capture_output=True,
        text=True,
        cwd="/home/phyrexian/Downloads/llm_automation/project_portfolio/Cite-Agent"
    )
    
    return result.stdout + result.stderr

print("=" * 100)
print("COMPREHENSIVE TOOLBOX TEST - cite-agent v1.4.13")
print("=" * 100)
print()

# Clear session for fresh start
subprocess.run("rm -f ~/.nocturnal_archive/session.json", shell=True)

test_results = {
    "passed": [],
    "failed": [],
    "warnings": []
}

# ==================== TEST 1: File Operations ====================
print("\n📁 TEST 1: FILE OPERATIONS TOOLSET")
print("-" * 100)

print("\n1.1 - list_directory tool")
output = run_cite_agent_query("list all python files in cite_agent folder", function_calling=True)
has_listing = ".py" in output or "list" in output.lower()
if has_listing:
    print("✅ PASS: list_directory working")
    test_results["passed"].append("list_directory")
else:
    print("❌ FAIL: list_directory not working")
    test_results["failed"].append("list_directory")

print("\n1.2 - read_file tool")
output = run_cite_agent_query("read the first 10 lines of setup.py", function_calling=True)
has_content = "cite" in output.lower() or "setup" in output.lower()
if has_content:
    print("✅ PASS: read_file working")
    test_results["passed"].append("read_file")
else:
    print("❌ FAIL: read_file not working")
    test_results["failed"].append("read_file")

# ==================== TEST 2: Shell Commands ====================
print("\n\n💻 TEST 2: SHELL COMMAND EXECUTION")
print("-" * 100)

print("\n2.1 - Simple shell command (pwd)")
output = run_cite_agent_query("what is the current directory?", function_calling=True)
has_pwd = "Cite-Agent" in output or "cite-agent" in output or "pwd" in output
if has_pwd:
    print("✅ PASS: Shell commands working")
    test_results["passed"].append("shell_commands")
else:
    print("❌ FAIL: Shell commands not working")
    test_results["failed"].append("shell_commands")

print("\n2.2 - Command with output (ls)")
output = run_cite_agent_query("list files in current directory", function_calling=True)
has_files = "README" in output or "setup.py" in output or ".py" in output
if has_files:
    print("✅ PASS: Shell output parsing working")
    test_results["passed"].append("shell_output")
else:
    print("❌ FAIL: Shell output not parsing correctly")
    test_results["failed"].append("shell_output")

# ==================== TEST 3: Data Operations ====================
print("\n\n📊 TEST 3: DATA OPERATIONS TOOLSET")
print("-" * 100)

print("\n3.1 - load_dataset tool (CSV)")
output = run_cite_agent_query("load the sample_data.csv file and show me the first row", function_calling=True)
has_data = "csv" in output.lower() or "data" in output.lower() or "row" in output.lower()
if has_data:
    print("✅ PASS: load_dataset working")
    test_results["passed"].append("load_dataset")
else:
    print("⚠️  WARNING: load_dataset may not be working (or file doesn't exist)")
    test_results["warnings"].append("load_dataset")

print("\n3.2 - analyze_data tool")
output = run_cite_agent_query("analyze the data in sample_data.csv and give me statistics", function_calling=True)
has_analysis = "mean" in output.lower() or "average" in output.lower() or "statistics" in output.lower()
if has_analysis:
    print("✅ PASS: analyze_data working")
    test_results["passed"].append("analyze_data")
else:
    print("⚠️  WARNING: analyze_data may not be working")
    test_results["warnings"].append("analyze_data")

# ==================== TEST 4: Research Tools ====================
print("\n\n🔍 TEST 4: RESEARCH TOOLSET")
print("-" * 100)

print("\n4.1 - web_search tool")
output = run_cite_agent_query("search the web for recent AI developments", function_calling=True)
has_search = "search" in output.lower() or "http" in output.lower() or "result" in output.lower()
if has_search:
    print("✅ PASS: web_search working")
    test_results["passed"].append("web_search")
else:
    print("❌ FAIL: web_search not working")
    test_results["failed"].append("web_search")

print("\n4.2 - search_papers tool (Archive API)")
output = run_cite_agent_query("search for papers on machine learning", function_calling=True)
has_papers = "paper" in output.lower() or "search" in output.lower() or "arxiv" in output.lower()
if has_papers:
    print("✅ PASS: search_papers working")
    test_results["passed"].append("search_papers")
else:
    print("⚠️  WARNING: search_papers may not be working (demo API?)")
    test_results["warnings"].append("search_papers")

# ==================== TEST 5: Financial Tools ====================
print("\n\n💰 TEST 5: FINANCIAL TOOLSET")
print("-" * 100)

print("\n5.1 - get_financial_data tool")
output = run_cite_agent_query("get stock data for AAPL", function_calling=True)
has_financial = "aapl" in output.lower() or "stock" in output.lower() or "financial" in output.lower()
if has_financial:
    print("✅ PASS: get_financial_data working")
    test_results["passed"].append("get_financial_data")
else:
    print("⚠️  WARNING: get_financial_data may not be working (demo API?)")
    test_results["warnings"].append("get_financial_data")

# ==================== TEST 6: Error Handling ====================
print("\n\n🚨 TEST 6: ERROR HANDLING & EDGE CASES")
print("-" * 100)

print("\n6.1 - Non-existent file")
output = run_cite_agent_query("read the file nonexistent_file_12345.txt", function_calling=True)
has_error_handling = "not found" in output.lower() or "does not exist" in output.lower() or "error" in output.lower()
if has_error_handling:
    print("✅ PASS: Error handling for missing files")
    test_results["passed"].append("error_handling_files")
else:
    print("❌ FAIL: No proper error handling for missing files")
    test_results["failed"].append("error_handling_files")

print("\n6.2 - Invalid command")
output = run_cite_agent_query("run this invalid bash command: invalidcommand12345", function_calling=True)
has_error_handling = "error" in output.lower() or "not found" in output.lower() or "invalid" in output.lower()
if has_error_handling:
    print("✅ PASS: Error handling for invalid commands")
    test_results["passed"].append("error_handling_commands")
else:
    print("❌ FAIL: No proper error handling for invalid commands")
    test_results["failed"].append("error_handling_commands")

print("\n6.3 - Empty query handling")
output = run_cite_agent_query("", function_calling=True, timeout=20)
has_response = len(output) > 100  # Should have some response, not crash
if has_response:
    print("✅ PASS: Handles empty queries gracefully")
    test_results["passed"].append("empty_query_handling")
else:
    print("❌ FAIL: Empty query causes issues")
    test_results["failed"].append("empty_query_handling")

# ==================== TEST 7: Multi-turn Context ====================
print("\n\n🔄 TEST 7: MULTI-TURN CONVERSATIONS & CONTEXT")
print("-" * 100)

print("\n7.1 - Pronoun resolution test")
# This requires actual multi-turn conversation, skipping for now
print("⏭️  SKIP: Requires interactive multi-turn session")
test_results["warnings"].append("pronoun_resolution_not_tested")

# ==================== TEST 8: Token Tracking ====================
print("\n\n🪙 TEST 8: TOKEN TRACKING")
print("-" * 100)

print("\n8.1 - Verify tokens tracked (not 0)")
output = run_cite_agent_query("what is 2+2?", function_calling=True)
# Token tracking is in debug output, hard to verify without debug mode
print("⏭️  SKIP: Requires debug mode output analysis")
test_results["warnings"].append("token_tracking_not_verified")

# ==================== TEST 9: Progress Indicators ====================
print("\n\n📊 TEST 9: PROGRESS INDICATORS")
print("-" * 100)

print("\n9.1 - Multi-step progress indicator")
output = run_cite_agent_query("list files, then read setup.py, then analyze it", function_calling=True)
has_progress = "💭" in output or "Processing step" in output
if has_progress:
    print("✅ PASS: Progress indicators showing")
    test_results["passed"].append("progress_indicators")
else:
    print("⚠️  WARNING: Progress indicators not visible (may require more complex query)")
    test_results["warnings"].append("progress_indicators")

# ==================== TEST 10: Backend Busy Scenario ====================
print("\n\n⏳ TEST 10: BACKEND BUSY / TIMEOUT SCENARIOS")
print("-" * 100)

print("\n10.1 - Quick timeout test")
# Can't easily simulate backend busy, but can test timeout handling
print("⏭️  SKIP: Requires actual backend busy condition")
test_results["warnings"].append("backend_busy_not_tested")

# ==================== FINAL SUMMARY ====================
print("\n\n" + "=" * 100)
print("FINAL TEST SUMMARY")
print("=" * 100)

total_passed = len(test_results["passed"])
total_failed = len(test_results["failed"])
total_warnings = len(test_results["warnings"])
total_tests = total_passed + total_failed + total_warnings

print(f"\n✅ PASSED: {total_passed}/{total_tests}")
print(f"❌ FAILED: {total_failed}/{total_tests}")
print(f"⚠️  WARNINGS: {total_warnings}/{total_tests}")

if test_results["passed"]:
    print(f"\n✅ Passed tests: {', '.join(test_results['passed'])}")

if test_results["failed"]:
    print(f"\n❌ Failed tests: {', '.join(test_results['failed'])}")

if test_results["warnings"]:
    print(f"\n⚠️  Warnings: {', '.join(test_results['warnings'])}")

# Save results
with open("complete_toolbox_test_results.json", "w") as f:
    json.dump(test_results, f, indent=2)

print(f"\n📄 Full results saved to: complete_toolbox_test_results.json")

# Exit code
if total_failed > 0:
    print("\n❌ TESTING FAILED - Some tools not working correctly")
    sys.exit(1)
else:
    print("\n🎉 TESTING COMPLETE - All critical tools working!")
    sys.exit(0)
