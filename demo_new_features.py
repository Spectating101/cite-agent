#!/usr/bin/env python3
"""
Real-world demonstration of new features:
Shows how cite-agent can now analyze in-memory data like a research assistant
"""

import pandas as pd
import numpy as np

# Simulate a researcher's data analysis session
print("="*70)
print("SIMULATING RESEARCHER'S DATA ANALYSIS SESSION")
print("="*70)

# Create realistic research data
print("\n1. Loading research data...")
survey_data = pd.DataFrame({
    'participant_id': range(1, 101),
    'age': np.random.randint(18, 65, 100),
    'treatment_group': np.random.choice(['Control', 'Treatment'], 100),
    'pre_test_score': np.random.normal(50, 10, 100),
    'post_test_score': np.random.normal(55, 12, 100),
    'satisfaction': np.random.randint(1, 8, 100),
    'completion_time_min': np.random.normal(45, 15, 100)
})

print(f"   ✅ Loaded survey_data: {survey_data.shape[0]} participants")
print(f"      Columns: {list(survey_data.columns)}")

# Create summary statistics
print("\n2. Computing preliminary statistics...")
summary_stats = survey_data.groupby('treatment_group').agg({
    'pre_test_score': ['mean', 'std'],
    'post_test_score': ['mean', 'std'],
    'satisfaction': 'mean'
}).round(2)

print("   ✅ Created summary_stats table")

# Now demonstrate cite-agent's new workspace features
print("\n" + "="*70)
print("DEMONSTRATING CITE-AGENT'S NEW CAPABILITIES")
print("="*70)

import asyncio
import sys
sys.path.insert(0, '.')

from cite_agent.enhanced_ai_agent import EnhancedNocturnalAgent

async def demo():
    agent = EnhancedNocturnalAgent()
    await agent.initialize()

    # Feature 1: Workspace Inspection
    print("\n📦 FEATURE 1: Workspace Inspection")
    print("-" * 70)
    result = agent.describe_workspace()

    if 'Python' in result:
        py_workspace = result['Python']
        print(f"Found {py_workspace.get('total_objects', 0)} objects in Python workspace")
        print(f"Total size: {py_workspace.get('total_size_mb', 0):.4f} MB")

        print("\nData objects available:")
        for obj in py_workspace.get('objects', []):
            if obj['name'] in ['survey_data', 'summary_stats']:
                dims = obj.get('dimensions', [])
                dims_str = f"{dims[0]}×{dims[1]}" if len(dims) == 2 else str(dims)
                print(f"  • {obj['name']}: {obj['type']} ({dims_str})")

    # Feature 2: Inspect specific object
    print("\n🔍 FEATURE 2: Object Inspection")
    print("-" * 70)
    result = agent.inspect_workspace_object('survey_data')

    if 'error' not in result:
        print(f"Object: {result.get('name')}")
        print(f"Type: {result.get('type')}")
        print(f"Dimensions: {result.get('dimensions')}")
        print(f"Columns: {', '.join(result.get('columns', []))}")

    # Feature 3: Data preview
    print("\n👁️  FEATURE 3: Data Preview")
    print("-" * 70)
    result = agent.get_workspace_data('survey_data', limit=5)

    if 'error' not in result:
        print(f"Showing {result.get('shown_rows')} of {result.get('total_rows')} rows:")
        for i, row in enumerate(result.get('data', [])[:5], 1):
            print(f"  Row {i}: {row}")

    # Feature 4: Statistical Summary
    print("\n📊 FEATURE 4: Statistical Summary with Auto-Methods")
    print("-" * 70)
    result = agent.summarize_data('survey_data')

    if 'error' not in result:
        print(f"Dataset: {result.get('name')}")
        print(f"Shape: {result.get('shape')[0]} rows × {result.get('shape')[1]} columns")

        print(f"\nAuto-generated methods section:")
        print("-" * 70)
        methods = result.get('methods_text', '')
        print(methods[:500] + "..." if len(methods) > 500 else methods)

    # Feature 5: Column Search
    print("\n🔎 FEATURE 5: Cross-DataFrame Column Search")
    print("-" * 70)
    result = agent.search_columns('score')

    if 'error' not in result:
        print(f"Found {result.get('total_matches')} columns matching 'score':")
        for match in result.get('results', []):
            print(f"  • {match.get('object')}.{match.get('column')} ({match.get('type')})")

    # Feature 6: Code Templates
    print("\n📝 FEATURE 6: Ready-to-Use Statistical Code")
    print("-" * 70)
    result = agent.get_code_template(
        'ttest_independent_r',
        data='survey_data',
        variable='post_test_score',
        group_var='treatment_group',
        group1='Control',
        group2='Treatment'
    )

    if 'error' not in result:
        print("Generated R code for independent t-test:")
        print("-" * 70)
        print(result.get('code', ''))

        if result.get('citations'):
            print("\nCitations to include:")
            for citation in result.get('citations', []):
                print(f"  • {citation}")

    # Feature 7: List all templates
    print("\n📋 FEATURE 7: Available Templates")
    print("-" * 70)
    result = agent.list_code_templates()

    print(f"Total templates available: {result.get('total')}")
    print("\nR Templates:")
    for template in result.get('templates', []):
        if template['language'] == 'R':
            print(f"  • {template['name']}: {template['description'][:60]}...")

    await agent.close()

# Run demo
asyncio.run(demo())

print("\n" + "="*70)
print("SUMMARY")
print("="*70)
print("""
New features demonstrated:
✅ Workspace inspection - See all data in memory
✅ Object details - Dimensions, columns, types
✅ Data preview - View actual rows
✅ Statistical summaries - Auto-generate methods sections
✅ Column search - Find variables across dataframes
✅ Code templates - Ready-to-use analysis code
✅ Citation management - Proper statistical references

VALUE PROPOSITION:
Before: "Upload your CSV and I'll try to help"
After:  "I can see your R/Python/Stata data in memory, analyze it,
         generate proper statistical code, and give you citation-ready methods"

This is HUGE for academic researchers!
""")
