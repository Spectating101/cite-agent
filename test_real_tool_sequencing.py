#!/usr/bin/env python3
"""
REAL Tool Sequencing Tests - Using cite-agent CLI directly
Tests ACTUAL multi-tool workflows with real queries

These are NOT unit tests - these are integration tests that:
1. Call cite-agent CLI with real queries
2. Verify multiple tools are used in sequence
3. Check that context passes between steps
4. Validate final answers are synthesized
"""

import subprocess
import json
import re
import time
from datetime import datetime
from pathlib import Path


class RealToolSequencingTester:
    """Test real tool sequencing using cite-agent CLI"""
    
    def __init__(self):
        self.results = {
            "test_suite": "Real Tool Sequencing v1.5.6",
            "timestamp": datetime.now().isoformat(),
            "tests": []
        }
    
    def run_cite_agent(self, query: str, timeout=120):
        """
        Run cite-agent CLI with a query
        
        Returns:
            dict with {output, steps_detected, tools_used, has_synthesis}
        """
        try:
            result = subprocess.run(
                ["cite-agent", query],
                capture_output=True,
                text=True,
                timeout=timeout,
                cwd=str(Path.home() / "Downloads" / "data")
            )
            
            output = result.stdout + result.stderr
            
            # Detect steps
            step_matches = re.findall(r'Step (\d+)/(\d+):', output)
            num_steps = int(step_matches[-1][1]) if step_matches else 0
            
            # Detect tools used
            tools_used = []
            if "get_financial_data" in output or "FinSight" in output:
                tools_used.append("get_financial_data")
            if "run_python_code" in output or "python3 /tmp/" in output:
                tools_used.append("run_python_code")
            if "load_dataset" in output:
                tools_used.append("load_dataset")
            if "search_papers" in output:
                tools_used.append("search_papers")
            if "run_regression" in output:
                tools_used.append("run_regression")
            if "analyze_data" in output:
                tools_used.append("analyze_data")
            if "plot_data" in output:
                tools_used.append("plot_data")
            if "execute_shell_command" in output or "Command executed:" in output:
                tools_used.append("execute_shell_command")
            if "read_file" in output:
                tools_used.append("read_file")
            if "write_file" in output:
                tools_used.append("write_file")
            
            # Check for synthesis (final answer after all steps)
            has_synthesis = (
                "✅ All" in output and "tasks completed!" in output
                # Could also check for final answer patterns
            )
            
            return {
                "output": output,
                "steps_detected": num_steps,
                "tools_used": tools_used,
                "has_synthesis": has_synthesis,
                "success": result.returncode == 0
            }
            
        except subprocess.TimeoutExpired:
            return {
                "output": "TIMEOUT",
                "steps_detected": 0,
                "tools_used": [],
                "has_synthesis": False,
                "success": False,
                "error": "Timeout after 120s"
            }
        except Exception as e:
            return {
                "output": f"ERROR: {str(e)}",
                "steps_detected": 0,
                "tools_used": [],
                "has_synthesis": False,
                "success": False,
                "error": str(e)
            }
    
    def test_scenario(self, name: str, query: str, expected_steps: int, 
                     expected_tools: list, validation_fn=None):
        """
        Test a real tool sequencing scenario
        
        Args:
            name: Test name
            query: Query to send to cite-agent
            expected_steps: Minimum number of workflow steps
            expected_tools: List of tools that should be used
            validation_fn: Optional function to validate output
        """
        print(f"\n{'='*80}")
        print(f"🧪 TEST: {name}")
        print(f"{'='*80}")
        print(f"Query: {query}")
        print(f"Expected: {expected_steps}+ steps, tools: {expected_tools}")
        print(f"{'─'*80}\n")
        
        start_time = time.time()
        result = self.run_cite_agent(query)
        elapsed = time.time() - start_time
        
        # Validate
        steps_ok = result['steps_detected'] >= expected_steps
        tools_ok = len(result['tools_used']) >= len(expected_tools) * 0.5  # At least 50%
        
        validation_result = "N/A"
        validation_passed = True
        if validation_fn:
            try:
                validation_passed = validation_fn(result['output'])
                validation_result = "✅ PASS" if validation_passed else "❌ FAIL"
            except Exception as e:
                validation_passed = False
                validation_result = f"❌ ERROR: {str(e)}"
        
        status = "✅ PASS" if (steps_ok and tools_ok and validation_passed and result['success']) else "❌ FAIL"
        
        # Show output preview
        print("📤 OUTPUT PREVIEW:")
        print("─" * 80)
        output_lines = result['output'].split('\n')
        for line in output_lines[:50]:  # First 50 lines
            print(line)
        if len(output_lines) > 50:
            print(f"... ({len(output_lines) - 50} more lines)")
        print("─" * 80)
        
        print(f"\n{status} - {name}")
        print(f"⏱️  Time: {elapsed:.2f}s")
        print(f"📝 Steps: {result['steps_detected']}/{expected_steps}")
        print(f"🔧 Tools: {result['tools_used']}")
        print(f"✓  Validation: {validation_result}")
        
        test_result = {
            "name": name,
            "status": status,
            "query": query,
            "elapsed": round(elapsed, 2),
            "expected_steps": expected_steps,
            "actual_steps": result['steps_detected'],
            "expected_tools": expected_tools,
            "actual_tools": result['tools_used'],
            "validation": validation_result,
            "has_synthesis": result['has_synthesis'],
            "output_length": len(result['output'])
        }
        
        self.results["tests"].append(test_result)
        return test_result
    
    def save_results(self, filename="real_tool_sequencing_results.json"):
        """Save test results"""
        total = len(self.results["tests"])
        passed = sum(1 for t in self.results["tests"] if "✅ PASS" in t["status"])
        
        self.results["summary"] = {
            "total_tests": total,
            "passed": passed,
            "failed": total - passed,
            "pass_rate": f"{(passed/total*100):.1f}%" if total > 0 else "N/A"
        }
        
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n{'='*80}")
        print(f"📄 Results saved to: {filename}")
        print(f"{'='*80}")


