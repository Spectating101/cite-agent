#!/usr/bin/env python3
"""
STRESS TEST SUITE - 30+ Edge Cases for Tool Selection & Sequencing
Tests cite-agent's robustness under extreme conditions

Categories:
1. Tool Selection Edge Cases (5 tests)
2. Complex Multi-Tool Sequencing (8 tests)
3. Error Handling & Recovery (5 tests)
4. Context Passing Stress Tests (5 tests)
5. Cross-Domain Workflows (5 tests)
6. Ambiguous Query Resolution (3 tests)
7. Performance & Limits (3 tests)
8. Real-World Scenarios (6+ tests)

Total: 30+ comprehensive stress tests
"""

import subprocess
import json
import time
import os
import re
from datetime import datetime
from pathlib import Path


class StressTestRunner:
    """Run comprehensive stress tests on cite-agent"""
    
    def __init__(self):
        self.results = {
            "test_suite": "Stress Test Suite v1.5.6 - 30+ Edge Cases",
            "timestamp": datetime.now().isoformat(),
            "categories": {},
            "tests": []
        }
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
    
    def run_cite_agent(self, query: str, timeout=120, cwd=None):
        """Run cite-agent with a query"""
        if cwd is None:
            cwd = str(Path.home() / "Downloads" / "data")
        
        try:
            result = subprocess.run(
                ["cite-agent", query],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=cwd
            )
            
            output = result.stdout + result.stderr
            
            # Detect workflow steps
            step_matches = re.findall(r'Step (\d+)/(\d+):', output)
            num_steps = int(step_matches[-1][1]) if step_matches else 0
            
            # Detect tools (comprehensive list)
            tools_pattern = {
                'get_financial_data': r'FinSight headers|get_financial_data',
                'run_python_code': r'python3 /tmp/|run_python_code|Executing code',
                'execute_shell_command': r'Command executed:|execute_shell_command',
                'search_papers': r'search_papers|Searching papers',
                'find_related_papers': r'find_related_papers',
                'add_paper': r'add_paper',
                'export_to_zotero': r'export_to_zotero',
                'load_dataset': r'load_dataset|Loading dataset',
                'analyze_data': r'analyze_data|Analyzing data',
                'run_regression': r'run_regression|Running regression',
                'plot_data': r'plot_data|Plotting',
                'read_file': r'read_file|Reading file',
                'write_file': r'write_file|Writing file',
                'list_directory': r'list_directory|Listing directory',
                'web_search': r'web_search',
                'load_transcript': r'load_transcript',
                'create_code': r'create_code',
                'code_segment': r'code_segment',
                'extract_themes': r'extract_themes',
                'check_assumptions': r'check_assumptions',
                'detect_project': r'detect_project'
            }
            
            tools_used = []
            for tool, pattern in tools_pattern.items():
                if re.search(pattern, output, re.IGNORECASE):
                    tools_used.append(tool)
            
            # Check for errors
            has_error = bool(re.search(r'error|exception|traceback|failed', output, re.IGNORECASE))
            has_synthesis = "✅ All" in output and "tasks completed" in output
            
            return {
                "output": output,
                "steps": num_steps,
                "tools": list(set(tools_used)),
                "has_error": has_error,
                "has_synthesis": has_synthesis,
                "success": result.returncode == 0 and not has_error,
                "output_length": len(output)
            }
            
        except subprocess.TimeoutExpired:
            return {
                "output": "TIMEOUT",
                "steps": 0,
                "tools": [],
                "has_error": True,
                "has_synthesis": False,
                "success": False,
                "timeout": True
            }
        except Exception as e:
            return {
                "output": f"ERROR: {str(e)}",
                "steps": 0,
                "tools": [],
                "has_error": True,
                "has_synthesis": False,
                "success": False,
                "error": str(e)
            }
    
    def test(self, category: str, name: str, query: str, 
             expected_tools: list = None, expected_steps: int = None,
             validation_fn=None, should_fail=False, timeout=120):
        """
        Run a single test
        
        Args:
            category: Test category
            name: Test name
            query: Query to test
            expected_tools: List of tools that should be used
            expected_steps: Minimum number of workflow steps
            validation_fn: Custom validation function
            should_fail: True if this test is expected to fail (error handling tests)
            timeout: Max execution time
        """
        self.total_tests += 1
        
        print(f"\n{'='*80}")
        print(f"🧪 [{category}] TEST #{self.total_tests}: {name}")
        print(f"{'='*80}")
        print(f"Query: {query}")
        if expected_tools:
            print(f"Expected Tools: {', '.join(expected_tools)}")
        if expected_steps:
            print(f"Expected Steps: {expected_steps}+")
        print(f"{'─'*80}\n")
        
        start_time = time.time()
        result = self.run_cite_agent(query, timeout=timeout)
        elapsed = time.time() - start_time
        
        # Validation
        tools_ok = True
        if expected_tools:
            tools_found = len([t for t in expected_tools if t in result['tools']])
            tools_ok = tools_found >= len(expected_tools) * 0.5  # At least 50%
        
        steps_ok = True
        if expected_steps:
            steps_ok = result['steps'] >= expected_steps
        
        validation_ok = True
        validation_msg = "N/A"
        if validation_fn:
            try:
                validation_ok = validation_fn(result['output'])
                validation_msg = "✅ PASS" if validation_ok else "❌ FAIL"
            except Exception as e:
                validation_ok = False
                validation_msg = f"❌ ERROR: {str(e)}"
        
        # For "should_fail" tests, success means we handled the error gracefully
        if should_fail:
            status = "✅ PASS" if result['has_error'] else "❌ FAIL (expected error)"
        else:
            status = "✅ PASS" if (result['success'] and tools_ok and steps_ok and validation_ok) else "❌ FAIL"
        
        if "✅ PASS" in status:
            self.passed_tests += 1
        else:
            self.failed_tests += 1
        
        # Show result preview
        print(f"📤 OUTPUT PREVIEW (first 300 chars):")
        print(f"{'─'*80}")
        print(result['output'][:300] + "..." if len(result['output']) > 300 else result['output'])
        print(f"{'─'*80}\n")
        
        print(f"{status} - {name}")
        print(f"⏱️  Time: {elapsed:.2f}s")
        print(f"📝 Steps: {result['steps']}" + (f"/{expected_steps}" if expected_steps else ""))
        print(f"🔧 Tools: {len(result['tools'])} used: {', '.join(result['tools'][:5])}" + ("..." if len(result['tools']) > 5 else ""))
        print(f"✓  Validation: {validation_msg}")
        if result.get('timeout'):
            print("⏱️  TIMEOUT!")
        
        # Record result
        test_result = {
            "category": category,
            "name": name,
            "status": status,
            "query": query,
            "elapsed": round(elapsed, 2),
            "expected_tools": expected_tools or [],
            "actual_tools": result['tools'],
            "expected_steps": expected_steps or 0,
            "actual_steps": result['steps'],
            "validation": validation_msg,
            "has_synthesis": result['has_synthesis'],
            "output_length": result.get('output_length', 0),
            "should_fail": should_fail
        }
        
        self.results["tests"].append(test_result)
        
        # Track by category
        if category not in self.results["categories"]:
            self.results["categories"][category] = {"total": 0, "passed": 0, "failed": 0}
        self.results["categories"][category]["total"] += 1
        if "✅ PASS" in status:
            self.results["categories"][category]["passed"] += 1
        else:
            self.results["categories"][category]["failed"] += 1
        
        return test_result
    
    def save_results(self, filename="stress_test_results.json"):
        """Save comprehensive test results"""
        self.results["summary"] = {
            "total_tests": self.total_tests,
            "passed": self.passed_tests,
            "failed": self.failed_tests,
            "pass_rate": f"{(self.passed_tests/self.total_tests*100):.1f}%" if self.total_tests > 0 else "N/A"
        }
        
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n{'='*80}")
        print(f"📄 Results saved to: {filename}")
        print(f"{'='*80}")


