#!/usr/bin/env python3
"""
Test script for workspace inspection functionality
"""

from cite_agent import EnhancedNocturnalAgent
import pandas as pd
import numpy as np

# Create some sample data in Python workspace
print("Creating sample data in Python workspace...\n")

# Create a dataframe
df_sales = pd.DataFrame({
    'date': pd.date_range('2024-01-01', periods=10),
    'revenue': np.random.randint(1000, 5000, 10),
    'costs': np.random.randint(500, 2000, 10),
    'region': ['North', 'South', 'East', 'West'] * 2 + ['North', 'South']
})

# Create another dataframe
df_customers = pd.DataFrame({
    'customer_id': range(1, 6),
    'name': ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'],
    'lifetime_value': [10000, 15000, 8000, 12000, 20000]
})

# Create some variables
total_revenue = df_sales['revenue'].sum()
avg_costs = df_sales['costs'].mean()
regions = ['North', 'South', 'East', 'West']

print("Sample data created:")
print(f"  - df_sales: {df_sales.shape}")
print(f"  - df_customers: {df_customers.shape}")
print(f"  - total_revenue: {total_revenue}")
print(f"  - avg_costs: {avg_costs}")
print(f"  - regions: {regions}")
print()

# Now test workspace inspection
print("=" * 60)
print("TESTING WORKSPACE INSPECTION")
print("=" * 60)
print()

agent = EnhancedNocturnalAgent()

# Set Python namespace to current globals
python_inspector = agent.workspace_manager.get_inspector("Python")
if python_inspector:
    python_inspector.set_namespace(globals())

# Test 1: List workspace objects
print("1. Listing workspace objects:")
print("-" * 60)
result = agent.list_workspace_objects(platform="Python")
if 'error' not in result:
    print(f"Platform: {result['platform']}")
    print(f"Total objects: {result['total_objects']}")
    print()
    print("Objects:")
    for obj in result['objects']:
        print(f"  - {obj['name']:20s} {obj['type']:15s} {obj['class']:15s}", end="")
        if obj.get('dimensions'):
            print(f" {obj['dimensions']}", end="")
        elif obj.get('size'):
            print(f" (size: {obj['size']})", end="")
        print()
else:
    print(f"Error: {result['error']}")
print()

# Test 2: Inspect specific object
print("2. Inspecting 'df_sales' object:")
print("-" * 60)
result = agent.inspect_workspace_object('df_sales', platform="Python")
if 'error' not in result:
    print(f"Name: {result['name']}")
    print(f"Type: {result['type']}")
    print(f"Class: {result['class']}")
    print(f"Dimensions: {result['dimensions']}")
    print(f"Columns: {result['columns']}")
    if 'metadata' in result and 'column_types' in result['metadata']:
        print("Column types:")
        for col, dtype in result['metadata']['column_types'].items():
            print(f"  - {col}: {dtype}")
else:
    print(f"Error: {result['error']}")
print()

# Test 3: Get actual data
print("3. Viewing data from 'df_sales':")
print("-" * 60)
result = agent.get_workspace_data('df_sales', limit=5, platform="Python")
if 'error' not in result:
    print(f"Type: {result['type']}")
    print(f"Total rows: {result['total_rows']}")
    print(f"Showing: {result['shown_rows']} rows")
    print(f"Truncated: {result['truncated']}")
    print()
    print("Data preview:")
    for i, row in enumerate(result['data'], 1):
        print(f"  Row {i}: {row}")
else:
    print(f"Error: {result['error']}")
print()

# Test 4: Describe entire workspace
print("4. Describing entire workspace:")
print("-" * 60)
result = agent.describe_workspace(platform="Python")
if 'error' not in result:
    print(f"Platform: {result['platform']}")
    print(f"Total objects: {result['total_objects']}")
    print(f"Total size: {result['total_size_mb']:.4f} MB")
    print(f"Environment: {result['environment_name']}")
else:
    print(f"Error: {result['error']}")
print()

print("=" * 60)
print("✅ WORKSPACE INSPECTION TEST COMPLETE")
print("=" * 60)
