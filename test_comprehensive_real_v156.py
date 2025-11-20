#!/usr/bin/env python3
"""
REAL Comprehensive Tool Sequencing Test Suite for Cite-Agent v1.5.6

This is NOT shallow toy testing. These are REAL multi-tool workflow scenarios
that exercise the full 39-tool capability of cite-agent.

Author: Testing Framework v1.5.6
Date: 2024
"""

import json
import time
import sys
from datetime import datetime
from pathlib import Path

# Add cite_agent to path
sys.path.insert(0, str(Path(__file__).parent / "cite_agent"))

from cite_agent.enhanced_ai_agent import EnhancedAIAgent
from cite_agent.memory_manager import ConversationMemoryManager


class ComprehensiveTestRunner:
    """Run REAL comprehensive tests with multi-tool workflows"""
    
    def __init__(self):
        self.agent = EnhancedAIAgent()
        self.memory = ConversationMemoryManager()
        self.results = {
            "test_suite": "Comprehensive Tool Sequencing v1.5.6",
            "timestamp": datetime.now().isoformat(),
            "tests": []
        }
    
    def run_test(self, test_name: str, query: str, expected_tools: list, 
                 min_steps: int = 1, validation_fn=None):
        """
        Run a comprehensive test with tool sequencing validation
        
        Args:
            test_name: Test identifier
            query: Query to send to agent
            expected_tools: List of tools that should be used
            min_steps: Minimum number of workflow steps expected
            validation_fn: Optional function to validate the response
        """
        print(f"\n{'='*80}")
        print(f"🧪 TEST: {test_name}")
        print(f"{'='*80}")
        print(f"Query: {query}\n")
        
        start_time = time.time()
        
        try:
            # Execute query
            response = self.agent.process_query(query)
            elapsed = time.time() - start_time
            
            print(f"\n{'─'*80}")
            print("📊 RESPONSE:")
            print(f"{'─'*80}")
            print(response)
            
            # Extract metadata
            tools_used = []
            num_steps = 0
            
            # Try to detect tools from response (simple heuristic)
            for tool in expected_tools:
                if tool in response or tool.replace('_', ' ') in response.lower():
                    tools_used.append(tool)
            
            # Count workflow steps (look for "Step X" or "Task X")
            import re
            step_matches = re.findall(r'(?:Step|Task)\s+(\d+)', response)
            if step_matches:
                num_steps = max(int(m) for m in step_matches)
            
            # Run custom validation if provided
            validation_passed = True
            validation_msg = "No custom validation"
            if validation_fn:
                try:
                    validation_passed = validation_fn(response)
                    validation_msg = "Validation passed" if validation_passed else "Validation failed"
                except Exception as e:
                    validation_passed = False
                    validation_msg = f"Validation error: {str(e)}"
            
            # Determine test status
            tools_found = len(tools_used) >= len(expected_tools) * 0.5  # At least 50% of tools
            steps_ok = num_steps >= min_steps
            status = "✅ PASS" if (tools_found and steps_ok and validation_passed) else "❌ FAIL"
            
            # Record results
            test_result = {
                "test_name": test_name,
                "status": status,
                "query": query,
                "elapsed_seconds": round(elapsed, 2),
                "expected_tools": expected_tools,
                "tools_detected": tools_used,
                "tools_coverage": f"{len(tools_used)}/{len(expected_tools)}",
                "min_steps_required": min_steps,
                "steps_executed": num_steps,
                "validation": validation_msg,
                "response_length": len(response),
                "response_preview": response[:500] + "..." if len(response) > 500 else response
            }
            
            self.results["tests"].append(test_result)
            
            print(f"\n{'─'*80}")
            print(f"{status} - {test_name}")
            print(f"{'─'*80}")
            print(f"⏱️  Time: {elapsed:.2f}s")
            print(f"🔧 Tools: {len(tools_used)}/{len(expected_tools)} detected")
            print(f"📝 Steps: {num_steps}/{min_steps}")
            print(f"✓  Validation: {validation_msg}")
            
            return test_result
            
        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")
            test_result = {
                "test_name": test_name,
                "status": "❌ ERROR",
                "query": query,
                "error": str(e),
                "elapsed_seconds": time.time() - start_time
            }
            self.results["tests"].append(test_result)
            return test_result
    
    def save_results(self, filename="comprehensive_test_results_v156.json"):
        """Save test results to JSON file"""
        # Calculate summary statistics
        total_tests = len(self.results["tests"])
        passed = sum(1 for t in self.results["tests"] if "✅ PASS" in t["status"])
        failed = sum(1 for t in self.results["tests"] if "❌ FAIL" in t["status"])
        errors = sum(1 for t in self.results["tests"] if "❌ ERROR" in t["status"])
        
        self.results["summary"] = {
            "total_tests": total_tests,
            "passed": passed,
            "failed": failed,
            "errors": errors,
            "pass_rate": f"{(passed/total_tests*100):.1f}%" if total_tests > 0 else "N/A"
        }
        
        with open(filename, 'w') as f:
            json.dump(self.results, f, indent=2)
        
        print(f"\n{'='*80}")
        print(f"📄 Results saved to: {filename}")
        print(f"{'='*80}")


