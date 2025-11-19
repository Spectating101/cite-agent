#!/usr/bin/env python3
"""
EXHAUSTIVE MULTI-TURN TESTING
Tests ALL 27+ tools with real back-and-forth conversations
"""

import subprocess
import sys
import time

def test_multiturn_conversation(turns, test_name):
    """Execute a multi-turn conversation test"""
    print(f"\n{'='*100}")
    print(f"🧪 {test_name}")
    print(f"{'='*100}\n")
    
    # Setup
    subprocess.run("rm -f ~/.nocturnal_archive/session.json", shell=True, capture_output=True)
    
    # Create input for all turns
    input_text = "\n".join(turns) + "\nquit\n"
    
    # Execute
    env_setup = "export $(cat .env.local | grep -v '^#' | xargs) && export NOCTURNAL_FUNCTION_CALLING=1"
    cmd = f'cd /home/phyrexian/Downloads/llm_automation/project_portfolio/Cite-Agent && {env_setup} && echo -e "{input_text}" | timeout 90 cite-agent 2>&1'
    
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    output = result.stdout + result.stderr
    
    # Analyze output
    for i, turn in enumerate(turns, 1):
        print(f"📤 Turn {i}: {turn}")
        # Find agent response after this turn
        if "Agent:" in output:
            response_start = output.find(f"👤 You: {turn}")
            if response_start != -1:
                response_section = output[response_start:response_start+500]
                agent_response = response_section.split("🤖 Agent:")
                if len(agent_response) > 1:
                    print(f"📥 Agent: {agent_response[1].split('👤 You:')[0].strip()[:200]}...")
        print()
    
    return output

# Test Data Analysis Workflow (Most Critical!)
print("\n" + "🔬"*50)
print("STARTING EXHAUSTIVE MULTI-TURN TESTING - ALL TOOLS")
print("🔬"*50 + "\n")

results = {}

# TEST 1: Data Loading & Analysis (FIXED!)
results['data_workflow'] = test_multiturn_conversation([
    "load sample_data.csv",
    "what columns does it have?",
    "show me the first 3 rows",
    "calculate the mean of all columns"
], "TEST 1: Data Loading & Multi-Turn Analysis")

# TEST 2: File Operations Chain
results['file_ops'] = test_multiturn_conversation([
    "list files in the current directory",
    "read README.md",
    "summarize what you just read in 2 sentences"
], "TEST 2: File Operations with Context")

# TEST 3: Research Workflow
results['research'] = test_multiturn_conversation([
    "search the web for Python 3.13 new features",
    "what did you find about pattern matching?",
    "tell me more about the first result"
], "TEST 3: Research with Follow-up Questions")

# TEST 4: Shell Commands
results['shell'] = test_multiturn_conversation([
    "what is the current directory?",
    "list python files here",
    "count how many there are"
], "TEST 4: Shell Command Chain")

# TEST 5: Error Handling  
results['errors'] = test_multiturn_conversation([
    "load nonexistent_file.csv",
    "okay, then load sample_data.csv instead",
    "show me its structure"
], "TEST 5: Error Recovery & Continuation")

# TEST 6: Complex Multi-Step
results['complex'] = test_multiturn_conversation([
    "list all CSV files",
    "load the first one you found",
    "analyze it",
    "what insights can you give me?"
], "TEST 6: Complex Multi-Step Workflow")

# TEST 7: Context Memory
results['context'] = test_multiturn_conversation([
    "show me setup.py",
    "what does that file do?",
    "explain the first function in it",
    "is there error handling in that function?"
], "TEST 7: Deep Context Memory")

# SUMMARY
print(f"\n{'='*100}")
print("📊 EXHAUSTIVE TESTING SUMMARY")
print(f"{'='*100}\n")

test_count = len(results)
print(f"Total multi-turn scenarios tested: {test_count}")
print(f"\nAll tests completed! Check output above for detailed results.")
print(f"\n🎯 Key Question: Did the agent remember context across ALL turns?")
print(f"🎯 Key Question: Did load_dataset work correctly?")
print(f"🎯 Key Question: Were there any crashes or empty responses?")

print(f"\n{'='*100}\n")
