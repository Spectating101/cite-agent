#!/usr/bin/env python3
"""
Conversational UX Testing - Real User Scenarios
================================================

Tests whether the agent:
1. Chooses correct tools from natural language prompts
2. Chains tools together intelligently
3. Presents results in a user-friendly way (not overwhelming JSON)
4. Handles ambiguous requests gracefully
5. Provides helpful context/explanations
"""

import asyncio
import sys
from pathlib import Path
from typing import Dict, Any, List
import json

# Add cite_agent to path
sys.path.insert(0, str(Path(__file__).parent))

from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent


class ConversationalUXTester:
    """Test real-world conversational scenarios"""
    
    def __init__(self):
        self.agent = None
        self.test_results = {
            "scenarios_tested": 0,
            "passed": 0,
            "failed": 0,
            "details": []
        }
    
    async def setup(self):
        """Initialize agent"""
        print("🤖 Initializing Cite-Agent...\n")
        self.agent = EnhancedNocturnalAgent()
        await self.agent.initialize()
        print("✅ Agent ready!\n")
    
    async def test_scenario(
        self,
        name: str,
        user_message: str,
        expected_tools: List[str],
        success_indicators: List[str],
        ux_checks: Dict[str, Any]
    ) -> bool:
        """
        Test a conversational scenario
        
        Args:
            name: Scenario name
            user_message: Natural language prompt
            expected_tools: Tools that should be called
            success_indicators: Keywords/patterns that indicate success
            ux_checks: UX quality checks (output_length, formatting, etc)
        """
        print("=" * 80)
        print(f"📝 SCENARIO: {name}")
        print("=" * 80)
        print(f"👤 User: {user_message}\n")
        
        self.test_results["scenarios_tested"] += 1
        
        try:
            # Send message and get response
            chat_response = await self.agent.call_backend_query(user_message)
            response = chat_response.response if hasattr(chat_response, 'response') else str(chat_response)
            
            print(f"🤖 Agent Response:")
            print("-" * 80)
            print(response)
            print("-" * 80)
            
            # Extract tool calls from agent's history
            tools_called = []
            if hasattr(self.agent, 'conversation_history'):
                for entry in self.agent.conversation_history:
                    if entry.get('role') == 'assistant' and 'tool_calls' in entry:
                        for tool_call in entry['tool_calls']:
                            tools_called.append(tool_call.get('function', {}).get('name', ''))
            
            # Check if expected tools were called
            tools_check = all(tool in tools_called for tool in expected_tools)
            
            # Check for success indicators in response
            indicators_check = all(indicator.lower() in response.lower() for indicator in success_indicators)
            
            # UX Checks
            ux_passed = True
            ux_feedback = []
            
            # Check output length (not overwhelming)
            max_length = ux_checks.get("max_length", 2000)
            if len(response) > max_length:
                ux_passed = False
                ux_feedback.append(f"❌ Response too long ({len(response)} chars > {max_length})")
            else:
                ux_feedback.append(f"✅ Good length ({len(response)} chars)")
            
            # Check for raw JSON dumps (bad UX)
            if response.count('{') > 5 and response.count('}') > 5:
                # Check if it's formatted JSON or raw dump
                if not any(marker in response for marker in ['```json', '**', 'Summary:', 'Results:']):
                    ux_passed = False
                    ux_feedback.append("❌ Contains raw JSON dump (not user-friendly)")
                else:
                    ux_feedback.append("✅ JSON is formatted/contextualized")
            else:
                ux_feedback.append("✅ No overwhelming JSON")
            
            # Check for explanatory text (not just tool output)
            if ux_checks.get("requires_explanation", True):
                explanation_markers = ['here', 'found', 'shows', 'indicates', 'based on', 'this means']
                has_explanation = any(marker in response.lower() for marker in explanation_markers)
                if has_explanation:
                    ux_feedback.append("✅ Includes helpful explanation")
                else:
                    ux_passed = False
                    ux_feedback.append("❌ Missing explanatory context")
            
            # Check for structured formatting
            if ux_checks.get("requires_structure", True):
                structure_markers = ['##', '**', '- ', '\n\n', '1.', '•']
                has_structure = any(marker in response for marker in structure_markers)
                if has_structure:
                    ux_feedback.append("✅ Well-structured output")
                else:
                    ux_feedback.append("⚠️ Could use better formatting")
            
            # Overall pass/fail
            passed = tools_check and indicators_check and ux_passed
            
            # Print results
            print("\n📊 ASSESSMENT:")
            print(f"  Tools Called: {', '.join(tools_called) if tools_called else 'None detected'}")
            print(f"  Expected Tools: {', '.join(expected_tools)}")
            print(f"  Tools Check: {'✅' if tools_check else '❌'}")
            print(f"  Success Indicators: {'✅' if indicators_check else '❌'}")
            print(f"  UX Quality:")
            for feedback in ux_feedback:
                print(f"    {feedback}")
            print(f"\n  RESULT: {'✅ PASS' if passed else '❌ FAIL'}\n")
            
            # Record result
            self.test_results["details"].append({
                "scenario": name,
                "user_message": user_message,
                "tools_called": tools_called,
                "expected_tools": expected_tools,
                "response_length": len(response),
                "ux_feedback": ux_feedback,
                "passed": passed
            })
            
            if passed:
                self.test_results["passed"] += 1
            else:
                self.test_results["failed"] += 1
            
            return passed
            
        except Exception as e:
            print(f"❌ ERROR: {str(e)}\n")
            self.test_results["failed"] += 1
            self.test_results["details"].append({
                "scenario": name,
                "error": str(e),
                "passed": False
            })
            return False
    
    async def run_all_tests(self):
        """Run comprehensive UX testing scenarios"""
        
        # Scenario 1: Simple data question (should be conversational, not raw output)
        await self.test_scenario(
            name="Quick Data Question",
            user_message="What files are in the current directory?",
            expected_tools=["list_directory"],
            success_indicators=["files", "directory"],
            ux_checks={
                "max_length": 1500,
                "requires_explanation": True,
                "requires_structure": True
            }
        )
        
        # Scenario 2: Multi-step analysis (should chain tools smoothly)
        await self.test_scenario(
            name="Multi-Step Analysis",
            user_message="Load test_research_data.csv and tell me if age and score are correlated",
            expected_tools=["load_dataset", "analyze_data"],
            success_indicators=["correlation", "age", "score"],
            ux_checks={
                "max_length": 2000,
                "requires_explanation": True,
                "requires_structure": True
            }
        )
        
        # Scenario 3: Ambiguous request (should ask clarifying questions or make smart choice)
        await self.test_scenario(
            name="Ambiguous Request",
            user_message="Show me some stats",
            expected_tools=["analyze_data", "descriptive_stats"],  # Could use either
            success_indicators=["statistics", "data"],
            ux_checks={
                "max_length": 1500,
                "requires_explanation": True,
                "requires_structure": False  # Might just ask for clarification
            }
        )
        
        # Scenario 4: Visualization (should present nicely, not just ASCII dump)
        await self.test_scenario(
            name="Data Visualization",
            user_message="Create a scatter plot of age vs score from the dataset",
            expected_tools=["plot_data"],
            success_indicators=["plot", "scatter"],
            ux_checks={
                "max_length": 3000,  # ASCII plots can be long
                "requires_explanation": True,
                "requires_structure": True
            }
        )
        
        # Scenario 5: Complex workflow (should guide user through steps)
        await self.test_scenario(
            name="Complex Workflow",
            user_message="I want to analyze my data quality and fix any issues",
            expected_tools=["scan_data_quality", "auto_clean_data"],
            success_indicators=["quality", "issues", "fixed"],
            ux_checks={
                "max_length": 2500,
                "requires_explanation": True,
                "requires_structure": True
            }
        )
        
        # Scenario 6: Implicit tool chaining (should figure out what's needed)
        await self.test_scenario(
            name="Implicit Multi-Tool",
            user_message="What's the regression between score and age, and are the assumptions met?",
            expected_tools=["run_regression", "check_assumptions"],
            success_indicators=["regression", "assumptions", "score", "age"],
            ux_checks={
                "max_length": 2500,
                "requires_explanation": True,
                "requires_structure": True
            }
        )
        
        # Scenario 7: Qualitative coding workflow
        await self.test_scenario(
            name="Qualitative Coding",
            user_message="Create a code called 'optimism' and load this transcript: 'P1: I feel hopeful about the future.'",
            expected_tools=["create_code", "load_transcript"],
            success_indicators=["code", "created", "transcript", "loaded"],
            ux_checks={
                "max_length": 1500,
                "requires_explanation": True,
                "requires_structure": True
            }
        )
        
        # Scenario 8: Literature synthesis
        await self.test_scenario(
            name="Literature Review",
            user_message="Add a paper titled 'Neural Networks' by Smith (2024) about deep learning advances, then synthesize findings",
            expected_tools=["add_paper", "synthesize_literature"],
            success_indicators=["paper", "added", "synthesis"],
            ux_checks={
                "max_length": 2000,
                "requires_explanation": True,
                "requires_structure": True
            }
        )
        
        # Scenario 9: Power analysis (should explain stats concepts)
        await self.test_scenario(
            name="Power Analysis",
            user_message="How many participants do I need for a t-test with medium effect size?",
            expected_tools=["calculate_sample_size"],
            success_indicators=["sample", "participants", "effect"],
            ux_checks={
                "max_length": 1500,
                "requires_explanation": True,
                "requires_structure": True
            }
        )
        
        # Scenario 10: Natural conversation (should respond naturally)
        await self.test_scenario(
            name="Casual Conversation",
            user_message="Hi! Can you help me analyze some data?",
            expected_tools=["chat"],  # Might not call any tools, just chat
            success_indicators=["help", "analyze"],
            ux_checks={
                "max_length": 1000,
                "requires_explanation": False,
                "requires_structure": False
            }
        )
    
    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("📊 CONVERSATIONAL UX TEST SUMMARY")
        print("=" * 80)
        print(f"Total Scenarios: {self.test_results['scenarios_tested']}")
        print(f"✅ Passed: {self.test_results['passed']}")
        print(f"❌ Failed: {self.test_results['failed']}")
        
        pass_rate = (self.test_results['passed'] / self.test_results['scenarios_tested'] * 100) if self.test_results['scenarios_tested'] > 0 else 0
        print(f"Pass Rate: {pass_rate:.1f}%")
        
        if self.test_results['failed'] > 0:
            print("\n❌ FAILED SCENARIOS:")
            for detail in self.test_results['details']:
                if not detail.get('passed', False):
                    print(f"  - {detail['scenario']}")
                    if 'error' in detail:
                        print(f"    Error: {detail['error']}")
        
        print("\n💡 UX INSIGHTS:")
        
        # Analyze average response length
        lengths = [d['response_length'] for d in self.test_results['details'] if 'response_length' in d]
        if lengths:
            avg_length = sum(lengths) / len(lengths)
            print(f"  Average response length: {avg_length:.0f} characters")
            if avg_length > 2000:
                print("    ⚠️ Responses might be too verbose")
            elif avg_length < 200:
                print("    ⚠️ Responses might be too brief")
            else:
                print("    ✅ Good response length")
        
        # Analyze UX feedback patterns
        all_feedback = []
        for detail in self.test_results['details']:
            if 'ux_feedback' in detail:
                all_feedback.extend(detail['ux_feedback'])
        
        if all_feedback:
            positive_feedback = [f for f in all_feedback if '✅' in f]
            negative_feedback = [f for f in all_feedback if '❌' in f]
            
            print(f"\n  Positive UX indicators: {len(positive_feedback)}")
            print(f"  UX issues found: {len(negative_feedback)}")
            
            if negative_feedback:
                print("\n  Common UX issues:")
                # Count unique issues
                issue_counts = {}
                for feedback in negative_feedback:
                    issue = feedback.split('❌')[1].strip() if '❌' in feedback else feedback
                    issue_counts[issue] = issue_counts.get(issue, 0) + 1
                
                for issue, count in sorted(issue_counts.items(), key=lambda x: x[1], reverse=True):
                    print(f"    - {issue} ({count}x)")
        
        # Save detailed results
        results_file = Path(__file__).parent / "conversational_ux_results.json"
        with open(results_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        print(f"\n📄 Detailed results saved to: {results_file.name}")
        
        print("=" * 80 + "\n")


async def main():
    """Run conversational UX testing"""
    print("\n" + "=" * 80)
    print("🎭 CONVERSATIONAL UX TESTING - REAL USER SCENARIOS")
    print("=" * 80)
    print("Testing whether the agent:")
    print("  1. Chooses correct tools from natural language")
    print("  2. Chains tools together smoothly")
    print("  3. Presents results in user-friendly format")
    print("  4. Handles ambiguity gracefully")
    print("  5. Provides helpful context/explanations")
    print("=" * 80 + "\n")
    
    tester = ConversationalUXTester()
    
    try:
        await tester.setup()
        await tester.run_all_tests()
        tester.print_summary()
        
        # Exit with proper code
        exit_code = 0 if tester.test_results['failed'] == 0 else 1
        sys.exit(exit_code)
        
    except KeyboardInterrupt:
        print("\n⚠️ Testing interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Testing failed with error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