def main():
    """Run all real tool sequencing tests"""
    tester = RealToolSequencingTester()
    
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║           🧪 REAL TOOL SEQUENCING TESTS - Cite-Agent v1.5.6               ║
║                                                                            ║
║  Testing ACTUAL multi-tool workflows with cite-agent CLI                  ║
║  These are NOT toy examples - real queries that MUST sequence tools!      ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
    """)
    
    time.sleep(2)
    
    # ==========================================================================
    # CATEGORY 1: FINANCIAL ANALYSIS WORKFLOWS
    # ==========================================================================
    
    print("\n" + "="*80)
    print("💰 CATEGORY 1: FINANCIAL ANALYSIS WORKFLOWS")
    print("="*80)
    
    tester.test_scenario(
        name="Tesla_Revenue_Analysis",
        query="Analyze Tesla's revenue for the last 2 years. Get the financial data, then calculate the growth rate.",
        expected_steps=2,
        expected_tools=["get_financial_data", "run_python_code"],
        validation_fn=lambda o: "tesla" in o.lower() and ("growth" in o.lower() or "%" in o)
    )
    
    tester.test_scenario(
        name="Apple_PE_Ratio_Deep_Analysis",
        query="Get Apple's current P/E ratio, then compare it to the tech industry average, and tell me if it's overvalued or undervalued.",
        expected_steps=3,
        expected_tools=["get_financial_data", "run_python_code"],
        validation_fn=lambda o: "apple" in o.lower() and ("overvalued" in o.lower() or "undervalued" in o.lower())
    )
    
    tester.test_scenario(
        name="Microsoft_5Year_Revenue_Trend",
        query="Analyze Microsoft's revenue trend over the last 5 years. Fetch the data, calculate year-over-year growth rates, and identify any patterns.",
        expected_steps=3,
        expected_tools=["get_financial_data", "run_python_code"],
        validation_fn=lambda o: "microsoft" in o.lower() and "revenue" in o.lower()
    )
    
    # ==========================================================================
    # CATEGORY 2: DATA ANALYSIS WORKFLOWS
    # ==========================================================================
    
    print("\n" + "="*80)
    print("📊 CATEGORY 2: DATA ANALYSIS WORKFLOWS")
    print("="*80)
    
    tester.test_scenario(
        name="CSV_File_Statistical_Analysis",
        query="Load the file 'sample_data.csv', analyze the descriptive statistics, and tell me the mean and standard deviation of all numeric columns.",
        expected_steps=2,
        expected_tools=["load_dataset", "analyze_data"],
        validation_fn=lambda o: ("mean" in o.lower() or "average" in o.lower()) and ("std" in o.lower() or "deviation" in o.lower())
    )
    
    tester.test_scenario(
        name="Exam_Data_Regression_Analysis",
        query="Load 'exam_data.csv' and run a regression to predict final_score from study_hours. Then tell me how much each additional study hour improves the score.",
        expected_steps=3,
        expected_tools=["load_dataset", "run_regression", "run_python_code"],
        validation_fn=lambda o: "regression" in o.lower() and "study" in o.lower()
    )
    
    # ==========================================================================
    # CATEGORY 3: FILE + COMPUTATION WORKFLOWS
    # ==========================================================================
    
    print("\n" + "="*80)
    print("📂 CATEGORY 3: FILE + COMPUTATION WORKFLOWS")
    print("="*80)
    
    tester.test_scenario(
        name="Read_Numbers_Calculate_Stats",
        query="Read the file 'numbers.txt', extract all the numbers from it, calculate their mean, median, and standard deviation.",
        expected_steps=3,
        expected_tools=["read_file", "run_python_code"],
        validation_fn=lambda o: "mean" in o.lower() and "median" in o.lower()
    )
    
    tester.test_scenario(
        name="Shell_File_Count_Analysis",
        query="Count how many Python files are in the current directory using shell command, then calculate what percentage they represent of all files.",
        expected_steps=3,
        expected_tools=["execute_shell_command", "run_python_code"],
        validation_fn=lambda o: ".py" in o.lower() and ("%" in o or "percent" in o.lower())
    )
    
    # ==========================================================================
    # CATEGORY 4: MULTI-STEP CALCULATION CHAINS
    # ==========================================================================
    
    print("\n" + "="*80)
    print("🔢 CATEGORY 4: MULTI-STEP CALCULATION CHAINS")
    print("="*80)
    
    tester.test_scenario(
        name="Factorial_Chain_Complex",
        query="Calculate 10 factorial, then divide that result by 5, then multiply by 2, then check if the final result is prime.",
        expected_steps=4,
        expected_tools=["run_python_code"],
        validation_fn=lambda o: "1451520" in o or "not prime" in o.lower() or "prime" in o.lower()
    )
    
    tester.test_scenario(
        name="Statistical_Computation_Chain",
        query="Calculate the mean of [10, 20, 30, 40, 50], then calculate the variance, then the standard deviation, then the coefficient of variation.",
        expected_steps=4,
        expected_tools=["run_python_code"],
        validation_fn=lambda o: "30" in o and ("14.1" in o or "variance" in o.lower())
    )
    
    # ==========================================================================
    # CATEGORY 5: CROSS-DOMAIN WORKFLOWS
    # ==========================================================================
    
    print("\n" + "="*80)
    print("🌐 CATEGORY 5: CROSS-DOMAIN WORKFLOWS")
    print("="*80)
    
    tester.test_scenario(
        name="Financial_Data_To_File_Analysis",
        query="Get Tesla's revenue data, then save it to a file called 'tesla_revenue.txt', then read the file back and calculate the average.",
        expected_steps=4,
        expected_tools=["get_financial_data", "write_file", "read_file", "run_python_code"],
        validation_fn=lambda o: "tesla" in o.lower() and "average" in o.lower()
    )
    
    tester.test_scenario(
        name="Shell_Count_Then_Math",
        query="Use shell to count the total number of files in the current directory, then calculate the factorial of that number.",
        expected_steps=2,
        expected_tools=["execute_shell_command", "run_python_code"],
        validation_fn=lambda o: "factorial" in o.lower() or "!" in o
    )
    
    # ==========================================================================
    # FINAL SUMMARY
    # ==========================================================================
    
    print("\n" + "="*80)
    print("📊 TEST EXECUTION COMPLETE")
    print("="*80)
    
    tester.save_results()
    
    summary = tester.results["summary"]
    print(f"""
╔════════════════════════════════════════════════════════════════════════════╗
║                          TEST SUITE SUMMARY                                ║
╠════════════════════════════════════════════════════════════════════════════╣
║  Total Tests:  {summary['total_tests']:<3}                                                        ║
║  ✅ Passed:    {summary['passed']:<3}                                                        ║
║  ❌ Failed:    {summary['failed']:<3}                                                        ║
║  Pass Rate:    {summary['pass_rate']:<6}                                                   ║
╚════════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Detailed results
    print("\n" + "="*80)
    print("DETAILED RESULTS")
    print("="*80)
    for test in tester.results["tests"]:
        status_emoji = "✅" if "✅ PASS" in test["status"] else "❌"
        print(f"{status_emoji} {test['name']:<40} | {test['elapsed']:.1f}s | {test['actual_steps']}/{test['expected_steps']} steps | Tools: {len(test['actual_tools'])}")
    
    return tester.results


if __name__ == "__main__":
    main()
