#!/usr/bin/env python3
"""
Live Agent Intuition Test - Advanced Research Tools
Tests if the LLM agent intuitively uses advanced tools when given research queries
Similar to the load_dataset tool selection test
"""

import subprocess
import sys
import os
import json
import tempfile
from pathlib import Path
from typing import Dict, List, Tuple

# ANSI colors
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
BLUE = '\033[0;34m'
NC = '\033[0m'  # No Color

def load_env():
    """Load environment variables from .env.local"""
    env = os.environ.copy()
    env_file = Path('.env.local')
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env[key] = value
    
    # Enable debug mode
    env['NOCTURNAL_DEBUG'] = '1'
    return env

def run_cite_agent_test(prompt: str, timeout: int = 45) -> Tuple[str, bool]:
    """
    Run cite-agent with a prompt and capture debug output
    Returns: (output, success)
    """
    try:
        env = load_env()
        
        # Run cite-agent (debug mode via NOCTURNAL_DEBUG=1 in env)
        result = subprocess.run(
            ['cite-agent'],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env
        )
        
        output = result.stdout + result.stderr
        return output, result.returncode == 0
    
    except subprocess.TimeoutExpired:
        return "TIMEOUT: Agent took too long", False
    except Exception as e:
        return f"ERROR: {str(e)}", False

def check_tool_called(output: str, expected_tools: List[str]) -> Tuple[bool, str]:
    """
    Check if any of the expected tools were called
    Returns: (success, tool_found)
    """
    for tool in expected_tools:
        # Check for debug markers like [Tool Name] or "tool_name"
        if f'[{tool}]' in output or f'"{tool}"' in output.lower():
            return True, tool
    return False, None

def create_test_data():
    """Create test data files for the tests"""
    
    # Create a simple dataset
    with open('agent_test_data.csv', 'w') as f:
        f.write("participant_id,age,score,group,satisfaction\n")
        for i in range(20):
            group = 'control' if i % 2 == 0 else 'treatment'
            f.write(f"{i+1},{20+i},{70+i*2},{group},{3.5+(i*0.1)}\n")
    
    # Create a transcript
    with open('agent_test_transcript.txt', 'w') as f:
        f.write("""Interview with Participant 1
Interviewer: How do you feel about the program?
P1: I feel hopeful about it. There's definitely motivation to continue.
P1: But there are some barriers - mainly time constraints.

Interview with Participant 2  
Interviewer: What's your experience been like?
P2: Mixed feelings. I see the potential but face barriers with technology.
P2: More support would increase my motivation significantly.
""")
    
    print(f"{GREEN}✅ Test data created{NC}")
    print()

def cleanup_test_data():
    """Remove test data files"""
    files = ['agent_test_data.csv', 'agent_test_transcript.txt', 'quick_test_data.csv', 'pca_test_data.csv']
    for f in files:
        if Path(f).exists():
            Path(f).unlink()

