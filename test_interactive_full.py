#!/usr/bin/env python3
"""
Comprehensive interactive test of cite-agent with proper login flow
"""
import subprocess
import time
import sys

def test_cite_agent_thoroughly():
    """Test cite-agent with actual login and interaction"""
    
    print("🧪 COMPREHENSIVE CITE-AGENT TEST")
    print("=" * 70)
    print()
    
    # Test 1: Check CLI entry point exists
    print("📝 Test 1: Verify CLI entry point...")
    result = subprocess.run(['which', 'cite-agent'], capture_output=True, text=True)
    if result.returncode == 0:
        print(f"✅ cite-agent found at: {result.stdout.strip()}")
    else:
        print("❌ cite-agent command not found!")
        return False
    
    # Test 2: Check version
    print("\n📝 Test 2: Check version...")
    result = subprocess.run(['cite-agent', '--version'], capture_output=True, text=True, timeout=10)
    print(result.stdout)
    if "1.4." in result.stdout:
        print("✅ Version check passed")
    else:
        print(f"⚠️ Unexpected version output")
    
    # Test 3: Interactive login and query test
    print("\n📝 Test 3: Full interactive test with login...")
    print("   Login: s1133958@mail.yzu.edu.tw / s1133958")
    print("   Query: Simple research question")
    print()
    
    # Create input script - including ALL prompts
    test_input = """s1133958@mail.yzu.edu.tw
Y
Y
s1133958
s1133958
What is deep learning in 2 sentences?
exit
"""
    
    try:
        proc = subprocess.Popen(
            ['cite-agent'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1
        )
        
        # Send input
        stdout, stderr = proc.communicate(input=test_input, timeout=60)
        
        print("--- STDOUT ---")
        print(stdout[:2000])  # First 2000 chars
        
        if stderr:
            print("\n--- STDERR ---")
            print(stderr[:1000])
        
        # Analyze output
        print("\n" + "=" * 70)
        print("📊 ANALYSIS:")
        print("=" * 70)
        
        checks = {
            "Login prompt shown": "email" in stdout.lower() or "login" in stdout.lower(),
            "Session created": "session" in stdout.lower() or "signed in" in stdout.lower(),
            "Query processed": len(stdout) > 500,
            "Response generated": "deep learning" in stdout.lower() or "neural" in stdout.lower(),
            "No crashes": proc.returncode == 0 or proc.returncode is None,
            "Citations present": "et al" in stdout or "(" in stdout and ")" in stdout,
        }
        
        passed = sum(checks.values())
        total = len(checks)
        
        for check, result in checks.items():
            status = "✅" if result else "❌"
            print(f"{status} {check}")
        
        print(f"\n📊 Score: {passed}/{total} checks passed")
        
        if passed >= total * 0.7:  # 70% threshold
            print("\n🎉 OVERALL: PASS - Package is functional!")
            return True
        else:
            print("\n⚠️ OVERALL: FAIL - Package has issues")
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Test timed out after 60 seconds")
        proc.kill()
        return False
    except Exception as e:
        print(f"❌ Error during test: {e}")
        return False

if __name__ == "__main__":
    success = test_cite_agent_thoroughly()
    sys.exit(0 if success else 1)
