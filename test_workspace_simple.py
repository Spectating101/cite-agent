#!/usr/bin/env python3
"""
Simple test script for workspace inspection functionality (no pandas required)
"""

from cite_agent import EnhancedNocturnalAgent

# Create some sample data in Python workspace
print("Creating sample data in Python workspace...\n")

# Create simple Python data structures
sales_data = [
    {'date': '2024-01-01', 'revenue': 1500, 'costs': 800},
    {'date': '2024-01-02', 'revenue': 2200, 'costs': 1100},
    {'date': '2024-01-03', 'revenue': 1800, 'costs': 900},
]

customer_names = ['Alice', 'Bob', 'Charlie', 'Diana', 'Eve']
customer_values = [10000, 15000, 8000, 12000, 20000]

total_revenue = sum(item['revenue'] for item in sales_data)
avg_costs = sum(item['costs'] for item in sales_data) / len(sales_data)
regions = ['North', 'South', 'East', 'West']

print("Sample data created:")
print(f"  - sales_data: list with {len(sales_data)} items")
print(f"  - customer_names: list with {len(customer_names)} items")
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
print("2. Inspecting 'sales_data' object:")
print("-" * 60)
result = agent.inspect_workspace_object('sales_data', platform="Python")
if 'error' not in result:
    print(f"Name: {result['name']}")
    print(f"Type: {result['type']}")
    print(f"Class: {result['class']}")
    if result.get('size'):
        print(f"Size: {result['size']}")
    if result.get('preview'):
        print(f"Preview: {result['preview'][:200]}...")
else:
    print(f"Error: {result['error']}")
print()

# Test 3: Get actual data
print("3. Viewing data from 'customer_names':")
print("-" * 60)
result = agent.get_workspace_data('customer_names', limit=10, platform="Python")
if 'error' not in result:
    print(f"Type: {result['type']}")
    print(f"Total length: {result.get('total_length', 'N/A')}")
    print(f"Data: {result.get('data', result.get('preview', 'N/A'))}")
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
    print()
    print("Sample objects:")
    for obj in result['objects'][:5]:
        print(f"  - {obj['name']:20s} ({obj['class']})")
else:
    print(f"Error: {result['error']}")
print()

print("=" * 60)
print("✅ WORKSPACE INSPECTION TEST COMPLETE")
print("=" * 60)