class ToolIntuitionTest:
    def __init__(self):
        self.tests_run = 0
        self.tests_passed = 0
        self.tests_failed = 0
        self.results = []
    
    def run_test(self, test_name: str, prompt: str, expected_tools: List[str], category: str):
        """Run a single intuition test"""
        self.tests_run += 1
        
        print(f"{BLUE}{'='*80}{NC}")
        print(f"{YELLOW}TEST {self.tests_run}: {test_name}{NC}")
        print(f"Category: {category}")
        print(f"Prompt: {prompt}")
        print(f"Expected Tools: {', '.join(expected_tools)}")
        print()
        
        # Run the test
        output, success = run_cite_agent_test(prompt)
        
        # Check if expected tool was called
        tool_called, found_tool = check_tool_called(output, expected_tools)
        
        # Determine pass/fail
        if tool_called:
            print(f"{GREEN}✅ PASS{NC} - Agent intuitively called: {found_tool}")
            self.tests_passed += 1
            result = "PASS"
        else:
            print(f"{RED}❌ FAIL{NC} - Agent did not call expected tools")
            print(f"Expected one of: {', '.join(expected_tools)}")
            
            # Show what it might have done instead
            if 'search_papers' in output.lower():
                print(f"  → Called 'search_papers' instead")
            elif 'load_dataset' in output.lower():
                print(f"  → Called 'load_dataset' (but not the analysis tool)")
            elif 'chat' in output.lower():
                print(f"  → Used 'chat' (no tool selection)")
            else:
                print(f"  → No clear tool usage detected")
            
            self.tests_failed += 1
            result = "FAIL"
        
        # Store result
        self.results.append({
            'test_name': test_name,
            'category': category,
            'prompt': prompt,
            'expected_tools': expected_tools,
            'tool_called': tool_called,
            'found_tool': found_tool,
            'result': result
        })
        
        print()
        return tool_called
    
    def print_summary(self):
        """Print test summary"""
        print()
        print(f"{BLUE}{'='*80}{NC}")
        print(f"{BLUE}TEST SUMMARY{NC}")
        print(f"{BLUE}{'='*80}{NC}")
        print()
        
        # Overall stats
        pass_rate = (self.tests_passed / self.tests_run * 100) if self.tests_run > 0 else 0
        print(f"Total Tests: {self.tests_run}")
        print(f"{GREEN}Passed: {self.tests_passed}{NC}")
        print(f"{RED}Failed: {self.tests_failed}{NC}")
        print(f"Pass Rate: {pass_rate:.1f}%")
        print()
        
        # By category
        categories = {}
        for result in self.results:
            cat = result['category']
            if cat not in categories:
                categories[cat] = {'passed': 0, 'failed': 0}
            if result['result'] == 'PASS':
                categories[cat]['passed'] += 1
            else:
                categories[cat]['failed'] += 1
        
        print("Results by Category:")
        print("-" * 80)
        for cat, stats in categories.items():
            total = stats['passed'] + stats['failed']
            rate = stats['passed'] / total * 100 if total > 0 else 0
            status = f"{GREEN}✅{NC}" if rate >= 80 else f"{RED}❌{NC}"
            print(f"{status} {cat}: {stats['passed']}/{total} ({rate:.0f}%)")
        print()
        
        # Failed tests detail
        if self.tests_failed > 0:
            print(f"{RED}Failed Tests Detail:{NC}")
            print("-" * 80)
            for result in self.results:
                if result['result'] == 'FAIL':
                    print(f"❌ {result['test_name']}")
                    print(f"   Prompt: {result['prompt'][:70]}...")
                    print(f"   Expected: {', '.join(result['expected_tools'])}")
                    print()

