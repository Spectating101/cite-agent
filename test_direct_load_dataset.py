#!/usr/bin/env python3
"""
Direct tool testing - bypassing LLM to test tool execution
"""

import sys
import os

# Add cite_agent to path
sys.path.insert(0, '/home/phyrexian/Downloads/llm_automation/project_portfolio/Cite-Agent')

from cite_agent.research_assistant import DataAnalyzer

def test_load_dataset_directly():
    """Test load_dataset function directly without LLM"""
    print("🧪 Testing load_dataset directly...\n")
    
    analyzer = DataAnalyzer()
    
    # Test 1: Load sample_data.csv
    print("📤 Test: analyzer.load_dataset('sample_data.csv')")
    result = analyzer.load_dataset('sample_data.csv')
    print(f"📥 Result keys: {list(result.keys())}")
    print(f"� Full result:\n{result}")
    print()
    
    return result

if __name__ == "__main__":
    test_load_dataset_directly()