import re  # Import at module level

def main():
    """Run all 30+ stress tests"""
    tester = StressTestRunner()
    
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║         🔥 CITE-AGENT STRESS TEST SUITE - 30+ EDGE CASES 🔥               ║
║                                                                            ║
║  Testing tool selection, sequencing, error handling, and robustness       ║
║  This is COMPREHENSIVE - not toy examples!                                ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
    """)
    
    time.sleep(2)
    
    # =========================================================================
    # CATEGORY 1: TOOL SELECTION EDGE CASES (5 tests)
    # =========================================================================
    
    print("\n" + "="*80)
    print("📂 CATEGORY 1: TOOL SELECTION EDGE CASES")
    print("Testing if cite-agent picks the RIGHT tool for ambiguous queries")
    print("="*80)
    
    tester.test(
        category="Tool Selection",
        name="Ambiguous_Financial_vs_Research",
        query="Tell me about Tesla's performance",
        expected_tools=["get_financial_data"],  # Should pick financial, not research papers
        validation_fn=lambda o: "revenue" in o.lower() or "stock" in o.lower() or "price" in o.lower()
    )
    
    tester.test(
        category="Tool Selection",
        name="Ambiguous_Shell_vs_Python",
        query="Count to 10",
        expected_tools=["run_python_code"],  # Should use Python, not shell
        validation_fn=lambda o: any(str(i) in o for i in range(1, 11))
    )
    
    tester.test(
        category="Tool Selection",
        name="Ambiguous_File_vs_Web",
        query="Find information about machine learning",
        expected_tools=["search_papers", "web_search"],  # Could be either
        validation_fn=lambda o: "machine learning" in o.lower() or "ml" in o.lower()
    )
    
    tester.test(
        category="Tool Selection",
        name="Multi_Tool_OR_Logic",
        query="Get Apple's stock price OR search for papers about Apple products, whichever is faster",
        expected_tools=["get_financial_data", "search_papers"],  # Might use one or both
        validation_fn=lambda o: "apple" in o.lower()
    )
    
    tester.test(
        category="Tool Selection",
        name="Tool_Selection_With_Context",
        query="After you get Tesla's revenue, analyze it statistically",
        expected_tools=["get_financial_data", "run_python_code"],
        expected_steps=2,
        validation_fn=lambda o: "tesla" in o.lower() and ("mean" in o.lower() or "average" in o.lower() or "analysis" in o.lower())
    )
    
    # =========================================================================
    # CATEGORY 2: COMPLEX MULTI-TOOL SEQUENCING (8 tests)
    # =========================================================================
    
    print("\n" + "="*80)
    print("🔗 CATEGORY 2: COMPLEX MULTI-TOOL SEQUENCING")
    print("Testing long chains of 5+ tool calls")
    print("="*80)
    
    tester.test(
        category="Complex Sequencing",
        name="Five_Step_Math_Chain",
        query="Calculate 8 factorial, then divide by 4, then multiply by 3, then subtract 1000, then check if result is even",
        expected_tools=["run_python_code"],
        expected_steps=5,
        validation_fn=lambda o: "even" in o.lower() or "odd" in o.lower()
    )
    
    tester.test(
        category="Complex Sequencing",
        name="Financial_Deep_Analysis",
        query="Get Microsoft's revenue, calculate year-over-year growth, compare to industry average, determine if overvalued, and recommend buy/hold/sell",
        expected_tools=["get_financial_data", "run_python_code"],
        expected_steps=4,
        validation_fn=lambda o: ("buy" in o.lower() or "sell" in o.lower() or "hold" in o.lower()) and "microsoft" in o.lower()
    )
    
    tester.test(
        category="Complex Sequencing",
        name="Shell_File_Math_Chain",
        query="Create a file with numbers 1-100 (one per line), then read it, then calculate sum, mean, and median, then write results to summary.txt",
        expected_tools=["execute_shell_command", "read_file", "run_python_code", "write_file"],
        expected_steps=4,
        validation_fn=lambda o: "sum" in o.lower() and ("mean" in o.lower() or "average" in o.lower())
    )
    
    tester.test(
        category="Complex Sequencing",
        name="Research_Filter_Analysis_Chain",
        query="Search for papers about 'deep learning', filter to papers from 2020+, extract top 3 most cited, summarize their methods",
        expected_tools=["search_papers", "run_python_code"],
        expected_steps=3,
        validation_fn=lambda o: "deep learning" in o.lower() and ("2020" in o or "2021" in o or "2022" in o or "cited" in o.lower())
    )
    
    tester.test(
        category="Complex Sequencing",
        name="Cross_Domain_Finance_Research",
        query="Get Tesla's stock price, then search for research papers about Tesla's technology, then analyze correlation between paper sentiment and stock performance",
        expected_tools=["get_financial_data", "search_papers", "run_python_code"],
        expected_steps=3,
        validation_fn=lambda o: "tesla" in o.lower() and ("correlation" in o.lower() or "analysis" in o.lower())
    )
    
    tester.test(
        category="Complex Sequencing",
        name="Nested_Conditionals",
        query="Calculate 50 factorial. If result > 1000000, divide by 1000000 and continue, else multiply by 1000. Then check if divisible by 7.",
        expected_tools=["run_python_code"],
        expected_steps=3,
        validation_fn=lambda o: "divisible" in o.lower() or "remainder" in o.lower() or "%" in o
    )
    
    tester.test(
        category="Complex Sequencing",
        name="Loop_Simulation",
        query="Calculate factorial for numbers 5, 6, 7, 8, 9 and tell me which ones are prime",
        expected_tools=["run_python_code"],
        expected_steps=2,  # Should batch this
        validation_fn=lambda o: "prime" in o.lower() and ("120" in o or "720" in o or "5040" in o)
    )
    
    tester.test(
        category="Complex Sequencing",
        name="Six_Step_Data_Pipeline",
        query="Create test data with 3 columns (x, y, z) and 10 rows, save to data.csv, read it back, calculate correlation matrix, plot it, then interpret results",
        expected_tools=["run_python_code", "write_file", "read_file", "plot_data"],
        expected_steps=5,
        validation_fn=lambda o: "correlation" in o.lower()
    )
    
    # =========================================================================
    # CATEGORY 3: ERROR HANDLING & RECOVERY (5 tests)
    # =========================================================================
    
    print("\n" + "="*80)
    print("🛡️ CATEGORY 3: ERROR HANDLING & RECOVERY")
    print("Testing how cite-agent handles errors and edge cases")
    print("="*80)
    
    tester.test(
        category="Error Handling",
        name="Nonexistent_File",
        query="Read the file 'this_file_definitely_does_not_exist_12345.txt'",
        expected_tools=["read_file"],
        should_fail=True,  # Expected to fail gracefully
        validation_fn=lambda o: "not found" in o.lower() or "error" in o.lower() or "does not exist" in o.lower()
    )
    
    tester.test(
        category="Error Handling",
        name="Invalid_Ticker",
        query="Get financial data for ticker symbol 'INVALID_TICKER_XYZ999'",
        expected_tools=["get_financial_data"],
        should_fail=True,
        validation_fn=lambda o: "invalid" in o.lower() or "not found" in o.lower() or "error" in o.lower()
    )
    
    tester.test(
        category="Error Handling",
        name="Division_By_Zero",
        query="Calculate 100 divided by 0",
        expected_tools=["run_python_code"],
        should_fail=True,
        validation_fn=lambda o: "zero" in o.lower() or "infinity" in o.lower() or "undefined" in o.lower() or "error" in o.lower()
    )
    
    tester.test(
        category="Error Handling",
        name="Malformed_Query",
        query="asdfghjkl qwerty zxcvbnm",
        expected_tools=[],  # Should handle gracefully
        validation_fn=lambda o: len(o) > 10  # Should give some response
    )
    
    tester.test(
        category="Error Handling",
        name="Timeout_Simulation",
        query="Calculate factorial of 100000 (this should take forever)",
        expected_tools=["run_python_code"],
        timeout=10,  # Short timeout
        validation_fn=lambda o: True  # Just check it doesn't crash
    )
    
    # =========================================================================
    # CATEGORY 4: CONTEXT PASSING STRESS TESTS (5 tests)
    # =========================================================================
    
    print("\n" + "="*80)
    print("🔄 CATEGORY 4: CONTEXT PASSING STRESS TESTS")
    print("Testing if context correctly passes through long workflows")
    print("="*80)
    
    tester.test(
        category="Context Passing",
        name="Deep_Context_Chain",
        query="Calculate 5!, then add 20, then multiply by 2, then divide by 4, then subtract 50, then tell me the final number",
        expected_tools=["run_python_code"],
        expected_steps=6,
        validation_fn=lambda o: "20" in o or "final" in o.lower()  # (5! + 20) * 2 / 4 - 50 = 20
    )
    
    tester.test(
        category="Context Passing",
        name="Context_Between_Different_Tools",
        query="Get Apple's current stock price, then use that number as the factorial input, then check if result is even",
        expected_tools=["get_financial_data", "run_python_code"],
        expected_steps=3,
        validation_fn=lambda o: "even" in o.lower() or "odd" in o.lower()
    )
    
    tester.test(
        category="Context Passing",
        name="File_Context_Preservation",
        query="Write the number 42 to answer.txt, then read it back, then multiply by 2, then write result to answer2.txt, then read that",
        expected_tools=["write_file", "read_file", "run_python_code"],
        expected_steps=5,
        validation_fn=lambda o: "84" in o  # 42 * 2
    )
    
    tester.test(
        category="Context Passing",
        name="Context_With_Branching",
        query="Calculate 100 / 3. If result has decimal, round up, else keep as is. Then multiply by 3.",
        expected_tools=["run_python_code"],
        expected_steps=3,
        validation_fn=lambda o: "100" in o or "102" in o  # Should get back ~100
    )
    
    tester.test(
        category="Context Passing",
        name="Multi_Variable_Context",
        query="Calculate mean of [10,20,30], then calculate median of [10,20,30], then calculate their difference",
        expected_tools=["run_python_code"],
        expected_steps=3,
        validation_fn=lambda o: "0" in o  # mean = median = 20, difference = 0
    )
    
    # =========================================================================
    # CATEGORY 5: CROSS-DOMAIN WORKFLOWS (5 tests)
    # =========================================================================
    
    print("\n" + "="*80)
    print("🌐 CATEGORY 5: CROSS-DOMAIN WORKFLOWS")
    print("Testing workflows that span multiple domains")
    print("="*80)
    
    tester.test(
        category="Cross-Domain",
        name="Finance_Research_Synthesis",
        query="Get Tesla's revenue, then search papers about electric vehicle market, then synthesize: is Tesla's revenue justified by research findings?",
        expected_tools=["get_financial_data", "search_papers", "run_python_code"],
        expected_steps=3,
        validation_fn=lambda o: "tesla" in o.lower() and ("justified" in o.lower() or "revenue" in o.lower())
    )
    
    tester.test(
        category="Cross-Domain",
        name="Shell_Web_Finance",
        query="Count how many Python files in current directory, then search web for 'Python programming statistics', then get Python Software Foundation stock info (if exists)",
        expected_tools=["execute_shell_command", "web_search", "get_financial_data"],
        expected_steps=3,
        validation_fn=lambda o: "python" in o.lower()
    )
    
    tester.test(
        category="Cross-Domain",
        name="Math_File_Research",
        query="Calculate fibonacci(10), save result to fib.txt, then search for research papers about 'fibonacci in nature'",
        expected_tools=["run_python_code", "write_file", "search_papers"],
        expected_steps=3,
        validation_fn=lambda o: ("55" in o or "fibonacci" in o.lower()) and "nature" in o.lower()
    )
    
    tester.test(
        category="Cross-Domain",
        name="Data_Creation_Analysis_Research",
        query="Generate random dataset with 100 rows, analyze its distribution, then search for papers about 'statistical distribution analysis'",
        expected_tools=["run_python_code", "analyze_data", "search_papers"],
        expected_steps=3,
        validation_fn=lambda o: "distribution" in o.lower()
    )
    
    tester.test(
        category="Cross-Domain",
        name="Financial_Comparison_Multi_Company",
        query="Get revenue for Apple, Microsoft, and Google, then calculate which has highest growth rate, then search for analyst predictions about the winner",
        expected_tools=["get_financial_data", "run_python_code", "web_search"],
        expected_steps=4,
        validation_fn=lambda o: ("apple" in o.lower() or "microsoft" in o.lower() or "google" in o.lower()) and "growth" in o.lower()
    )
    
    # =========================================================================
    # CATEGORY 6: AMBIGUOUS QUERY RESOLUTION (3 tests)
    # =========================================================================
    
    print("\n" + "="*80)
    print("❓ CATEGORY 6: AMBIGUOUS QUERY RESOLUTION")
    print("Testing how cite-agent interprets unclear requests")
    print("="*80)
    
    tester.test(
        category="Ambiguous Resolution",
        name="Vague_Analysis_Request",
        query="Analyze something interesting",
        expected_tools=[],  # Agent should ask for clarification OR pick something
        validation_fn=lambda o: len(o) > 20  # Should respond with something
    )
    
    tester.test(
        category="Ambiguous Resolution",
        name="Multiple_Interpretations",
        query="Python",  # Could mean: language info, snake info, file operations, etc.
        expected_tools=[],
        validation_fn=lambda o: "python" in o.lower()
    )
    
    tester.test(
        category="Ambiguous Resolution",
        name="Context_Dependent_Query",
        query="Do it again",  # Requires previous context
        expected_tools=[],
        validation_fn=lambda o: True  # Should handle gracefully
    )
    
    # =========================================================================
    # CATEGORY 7: PERFORMANCE & LIMITS (3 tests)
    # =========================================================================
    
    print("\n" + "="*80)
    print("⚡ CATEGORY 7: PERFORMANCE & LIMITS")
    print("Testing performance boundaries and limits")
    print("="*80)
    
    tester.test(
        category="Performance",
        name="Large_Number_Calculation",
        query="Calculate 100 factorial and tell me how many digits it has",
        expected_tools=["run_python_code"],
        expected_steps=2,
        validation_fn=lambda o: "157" in o or "158" in o  # 100! has 158 digits
    )
    
    tester.test(
        category="Performance",
        name="Multiple_API_Calls",
        query="Get financial data for AAPL, MSFT, GOOGL, TSLA, and AMZN, then calculate average P/E ratio",
        expected_tools=["get_financial_data", "run_python_code"],
        expected_steps=2,
        validation_fn=lambda o: "average" in o.lower() or "mean" in o.lower()
    )
    
    tester.test(
        category="Performance",
        name="Long_Query_Processing",
        query="Calculate the factorial of 10, then calculate the factorial of 11, then calculate the factorial of 12, then find the sum of all three factorials, then check if the sum is divisible by 7, and if so, divide by 7, otherwise multiply by 7, then finally tell me the result",
        expected_tools=["run_python_code"],
        expected_steps=5,
        validation_fn=lambda o: any(char.isdigit() for char in o)  # Should have numbers in result
    )
    
    # =========================================================================
    # CATEGORY 8: REAL-WORLD SCENARIOS (6+ tests)
    # =========================================================================
    
    print("\n" + "="*80)
    print("🌍 CATEGORY 8: REAL-WORLD SCENARIOS")
    print("Testing realistic use cases researchers would actually use")
    print("="*80)
    
    tester.test(
        category="Real-World",
        name="Research_Paper_Analysis",
        query="Search for papers about 'transformer architecture', find the most cited paper, and summarize its key contributions",
        expected_tools=["search_papers", "run_python_code"],
        expected_steps=2,
        validation_fn=lambda o: "transformer" in o.lower() and ("attention" in o.lower() or "paper" in o.lower())
    )
    
    tester.test(
        category="Real-World",
        name="Investment_Analysis",
        query="Compare Tesla and NIO: get their revenues, calculate P/E ratios, and recommend which is better value",
        expected_tools=["get_financial_data", "run_python_code"],
        expected_steps=3,
        validation_fn=lambda o: ("tesla" in o.lower() or "nio" in o.lower()) and ("better" in o.lower() or "recommend" in o.lower())
    )
    
    tester.test(
        category="Real-World",
        name="Statistical_Significance_Test",
        query="Generate two random samples (n=100 each), one with mean=50 and one with mean=52, then run a t-test to check if they're significantly different",
        expected_tools=["run_python_code"],
        expected_steps=3,
        validation_fn=lambda o: ("significant" in o.lower() or "p-value" in o.lower() or "t-test" in o.lower())
    )
    
    tester.test(
        category="Real-World",
        name="Literature_Gap_Analysis",
        query="Search for papers about 'quantum computing applications', identify what areas have few papers (gaps), and suggest research directions",
        expected_tools=["search_papers", "run_python_code"],
        expected_steps=3,
        validation_fn=lambda o: "quantum" in o.lower() and ("gap" in o.lower() or "direction" in o.lower() or "suggest" in o.lower())
    )
    
    tester.test(
        category="Real-World",
        name="Data_Quality_Check",
        query="Create a dataset with some missing values, detect them, calculate percentage missing, and recommend imputation strategy",
        expected_tools=["run_python_code", "analyze_data"],
        expected_steps=3,
        validation_fn=lambda o: "missing" in o.lower() and ("percent" in o.lower() or "%" in o or "imputation" in o.lower())
    )
    
    tester.test(
        category="Real-World",
        name="Competitive_Intelligence",
        query="Get Apple and Samsung's revenues, calculate market share if combined revenue is 100%, then search news about their competition",
        expected_tools=["get_financial_data", "run_python_code", "web_search"],
        expected_steps=3,
        validation_fn=lambda o: ("apple" in o.lower() or "samsung" in o.lower()) and "market share" in o.lower()
    )
    
    # =========================================================================
    # FINAL SUMMARY
    # =========================================================================
    
    print("\n" + "="*80)
    print("📊 STRESS TEST EXECUTION COMPLETE")
    print("="*80)
    
    tester.save_results()
    
    summary = tester.results["summary"]
    print(f"""
