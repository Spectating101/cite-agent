#!/usr/bin/env python3
"""
Tool Output UX Testing - Check if tool outputs are user-friendly
===============================================================

Tests whether tool outputs are:
1. Not overly verbose/overwhelming
2. Well-formatted and structured  
3. Include helpful context/explanations
4. Present data in digestible chunks
"""

import sys
from pathlib import Path
import json

sys.path.insert(0, str(Path(__file__).parent))

from cite_agent.tool_executor import ToolExecutor


class ToolOutputUXTester:
    """Test UX quality of tool outputs"""
    
    def __init__(self):
        # Create mock agent for executor
        class MockAgent:
            def __init__(self):
                self.debug_mode = False
                
        self.executor = ToolExecutor(MockAgent())
        self.results = {
            "tools_tested": 0,
            "passed": 0,
            "issues": []
        }
    
    def test_tool_ux(self, tool_name: str, args: dict, ux_criteria: dict) -> bool:
        """
        Test a tool's output UX
        
        Args:
            tool_name: Tool to test
            args: Tool arguments
            ux_criteria: Dict with max_length, requires_formatting, etc.
        """
        print(f"\n{'='*80}")
        print(f"Testing: {tool_name}")
        print(f"Args: {json.dumps(args, indent=2)}")
        print(f"{'='*80}")
        
        self.results["tools_tested"] += 1
        
        try:
            # Execute tool
            result = self.executor.execute_tool(tool_name, args)
            
            # Convert to string for UX analysis
            if isinstance(result, dict):
                # Check if it's an error
                if "error" in result:
                    print(f"⚠️ Tool returned error: {result['error']}")
                    return True  # Errors are OK, we're testing UX not functionality
                
                result_str = json.dumps(result, indent=2)
            else:
                result_str = str(result)
            
            print(f"\n📤 OUTPUT ({len(result_str)} chars):")
            print("-" * 80)
            print(result_str[:500] + "..." if len(result_str) > 500 else result_str)
            print("-" * 80)
            
            # UX Checks
            issues = []
            
            # Check 1: Length (not overwhelming)
            max_length = ux_criteria.get("max_output_length", 3000)
            if len(result_str) > max_length:
                issues.append(f"Output too long: {len(result_str)} chars (max {max_length})")
            
            # Check 2: Raw JSON dump check
            if isinstance(result, dict):
                # Count deeply nested objects
                nested_count = result_str.count('{') + result_str.count('[')
                if nested_count > 20:
                    issues.append(f"Too much nested JSON ({nested_count} brackets) - might overwhelm users")
            
            # Check 3: Key usability - are important keys at top level?
            if isinstance(result, dict):
                important_keys = ["success", "error", "result", "data", "message"]
                has_clear_key = any(k in result for k in important_keys)
                if not has_clear_key and len(result) > 3:
                    issues.append("No clear top-level keys (success/error/result/data) - might confuse users")
            
            # Check 4: Readability - check for common UX-friendly patterns
            ux_markers = {
                "has_summary": any(k in (result if isinstance(result, dict) else {}) for k in ["summary", "message", "description"]),
                "has_count": any(k in (result if isinstance(result, dict) else {}) for k in ["count", "total", "rows", "length"]),
                "has_preview": any(k in (result if isinstance(result, dict) else {}) for k in ["preview", "sample", "head"]),
            }
            
            if ux_criteria.get("requires_summary", False) and not ux_markers["has_summary"]:
                issues.append("Missing summary/description for user context")
            
            # Print UX assessment
            print("\n💡 UX ASSESSMENT:")
            print(f"  Output Length: {len(result_str)} chars {'✅' if len(result_str) <= max_length else '⚠️'}")
            print(f"  Has Summary Field: {'✅' if ux_markers['has_summary'] else '➖'}")
            print(f"  Has Count Info: {'✅' if ux_markers['has_count'] else '➖'}")
            print(f"  Has Preview: {'✅' if ux_markers['has_preview'] else '➖'}")
            
            if issues:
                print(f"\n⚠️ UX ISSUES FOUND:")
                for issue in issues:
                    print(f"  - {issue}")
                self.results["issues"].append({
                    "tool": tool_name,
                    "issues": issues
                })
                return False
            else:
                print(f"\n✅ UX QUALITY: GOOD")
                self.results["passed"] += 1
                return True
            
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            return False
    
    def run_tests(self):
        """Run all UX tests"""
        print("\n" + "="*80)
        print("🎨 TOOL OUTPUT UX TESTING")
        print("="*80)
        print("Testing whether tool outputs are user-friendly:\n")
        print("  ✅ Not overwhelming (reasonable length)")
        print("  ✅ Well-structured (clear keys)")
        print("  ✅ Include helpful context")
        print("  ✅ Easy to understand at a glance")
        print("="*80)
        
        # Test file operations
        self.test_tool_ux(
            "list_directory",
            {"path": "."},
            {"max_output_length": 2000, "requires_summary": False}
        )
        
        self.test_tool_ux(
            "read_file",
            {"file_path": "README.md", "lines": 20},
            {"max_output_length": 3000, "requires_summary": False}
        )
        
        # Test data analysis
        self.test_tool_ux(
            "load_dataset",
            {"filepath": "test_research_data.csv"},
            {"max_output_length": 2000, "requires_summary": True}
        )
        
        self.test_tool_ux(
            "analyze_data",
            {"analysis_type": "correlation", "var1": "age", "var2": "score"},
            {"max_output_length": 1000, "requires_summary": True}
        )
        
        # Test visualization
        self.test_tool_ux(
            "plot_data",
            {"plot_type": "scatter", "x_data": "age", "y_data": "score", "title": "Age vs Score"},
            {"max_output_length": 2500, "requires_summary": False}
        )
        
        # Test data cleaning
        self.test_tool_ux(
            "scan_data_quality",
            {},
            {"max_output_length": 2500, "requires_summary": True}
        )
        
        # Test qualitative coding
        self.test_tool_ux(
            "create_code",
            {"code_name": "optimism", "description": "expressions of hope"},
            {"max_output_length": 500, "requires_summary": False}
        )
        
        self.test_tool_ux(
            "list_codes",
            {},
            {"max_output_length": 1500, "requires_summary": True}
        )
        
        # Test power analysis
        self.test_tool_ux(
            "calculate_sample_size",
            {"test_type": "ttest", "effect_size": 0.5, "power": 0.8},
            {"max_output_length": 1000, "requires_summary": True}
        )
        
        # Print summary
        print("\n" + "="*80)
        print("📊 UX TEST SUMMARY")
        print("="*80)
        print(f"Tools Tested: {self.results['tools_tested']}")
        print(f"✅ Good UX: {self.results['passed']}")
        print(f"⚠️ Has Issues: {len(self.results['issues'])}")
        
        pass_rate = (self.results['passed'] / self.results['tools_tested'] * 100) if self.results['tools_tested'] > 0 else 0
        print(f"UX Quality Rate: {pass_rate:.1f}%")
        
        if self.results['issues']:
            print("\n⚠️ TOOLS WITH UX ISSUES:")
            for item in self.results['issues']:
                print(f"\n  {item['tool']}:")
                for issue in item['issues']:
                    print(f"    - {issue}")
        
        print("\n💡 RECOMMENDATIONS:")
        if pass_rate < 70:
            print("  ⚠️ Many tools have UX issues - consider:")
            print("    - Adding summary fields to outputs")
            print("    - Reducing output verbosity")
            print("    - Providing clearer top-level structure")
        elif pass_rate < 90:
            print("  ✅ Most tools have good UX, minor improvements needed")
        else:
            print("  ✅ Excellent UX across all tools!")
        
        print("="*80 + "\n")
        
        return pass_rate


if __name__ == "__main__":
    tester = ToolOutputUXTester()
    pass_rate = tester.run_tests()
    
    # Exit with appropriate code
    sys.exit(0 if pass_rate >= 70 else 1)
