#!/usr/bin/env python3
"""
Test response quality of cite-agent to identify formatting issues
"""

import subprocess
import sys
import time

def test_agent_response(question):
    """Send a question to cite-agent and capture the response"""
    print(f"\n{'='*80}")
    print(f"Testing: {question}")
    print('='*80)
    
    # Use expect-like interaction
    proc = subprocess.Popen(
        ['cite-agent'],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    try:
        # Wait for prompt
        time.sleep(2)
        
        # Send "1" to resume session
        proc.stdin.write("1\n")
        proc.stdin.flush()
        time.sleep(1)
        
        # Send the question
        proc.stdin.write(f"{question}\n")
        proc.stdin.flush()
        time.sleep(5)  # Wait for response
        
        # Send quit
        proc.stdin.write("quit\n")
        proc.stdin.flush()
        time.sleep(1)
        
        # Get all output
        output, _ = proc.communicate(timeout=5)
        
        # Extract just the agent's response
        lines = output.split('\n')
        response_started = False
        agent_response = []
        
        for line in lines:
            if '👤 You:' in line and question[:20] in line:
                response_started = True
                continue
            if response_started:
                if '👤 You:' in line and 'quit' in line:
                    break
                if '🤖 Agent:' in line:
                    agent_response.append(line)
                elif response_started and agent_response:
                    agent_response.append(line)
        
        response_text = '\n'.join(agent_response)
        print("\n🤖 AGENT RESPONSE:")
        print(response_text)
        
        # Check for issues
        issues = []
        if 'We need to' in response_text:
            issues.append("❌ Internal thinking leaked: 'We need to'")
        if 'Probably' in response_text:
            issues.append("❌ Uncertainty language leaked: 'Probably'")
        if '{"command":' in response_text or '{"tool":' in response_text:
            issues.append("❌ JSON tool calls exposed in response")
        if 'Let\'s try:' in response_text:
            issues.append("❌ Planning language exposed")
        
        if issues:
            print("\n⚠️ ISSUES FOUND:")
            for issue in issues:
                print(f"  {issue}")
            return False
        else:
            print("\n✅ Response looks clean!")
            return True
            
    except Exception as e:
        print(f"❌ Error: {e}")
        proc.kill()
        return False

def main():
    test_questions = [
        "what is the current working directory?",
        "can you find folders starting with 'test_' in this directory?",
        "what python version are we running?",
        "can you help analyze a CSV file?",
    ]
    
    results = []
    for question in test_questions:
        result = test_agent_response(question)
        results.append((question, result))
        time.sleep(2)  # Pause between tests
    
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for question, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status}: {question[:50]}")
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n✅ All tests passed! Response quality is good.")
        return 0
    else:
        print(f"\n❌ {total - passed} tests failed. Response quality needs improvement.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