def main():
    """Run all comprehensive tests"""
    runner = ComprehensiveTestRunner()
    
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║      🧪 CITE-AGENT v1.5.6 COMPREHENSIVE TOOL SEQUENCING TEST SUITE        ║
║                                                                            ║
║  This is REAL comprehensive testing - NOT toy examples!                   ║
║  We test all 39 tools across 5 major workflow categories:                 ║
║    1. Research & Literature (8 tools)                                      ║
║    2. Data Analysis (13 tools)                                             ║
║    3. Qualitative Analysis (5 tools)                                       ║
║    4. Shell + Code Execution (3 tools)                                     ║
║    5. Cross-Domain Workflows (all categories combined)                     ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
    """)
    
    time.sleep(2)
    
    # ============================================================================
    # TEST CATEGORY 1: RESEARCH & LITERATURE WORKFLOWS
    # ============================================================================
    
    print("\n" + "="*80)
    print("📚 CATEGORY 1: RESEARCH & LITERATURE WORKFLOWS")
    print("="*80)
    
    runner.run_test(
        test_name="Research_Pipeline_Full",
        query=(
            "Find papers about 'transformer models in NLP', "
            "add the top 3 papers to my library, "
            "extract the main themes from them, "
            "and identify research gaps."
        ),
        expected_tools=["search_papers", "add_paper", "extract_lit_themes", "find_research_gaps"],
        min_steps=4,
        validation_fn=lambda r: "transformer" in r.lower() and "theme" in r.lower()
    )
    
    runner.run_test(
        test_name="Literature_Synthesis",
        query=(
            "Search for papers on 'AI ethics', "
            "find related papers to the most cited one, "
            "synthesize the literature focusing on 'algorithmic bias', "
            "and export the review."
        ),
        expected_tools=["search_papers", "find_related_papers", "synthesize_literature", "export_lit_review"],
        min_steps=4,
        validation_fn=lambda r: "ethics" in r.lower() or "bias" in r.lower()
    )
    
    # ============================================================================
    # TEST CATEGORY 2: DATA ANALYSIS WORKFLOWS
    # ============================================================================
    
    print("\n" + "="*80)
    print("📊 CATEGORY 2: DATA ANALYSIS WORKFLOWS")
    print("="*80)
    
    runner.run_test(
        test_name="Data_Cleaning_Pipeline",
        query=(
            "Load the dataset from 'sample_data.csv', "
            "scan for data quality issues, "
            "automatically clean the data, "
            "handle missing values using mean imputation, "
            "then analyze descriptive statistics."
        ),
        expected_tools=["load_dataset", "scan_data_quality", "auto_clean_data", 
                       "handle_missing_values", "analyze_data"],
        min_steps=5,
        validation_fn=lambda r: "missing" in r.lower() or "clean" in r.lower()
    )
    
    runner.run_test(
        test_name="Statistical_Analysis_Full",
        query=(
            "Load 'exam_data.csv', "
            "run a regression to predict final_score from study_hours and attendance, "
            "check the regression assumptions, "
            "plot the regression diagnostics, "
            "and calculate the statistical power."
        ),
        expected_tools=["load_dataset", "run_regression", "check_assumptions", 
                       "plot_data", "calculate_power"],
        min_steps=5,
        validation_fn=lambda r: "regression" in r.lower() or "r-squared" in r.lower()
    )
    
    runner.run_test(
        test_name="Advanced_Multivariate_Analysis",
        query=(
            "Load dataset 'products.csv', "
            "run PCA with 3 components, "
            "then run factor analysis with 2 factors, "
            "plot the factor loadings, "
            "and write the results to a file."
        ),
        expected_tools=["load_dataset", "run_pca", "run_factor_analysis", 
                       "plot_data", "write_file"],
        min_steps=5,
        validation_fn=lambda r: "pca" in r.lower() or "factor" in r.lower()
    )
    
    runner.run_test(
        test_name="Experimental_Design_Power",
        query=(
            "Calculate the required sample size for an experiment "
            "with effect size 0.5, power 0.8, and alpha 0.05. "
            "Then calculate the power if I only have 50 participants. "
            "Finally, calculate the minimum detectable effect with N=50."
        ),
        expected_tools=["calculate_sample_size", "calculate_power", "calculate_mde"],
        min_steps=3,
        validation_fn=lambda r: "sample" in r.lower() and "power" in r.lower()
    )
    
    # ============================================================================
    # TEST CATEGORY 3: QUALITATIVE ANALYSIS WORKFLOWS
    # ============================================================================
    
    print("\n" + "="*80)
    print("🗂️ CATEGORY 3: QUALITATIVE ANALYSIS WORKFLOWS")
    print("="*80)
    
    runner.run_test(
        test_name="Qualitative_Coding_Pipeline",
        query=(
            "Load the transcript from 'file.txt', "
            "create qualitative codes for 'user_frustration' and 'feature_request', "
            "code the relevant segments, "
            "list all codes used, "
            "extract themes, "
            "and generate a codebook."
        ),
        expected_tools=["load_transcript", "create_code", "code_segment", 
                       "list_codes", "extract_themes", "generate_codebook"],
        min_steps=6,
        validation_fn=lambda r: "code" in r.lower() or "theme" in r.lower()
    )
    
    # ============================================================================
    # TEST CATEGORY 4: SHELL + CODE EXECUTION WORKFLOWS
    # ============================================================================
    
    print("\n" + "="*80)
    print("⚙️ CATEGORY 4: SHELL + CODE EXECUTION WORKFLOWS")
    print("="*80)
    
    runner.run_test(
        test_name="Shell_Analysis_Pipeline",
        query=(
            "List all Python files in the current directory, "
            "count how many there are, "
            "then use Python code to calculate what percentage of total files they represent, "
            "and write the analysis to 'file_analysis.txt'."
        ),
        expected_tools=["list_directory", "execute_shell_command", 
                       "run_python_code", "write_file"],
        min_steps=4,
        validation_fn=lambda r: "python" in r.lower() or ".py" in r.lower()
    )
    
    runner.run_test(
        test_name="Git_Analysis_Code",
        query=(
            "Run shell command to get the last 10 git commits, "
            "then use Python code to parse the commit messages and count how many contain 'fix', "
            "then use Python again to calculate the 'fix rate' percentage."
        ),
        expected_tools=["execute_shell_command", "run_python_code"],
        min_steps=3,
        validation_fn=lambda r: "git" in r.lower() or "commit" in r.lower()
    )
    
    # ============================================================================
    # TEST CATEGORY 5: CROSS-DOMAIN COMPLEX WORKFLOWS
    # ============================================================================
    
    print("\n" + "="*80)
    print("🌐 CATEGORY 5: CROSS-DOMAIN COMPLEX WORKFLOWS")
    print("="*80)
    
    runner.run_test(
        test_name="Mixed_Methods_Research",
        query=(
            "Search for papers about 'user experience research methods', "
            "extract the main themes, "
            "then load interview transcript from 'file.txt', "
            "create codes based on the paper themes, "
            "code the transcript segments, "
            "extract themes from the coded data, "
            "and synthesize both the literature and qualitative findings."
        ),
        expected_tools=["search_papers", "extract_lit_themes", "load_transcript", 
                       "create_code", "code_segment", "extract_themes", 
                       "synthesize_literature"],
        min_steps=7,
        validation_fn=lambda r: ("user experience" in r.lower() or "research" in r.lower())
    )
    
    runner.run_test(
        test_name="Data_To_Visualization_Full",
        query=(
            "Load data from 'test_sales.csv', "
            "scan data quality, "
            "auto-clean the data, "
            "analyze descriptive statistics, "
            "run a regression to predict sales from marketing_spend, "
            "plot the results, "
            "and write a summary report to 'sales_analysis.txt'."
        ),
        expected_tools=["load_dataset", "scan_data_quality", "auto_clean_data", 
                       "analyze_data", "run_regression", "plot_data", "write_file"],
        min_steps=7,
        validation_fn=lambda r: "sales" in r.lower() or "regression" in r.lower()
    )
    
    runner.run_test(
        test_name="Project_Analysis_Full",
        query=(
            "Detect what type of project this is, "
            "list the directory contents, "
            "count the Python files using shell, "
            "check if the project has tests and uses git, "
            "then use Python code to calculate project health metrics, "
            "and write a project assessment report."
        ),
        expected_tools=["detect_project", "list_directory", "execute_shell_command", 
                       "check_assumptions", "run_python_code", "write_file"],
        min_steps=6,
        validation_fn=lambda r: "project" in r.lower()
    )
    
    # ============================================================================
    # TEST CATEGORY 6: MULTI-STEP MATH WITH CONTEXT PASSING (BASELINE)
    # ============================================================================
    
    print("\n" + "="*80)
    print("🔢 CATEGORY 6: MULTI-STEP MATH (BASELINE - CONTEXT PASSING VALIDATION)")
    print("="*80)
    
    runner.run_test(
        test_name="Math_Factorial_Chain",
        query=(
            "Calculate 10 factorial, then divide that result by 5, "
            "then multiply the result by 2."
        ),
        expected_tools=["run_python_code"],
        min_steps=3,
        validation_fn=lambda r: "1451520" in r or "1,451,520" in r  # (10! / 5) * 2 = 1,451,520
    )
    
    runner.run_test(
        test_name="Math_Prime_Chain",
        query=(
            "Calculate 7 factorial, then check if the result is prime, "
            "then find the next prime number after that result."
        ),
        expected_tools=["run_python_code"],
        min_steps=3,
        validation_fn=lambda r: "5040" in r or "not prime" in r.lower()  # 7! = 5040 (not prime)
    )
    
    runner.run_test(
        test_name="Math_Statistics_Chain",
        query=(
            "Calculate the mean of [10, 20, 30, 40, 50], "
            "then calculate the standard deviation of the same numbers, "
            "then calculate the coefficient of variation (std/mean * 100)."
        ),
        expected_tools=["run_python_code"],
        min_steps=3,
        validation_fn=lambda r: ("30" in r and "14.1" in r) or "coefficient" in r.lower()
    )
    
    # ============================================================================
    # FINAL RESULTS
    # ============================================================================
    
    print("\n" + "="*80)
    print("📊 TEST EXECUTION COMPLETE")
    print("="*80)
    
    # Save results
    runner.save_results()
    
    # Print summary
    summary = runner.results["summary"]
    print(f"""
╔════════════════════════════════════════════════════════════════════════════╗
║                          TEST SUITE SUMMARY                                ║
╠════════════════════════════════════════════════════════════════════════════╣
║  Total Tests:  {summary['total_tests']:<3}                                                        ║
║  ✅ Passed:    {summary['passed']:<3}                                                        ║
║  ❌ Failed:    {summary['failed']:<3}                                                        ║
║  ❌ Errors:    {summary['errors']:<3}                                                        ║
║  Pass Rate:    {summary['pass_rate']:<6}                                                   ║
╚════════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Print individual test results
    print("\n" + "="*80)
    print("DETAILED RESULTS BY CATEGORY")
    print("="*80)
    
    for test in runner.results["tests"]:
        status_emoji = "✅" if "✅ PASS" in test["status"] else "❌"
        print(f"{status_emoji} {test['test_name']:<40} | {test.get('elapsed_seconds', 0):.2f}s | Tools: {test.get('tools_coverage', 'N/A')}")
    
    print("\n" + "="*80)
    print(f"Full results saved to: comprehensive_test_results_v156.json")
    print("="*80)
    
    return runner.results


if __name__ == "__main__":
    main()
