#!/usr/bin/env python3
"""
Quick smoke test of key advanced tools
Tests a few critical tools to verify they actually work
"""

import subprocess
import sys
import tempfile
import os
from pathlib import Path

def run_cite_agent(prompt, timeout=30):
    """Run cite-agent with a prompt and capture output"""
    try:
        # Load environment
        env = os.environ.copy()
        if Path('.env.local').exists():
            with open('.env.local') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env[key] = value
        
        result = subprocess.run(
            ['cite-agent', '--debug'],
            input=prompt,
            capture_output=True,
            text=True,
            timeout=timeout,
            env=env
        )
        return result.stdout + result.stderr
    except subprocess.TimeoutExpired:
        return "TIMEOUT"
    except Exception as e:
        return f"ERROR: {str(e)}"

def test_plot_data():
    """Test plot_data tool"""
    print("🧪 TEST 1: ASCII Plotting (plot_data)")
    print("-" * 60)
    
    # Create test data
    with open('quick_test_data.csv', 'w') as f:
        f.write("x,y\n")
        for i in range(10):
            f.write(f"{i},{i*2}\n")
    
    prompt = "Load quick_test_data.csv and create a scatter plot of x vs y"
    output = run_cite_agent(prompt)
    
    # Check for success indicators
    success = any([
        '[ASCII Plotter]' in output,
        'plot_data' in output.lower(),
        'scatter' in output.lower()
    ])
    
    if success:
        print("✅ PASS - plot_data tool appears to be working")
    else:
        print("❌ FAIL - plot_data tool may not be working")
        print(f"Output snippet: {output[:500]}")
    
    os.remove('quick_test_data.csv')
    print()
    return success

def test_power_analysis():
    """Test power analysis tools"""
    print("🧪 TEST 2: Power Analysis (calculate_sample_size)")
    print("-" * 60)
    
    prompt = "Calculate the required sample size for a t-test with effect size 0.5 and power 0.80"
    output = run_cite_agent(prompt)
    
    # Check for success indicators
    success = any([
        '[Power' in output,
        'sample size' in output.lower(),
        'n_per_group' in output.lower()
    ])
    
    if success:
        print("✅ PASS - Power analysis appears to be working")
    else:
        print("❌ FAIL - Power analysis may not be working")
        print(f"Output snippet: {output[:500]}")
    
    print()
    return success

def test_qualitative_coding():
    """Test qualitative coding tools"""
    print("🧪 TEST 3: Qualitative Coding (create_code)")
    print("-" * 60)
    
    prompt = "Create a qualitative code named 'hope' with description 'expressions of optimism'"
    output = run_cite_agent(prompt)
    
    # Check for success indicators
    success = any([
        '[Qual Coding]' in output,
        'create_code' in output.lower(),
        'hope' in output.lower()
    ])
    
    if success:
        print("✅ PASS - Qualitative coding appears to be working")
    else:
        print("❌ FAIL - Qualitative coding may not be working")
        print(f"Output snippet: {output[:500]}")
    
    print()
    return success

def test_advanced_stats():
    """Test advanced statistics tools"""
    print("🧪 TEST 4: Advanced Statistics (run_pca)")
    print("-" * 60)
    
    # Create test data with multiple variables
    with open('pca_test_data.csv', 'w') as f:
        f.write("var1,var2,var3\n")
        for i in range(20):
            f.write(f"{i},{i*1.5},{i*0.8}\n")
    
    prompt = "Load pca_test_data.csv and run PCA on all variables"
    output = run_cite_agent(prompt)
    
    # Check for success indicators
    success = any([
        'PCA' in output,
        'principal component' in output.lower(),
        'explained variance' in output.lower()
    ])
    
    if success:
        print("✅ PASS - Advanced statistics (PCA) appears to be working")
    else:
        print("❌ FAIL - Advanced statistics may not be working")
        print(f"Output snippet: {output[:500]}")
    
    os.remove('pca_test_data.csv')
    print()
    return success

def main():
    print()
    print("=" * 80)
    print("QUICK SMOKE TEST - Advanced Research Tools")
    print("=" * 80)
    print()
    print("Testing: plot_data, power_analysis, qualitative_coding, advanced_stats")
    print()
    
    results = []
    
    # Run tests
    results.append(('Plotting', test_plot_data()))
    results.append(('Power Analysis', test_power_analysis()))
    results.append(('Qualitative Coding', test_qualitative_coding()))
    results.append(('Advanced Stats', test_advanced_stats()))
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print()
    print(f"Passed: {passed}/{total} ({passed/total*100:.0f}%)")
    print()
    
    if passed == total:
        print("🎉 All smoke tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed - check output above")
        return 1

if __name__ == '__main__':
    sys.exit(main())