╔════════════════════════════════════════════════════════════════════════════╗
║                      STRESS TEST SUITE SUMMARY                             ║
╠════════════════════════════════════════════════════════════════════════════╣
║  Total Tests:  {summary['total_tests']:<3}                                                        ║
║  ✅ Passed:    {summary['passed']:<3}                                                        ║
║  ❌ Failed:    {summary['failed']:<3}                                                        ║
║  Pass Rate:    {summary['pass_rate']:<6}                                                   ║
╚════════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Category breakdown
    print("\n" + "="*80)
    print("RESULTS BY CATEGORY")
    print("="*80)
    for category, stats in tester.results["categories"].items():
        pass_rate = (stats['passed'] / stats['total'] * 100) if stats['total'] > 0 else 0
        status = "✅" if pass_rate >= 70 else "⚠️" if pass_rate >= 50 else "❌"
        print(f"{status} {category:<35} | {stats['passed']}/{stats['total']} ({pass_rate:.1f}%)")
    
    # Individual results
    print("\n" + "="*80)
    print("DETAILED TEST RESULTS")
    print("="*80)
    for i, test in enumerate(tester.results["tests"], 1):
        status_emoji = "✅" if "✅ PASS" in test["status"] else "❌"
        print(f"{status_emoji} {i:02d}. [{test['category']}] {test['name']:<45} | {test['elapsed']:.1f}s | {test['actual_steps']} steps | {len(test['actual_tools'])} tools")
    
    print(f"\n{'='*80}")
    print("Full results saved to: stress_test_results.json")
    print("="*80)
    
    return tester.results


if __name__ == "__main__":
    main()