def main():
    print()
    print(f"{BLUE}{'='*80}{NC}")
    print(f"{BLUE}LIVE AGENT INTUITION TEST - Advanced Research Tools{NC}")
    print(f"{BLUE}{'='*80}{NC}")
    print()
    print("Testing if the LLM agent intuitively uses advanced tools for research queries")
    print("Similar to the load_dataset tool selection test")
    print()
    
    # Create test data
    create_test_data()
    
    # Initialize test suite
    suite = ToolIntuitionTest()
    
    # =========================================================================
    # Category 1: Data Visualization
    # =========================================================================
    print(f"{BLUE}{'='*80}{NC}")
    print(f"{BLUE}CATEGORY 1: Data Visualization{NC}")
    print(f"{BLUE}{'='*80}{NC}")
    print()
    
    suite.run_test(
        "Plot - Scatter Request",
        "Load agent_test_data.csv and show me a scatter plot of age vs score",
        ["ASCII Plotter", "plot_data", "Plotter"],
        "Visualization"
    )
    
    suite.run_test(
        "Plot - Relationship Visualization",
        "Load agent_test_data.csv and visualize the relationship between age and satisfaction",
        ["ASCII Plotter", "plot_data", "Plotter"],
        "Visualization"
    )
    
    suite.run_test(
        "Plot - Distribution Request",
        "Load agent_test_data.csv and show the distribution of scores as a histogram",
        ["ASCII Plotter", "plot_data", "Plotter"],
        "Visualization"
    )
    
    # =========================================================================
    # Category 2: Qualitative Coding
    # =========================================================================
    print(f"{BLUE}{'='*80}{NC}")
    print(f"{BLUE}CATEGORY 2: Qualitative Research{NC}")
    print(f"{BLUE}{'='*80}{NC}")
    print()
    
    suite.run_test(
        "Qualitative - Create Codebook",
        "I'm analyzing interviews. Create a qualitative code called 'hope' for expressions of optimism",
        ["Qual Coding", "create_code"],
        "Qualitative Research"
    )
    
    suite.run_test(
        "Qualitative - Extract Themes",
        "Load agent_test_transcript.txt and automatically extract common themes from the interview",
        ["Qual Coding", "auto_extract_themes", "load_transcript"],
        "Qualitative Research"
    )
    
    # =========================================================================
    # Category 3: Power Analysis
    # =========================================================================
    print(f"{BLUE}{'='*80}{NC}")
    print(f"{BLUE}CATEGORY 3: Power Analysis{NC}")
    print(f"{BLUE}{'='*80}{NC}")
    print()
    
    suite.run_test(
        "Power - Sample Size Calculation",
        "I'm planning a study. How many participants do I need for a t-test with medium effect size (d=0.5) and 80% power?",
        ["Power", "calculate_sample_size"],
        "Power Analysis"
    )
    
    suite.run_test(
        "Power - Study Planning",
        "What's the minimum detectable effect for a t-test with 50 participants per group and 80% power?",
        ["Power", "calculate_mde"],
        "Power Analysis"
    )
    
    suite.run_test(
        "Power - Achieved Power",
        "I have 30 participants per group. What statistical power do I have to detect a medium effect (d=0.5)?",
        ["Power", "calculate_power"],
        "Power Analysis"
    )
    
    # =========================================================================
    # Category 4: Advanced Statistics
    # =========================================================================
    print(f"{BLUE}{'='*80}{NC}")
    print(f"{BLUE}CATEGORY 4: Advanced Statistics{NC}")
    print(f"{BLUE}{'='*80}{NC}")
    print()
    
    suite.run_test(
        "Advanced Stats - PCA Request",
        "Load agent_test_data.csv and run principal component analysis to reduce dimensionality",
        ["PCA", "run_pca"],
        "Advanced Statistics"
    )
    
    suite.run_test(
        "Advanced Stats - Mediation",
        "Load agent_test_data.csv and test if score mediates the relationship between age and satisfaction",
        ["Mediation", "run_mediation"],
        "Advanced Statistics"
    )
    
    suite.run_test(
        "Advanced Stats - Moderation",
        "Load agent_test_data.csv and test if group moderates the effect of age on score",
        ["Moderation", "run_moderation"],
        "Advanced Statistics"
    )
    
    # =========================================================================
    # Category 5: Data Cleaning
    # =========================================================================
    print(f"{BLUE}{'='*80}{NC}")
    print(f"{BLUE}CATEGORY 5: Data Cleaning{NC}")
    print(f"{BLUE}{'='*80}{NC}")
    print()
    
    suite.run_test(
        "Data Cleaning - Quality Scan",
        "Load agent_test_data.csv and scan for data quality issues like missing values or outliers",
        ["Data Cleaning", "scan_data_quality"],
        "Data Cleaning"
    )
    
    # =========================================================================
    # Category 6: Literature Synthesis
    # =========================================================================
    print(f"{BLUE}{'='*80}{NC}")
    print(f"{BLUE}CATEGORY 6: Literature Synthesis{NC}")
    print(f"{BLUE}{'='*80}{NC}")
    print()
    
    suite.run_test(
        "Lit Synthesis - Add Paper",
        "Add this paper to my literature review: Title 'AI in Education', Abstract 'This study examines AI tools in classrooms'",
        ["Lit Synth", "add_paper"],
        "Literature Synthesis"
    )
    
    suite.run_test(
        "Lit Synthesis - Find Gaps",
        "What research gaps exist in my current literature collection?",
        ["Lit Synth", "find_research_gaps"],
        "Literature Synthesis"
    )
    
    # Print summary
    suite.print_summary()
    
    # Save results to JSON
    with open('tool_intuition_test_results.json', 'w') as f:
        json.dump({
            'total_tests': suite.tests_run,
            'passed': suite.tests_passed,
            'failed': suite.tests_failed,
            'pass_rate': suite.tests_passed / suite.tests_run * 100 if suite.tests_run > 0 else 0,
            'results': suite.results
        }, f, indent=2)
    
    print(f"Results saved to: tool_intuition_test_results.json")
    print()
    
    # Cleanup
    cleanup_test_data()
    print(f"{GREEN}✅ Test data cleaned up{NC}")
    print()
    
    # Exit code
    if suite.tests_failed == 0:
        print(f"{GREEN}🎉 ALL INTUITION TESTS PASSED!{NC}")
        print("The agent correctly uses advanced tools when given research queries.")
        return 0
    elif suite.tests_passed / suite.tests_run >= 0.8:
        print(f"{YELLOW}⚠️  MOSTLY PASSING (≥80%){NC}")
        print("The agent mostly uses correct tools, but some improvements needed.")
        return 0
    else:
        print(f"{RED}❌ INTUITION TESTS FAILED{NC}")
        print("The agent is not reliably selecting the correct advanced tools.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
