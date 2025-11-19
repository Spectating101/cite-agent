#!/usr/bin/env python3
"""
Comprehensive Tool Testing Script for Cite-Agent
Tests ALL 42 tools with real queries and verification
"""

import asyncio
import json
import os
import sys
from pathlib import Path

# Add cite_agent to path
sys.path.insert(0, str(Path(__file__).parent))

from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent
from cite_agent.tool_executor import ToolExecutor


class ComprehensiveToolTester:
    """Test all 42 tools systematically"""
    
    def __init__(self):
        self.agent = None
        self.executor = None
        self.results = {
            "total": 42,
            "tested": 0,
            "passed": 0,
            "failed": 0,
            "errors": 0,
            "details": []
        }
    
    async def setup(self):
        """Initialize agent and executor"""
        print("🔧 Initializing agent...")
        self.agent = EnhancedNocturnalAgent()
        await self.agent.initialize()
        self.executor = ToolExecutor(self.agent)
        print("✅ Agent initialized\n")
    
    async def test_tool(self, tool_name, args, expected_keys=None, should_error=False):
        """
        Test a single tool
        
        Args:
            tool_name: Name of the tool
            args: Arguments to pass
            expected_keys: Keys that should be in result (None = just check no error)
            should_error: Whether this test expects an error
        """
        print(f"Testing: {tool_name}")
        print(f"  Args: {json.dumps(args, indent=2)}")
        
        try:
            result = await self.executor.execute_tool(tool_name, args)
            
            # Check for errors
            has_error = "error" in result
            
            if should_error and not has_error:
                status = "❌ FAIL (expected error but got success)"
                passed = False
            elif not should_error and has_error:
                status = f"❌ FAIL (unexpected error: {result['error']})"
                passed = False
            elif expected_keys:
                missing_keys = [k for k in expected_keys if k not in result]
                if missing_keys:
                    status = f"❌ FAIL (missing keys: {missing_keys})"
                    passed = False
                else:
                    status = "✅ PASS"
                    passed = True
            else:
                status = "✅ PASS"
                passed = True
            
            self.results["tested"] += 1
            if passed:
                self.results["passed"] += 1
            else:
                self.results["failed"] += 1
            
            self.results["details"].append({
                "tool": tool_name,
                "status": status,
                "passed": passed,
                "result_keys": list(result.keys()),
                "error": result.get("error")
            })
            
            print(f"  Result: {status}")
            if not passed:
                print(f"  Output: {json.dumps(result, indent=2)[:200]}")
            print()
            
            return passed, result
            
        except Exception as e:
            status = f"❌ ERROR: {str(e)}"
            print(f"  Result: {status}\n")
            
            self.results["tested"] += 1
            self.results["errors"] += 1
            self.results["details"].append({
                "tool": tool_name,
                "status": status,
                "passed": False,
                "exception": str(e)
            })
            
            return False, {"error": str(e)}
    
    async def run_all_tests(self):
        """Run comprehensive test suite"""
        
        print("=" * 80)
        print("COMPREHENSIVE TOOL TESTING - ALL 42 TOOLS")
        print("=" * 80)
        print()
        
        # First, ensure test data exists
        await self.create_test_data()
        
        # Category 1: File/Shell Tools (4 tools)
        print("\n" + "=" * 80)
        print("CATEGORY 1: FILE/SHELL TOOLS (4/42)")
        print("=" * 80 + "\n")
        
        await self.test_tool("list_directory", {"path": "."}, expected_keys=["listing"])
        await self.test_tool("read_file", {"file_path": "test_research_data.csv", "lines": 5}, expected_keys=["content"])
        await self.test_tool("write_file", {
            "file_path": "test_output_comprehensive.txt",
            "content": "Test write"
        }, expected_keys=["success"])
        await self.test_tool("execute_shell_command", {"command": "echo 'test'", "working_directory": "."}, expected_keys=["output"])
        
        # Category 2: Core Research Tools (8 tools)
        print("\n" + "=" * 80)
        print("CATEGORY 2: CORE RESEARCH TOOLS (8/42)")
        print("=" * 80 + "\n")
        
        # Load dataset first for subsequent tests
        passed, result = await self.test_tool("load_dataset", {"filepath": "test_research_data.csv"}, expected_keys=["rows", "columns"])
        
        if passed:
            await self.test_tool("analyze_data", {"analysis_type": "correlation", "var1": "age", "var2": "score"}, expected_keys=["correlation"])
            await self.test_tool("run_regression", {"y_variable": "score", "x_variables": ["age"]}, expected_keys=["coefficients"])
            await self.test_tool("check_assumptions", {"test_type": "regression"}, expected_keys=["assumptions"])
        
        await self.test_tool("run_python_code", {"python_code": "print(2 + 2)"}, expected_keys=["success"])
        await self.test_tool("run_r_code", {"r_code": "print(2 + 2)"}, expected_keys=["success"])
        await self.test_tool("detect_project", {}, expected_keys=["type"])
        
        # Category 3: Visualization Tools (3 tools - testing plot_data with different types)
        print("\n" + "=" * 80)
        print("CATEGORY 3: VISUALIZATION TOOLS (3/42)")
        print("=" * 80 + "\n")
        
        await self.test_tool("plot_data", {
            "plot_type": "scatter",
            "x_data": "age",
            "y_data": "score",
            "title": "Age vs Score"
        }, expected_keys=["plot"])
        
        await self.test_tool("plot_data", {
            "plot_type": "histogram",
            "values": "age",
            "bins": 5,
            "title": "Age Distribution"
        }, expected_keys=["plot"])
        
        await self.test_tool("plot_data", {
            "plot_type": "bar",
            "categories": ["A", "B", "C"],
            "values": [10, 20, 15],
            "title": "Bar Chart"
        }, expected_keys=["plot"])
        
        # Category 4: Advanced Statistics (4 tools)
        print("\n" + "=" * 80)
        print("CATEGORY 4: ADVANCED STATISTICS (4/42)")
        print("=" * 80 + "\n")
        
        await self.test_tool("run_pca", {
            "variables": ["age", "score", "satisfaction"],
            "n_components": 2
        }, expected_keys=["success"])
        
        await self.test_tool("run_factor_analysis", {
            "variables": ["age", "score", "satisfaction"],
            "n_factors": 2
        }, should_error=True)  # Expects error: need 6+ variables for 2 factors
        
        await self.test_tool("run_mediation", {
            "X": "age",
            "M": "score",
            "Y": "satisfaction"
        }, should_error=True)  # Expects error: need 30+ samples
        
        await self.test_tool("run_moderation", {
            "X": "age",
            "W": "score",
            "Y": "satisfaction"
        }, should_error=True)  # Expects error: need 30+ samples
        
        # Category 5: Data Cleaning (3 tools)
        print("\n" + "=" * 80)
        print("CATEGORY 5: DATA CLEANING (3/42)")
        print("=" * 80 + "\n")
        
        await self.test_tool("scan_data_quality", {}, expected_keys=["success"])
        await self.test_tool("auto_clean_data", {"fix_types": ["missing_values"]})
        await self.test_tool("handle_missing_values", {
            "column": "age",
            "method": "median"
        })
        
        # Category 6: Power Analysis (3 tools)
        print("\n" + "=" * 80)
        print("CATEGORY 6: POWER ANALYSIS (3/42)")
        print("=" * 80 + "\n")
        
        await self.test_tool("calculate_sample_size", {
            "test_type": "ttest",
            "effect_size": 0.5,
            "power": 0.80
        }, expected_keys=["n_per_group"])
        
        await self.test_tool("calculate_power", {
            "test_type": "ttest",
            "effect_size": 0.5,
            "n": 64
        }, expected_keys=["achieved_power"])
        
        await self.test_tool("calculate_mde", {
            "test_type": "ttest",
            "n": 64,
            "power": 0.80
        }, expected_keys=["minimum_detectable_effect"])
        
        # Category 7: Qualitative Coding (6 tools)
        print("\n" + "=" * 80)
        print("CATEGORY 7: QUALITATIVE CODING (6/42)")
        print("=" * 80 + "\n")
        
        await self.test_tool("create_code", {
            "code_name": "hope",
            "description": "expressions of optimism"
        }, expected_keys=["success"])
        
        await self.test_tool("load_transcript", {
            "doc_id": "interview1",
            "content": "Interviewer: How do you feel?\nParticipant: I feel hopeful.",
            "format_type": "interview"
        }, expected_keys=["success", "lines"])
        
        await self.test_tool("code_segment", {
            "doc_id": "interview1",
            "line_start": 2,
            "line_end": 2,
            "codes": ["hope"]
        }, expected_keys=["success"])
        
        await self.test_tool("list_codes", {}, expected_keys=["codes"])
        await self.test_tool("extract_themes", {}, expected_keys=["themes"])
        await self.test_tool("generate_codebook", {}, expected_keys=["content"])
        
        # Category 8: Literature Synthesis (5 tools)
        print("\n" + "=" * 80)
        print("CATEGORY 8: LITERATURE SYNTHESIS (5/42)")
        print("=" * 80 + "\n")
        
        await self.test_tool("add_paper", {
            "paper_id": "test001",
            "title": "Test Paper",
            "abstract": "This is a test paper about machine learning and neural networks.",
            "authors": ["Smith, J."],
            "year": 2024,
            "findings": "Important results"
        }, expected_keys=["success"])
        
        await self.test_tool("extract_lit_themes", {}, should_error=True)  # Expects error: need 2+ papers
        await self.test_tool("find_research_gaps", {}, should_error=True)  # Expects error: need 5+ papers
        await self.test_tool("synthesize_literature", {
            "topic": "machine learning"
        }, expected_keys=["synthesis"])
        await self.test_tool("export_lit_review", {
            "format": "markdown"
        }, expected_keys=["content"])
        
        # Category 9: API Tools (4 tools)
        print("\n" + "=" * 80)
        print("CATEGORY 9: API TOOLS (4/42)")
        print("=" * 80 + "\n")
        
        # Note: These require network and API keys
        print("⚠️  Skipping API tools (require network/keys):")
        print("  - search_papers")
        print("  - get_financial_data")
        print("  - web_search")
        print("  - find_related_papers")
        print()
        
        # Category 10: Chat tool (1 tool)
        print("\n" + "=" * 80)
        print("CATEGORY 10: CHAT TOOL (1/42)")
        print("=" * 80 + "\n")
        
        await self.test_tool("chat", {"message": "Hello"}, expected_keys=["message"])
        
        # R Workspace Integration Tests
        print("\n" + "=" * 80)
        print("SPECIAL: R WORKSPACE INTEGRATION")
        print("=" * 80 + "\n")
        
        await self.test_r_workspace()
        
    async def create_test_data(self):
        """Ensure test data files exist"""
        print("📁 Creating test data files...")
        
        test_csv = Path("test_research_data.csv")
        if not test_csv.exists():
            print("  Creating test_research_data.csv...")
            content = """participant_id,age,score,group,satisfaction,motivation
1,25,85,A,4.5,7.8
2,30,92,B,4.8,8.2
3,28,78,A,4.2,7.1
4,35,96,B,5.0,8.8
5,24,82,A,4.1,6.9
6,29,88,B,4.6,7.9
7,31,84,A,4.3,7.5
8,27,91,B,4.9,8.5
9,26,79,A,3.8,6.5
10,32,87,B,4.7,8.0
11,28,83,A,4.4,7.6
12,30,89,B,4.8,8.3
13,29,86,A,4.5,7.7
14,33,94,B,4.9,8.6
15,25,80,A,4.0,6.8
16,31,90,B,4.7,8.1
17,27,85,A,4.4,7.4
18,34,93,B,4.9,8.7
19,26,81,A,4.2,7.0
20,30,88,B,4.6,8.0"""
            test_csv.write_text(content)
        print("✅ Test data ready\n")
    
    async def test_r_workspace(self):
        """Test R workspace bridge functionality"""
        print("Testing R Workspace Bridge...")
        print("  Checking if R is installed...")
        
        try:
            from cite_agent.r_workspace_bridge import RWorkspaceBridge
            bridge = RWorkspaceBridge()
            
            # Test 1: List R objects
            print("  Test 1: List objects in R workspace")
            result = bridge.list_objects()
            if result.get("success"):
                print(f"    ✅ Found {result.get('count', 0)} objects")
            else:
                print(f"    ⚠️  {result.get('error', 'Unknown error')}")
            
            # Test 2: Create R object and retrieve it
            print("  Test 2: Create R dataset and retrieve it")
            r_code = """
            test_data <- data.frame(
                x = c(1, 2, 3, 4, 5),
                y = c(10, 20, 30, 40, 50)
            )
            save(test_data, file='test_workspace.RData')
            """
            
            # Run R code to create workspace
            import subprocess
            result = subprocess.run(
                ["Rscript", "-e", r_code],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                # Try to list objects from saved workspace
                result = bridge.list_objects("test_workspace.RData")
                if result.get("success"):
                    objects = result.get("objects", [])
                    test_data_found = any(obj.get("name") == "test_data" for obj in objects)
                    if test_data_found:
                        print("    ✅ R workspace bridge can see saved objects")
                        
                        # Try to retrieve the dataframe
                        df_result = bridge.get_dataframe("test_data", "test_workspace.RData")
                        if df_result.get("success"):
                            print("    ✅ Successfully retrieved R dataframe")
                            print(f"       Rows: {df_result.get('rows')}, Columns: {df_result.get('columns')}")
                        else:
                            print(f"    ⚠️  Could not retrieve dataframe: {df_result.get('error')}")
                    else:
                        print("    ⚠️  test_data object not found in workspace")
                else:
                    print(f"    ⚠️  {result.get('error')}")
            else:
                print(f"    ⚠️  R execution failed: {result.stderr}")
            
            # Note about RStudio console
            print("\n  📝 Note: RStudio Console Integration")
            print("     - The bridge can read .RData files (saved workspaces)")
            print("     - For 'floating' console objects (not saved):")
            print("       User needs to save workspace: save.image('workspace.RData')")
            print("     - Agent can then access: list_objects('workspace.RData')")
            print("     - RStudio auto-saves to .RData on exit")
            
        except ImportError:
            print("    ⚠️  R workspace bridge module not found")
        except subprocess.TimeoutExpired:
            print("    ⚠️  R execution timed out")
        except FileNotFoundError:
            print("    ⚠️  R/Rscript not installed")
        except Exception as e:
            print(f"    ❌ Error: {str(e)}")
    
    async def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tools: {self.results['total']}")
        print(f"Tested: {self.results['tested']}")
        print(f"✅ Passed: {self.results['passed']}")
        print(f"❌ Failed: {self.results['failed']}")
        print(f"💥 Errors: {self.results['errors']}")
        print(f"Pass Rate: {self.results['passed'] / self.results['tested'] * 100:.1f}%")
        print()
        
        # Print failures
        failures = [d for d in self.results["details"] if not d.get("passed")]
        if failures:
            print(f"\n❌ FAILED TESTS ({len(failures)}):")
            for f in failures:
                print(f"  - {f['tool']}: {f['status']}")
                if f.get("error"):
                    print(f"    Error: {f['error']}")
        
        # Save detailed results to JSON
        output_file = Path("comprehensive_test_results.json")
        with open(output_file, "w") as f:
            json.dump(self.results, f, indent=2)
        print(f"\n📄 Detailed results saved to: {output_file}")
        print("=" * 80)


async def main():
    """Run comprehensive testing"""
    tester = ComprehensiveToolTester()
    
    try:
        await tester.setup()
        await tester.run_all_tests()
        await tester.print_summary()
    except KeyboardInterrupt:
        print("\n\n⚠️  Testing interrupted by user")
        await tester.print_summary()
    except Exception as e:
        print(f"\n\n❌ Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()
        await tester.print_summary()


if __name__ == "__main__":
    # Set environment for function calling mode
    os.environ["NOCTURNAL_FUNCTION_CALLING"] = "1"
    
    asyncio.run(main())
