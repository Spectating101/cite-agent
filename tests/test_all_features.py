#!/usr/bin/env python3
"""
Comprehensive test suite for all new data analysis features.
Tests: statistical summaries, method detection, academic formatting, smart search, code templates.
"""

from cite_agent import EnhancedNocturnalAgent
import sys

def test_statistical_summary():
    """Test statistical summary and data quality checks."""
    print("\n" + "="*80)
    print("TEST 1: Statistical Summary & Data Quality")
    print("="*80)

    # Create sample data
    sales_data = [
        {'date': '2024-01-01', 'revenue': 1500, 'costs': 800, 'region': 'North'},
        {'date': '2024-01-02', 'revenue': 2200, 'costs': 1100, 'region': 'South'},
        {'date': '2024-01-03', 'revenue': 1800, 'costs': 900, 'region': 'East'},
        {'date': '2024-01-04', 'revenue': 2500, 'costs': None, 'region': 'West'},  # Missing value
        {'date': '2024-01-05', 'revenue': 1900, 'costs': 950, 'region': 'North'},
        {'date': '2024-01-06', 'revenue': 5000, 'costs': 1200, 'region': 'South'},  # Outlier
    ]

    agent = EnhancedNocturnalAgent()
    python_inspector = agent.workspace_manager.get_inspector("Python")
    if python_inspector:
        # Add data to namespace
        globals()['sales_data_df'] = sales_data
        python_inspector.set_namespace(globals())

    # Test summarize_data
    print("\n📊 Generating statistical summary...")
    result = agent.summarize_data('sales_data_df', platform="Python")

    if 'error' in result:
        print(f"❌ Error: {result['error']}")
        return False

    print(f"✅ Summary generated for: {result['name']}")
    print(f"   Shape: {result['shape']}")
    print(f"   Numeric columns: {result['numeric_columns']}")
    print(f"   Categorical columns: {result['categorical_columns']}")

    print(f"\n📈 Statistics Table:")
    print(result['stats_table'])

    print(f"\n📝 Auto-Generated Methods Section:")
    print(result['methods_text'])

    print(f"\n⚠️  Data Quality Issues ({len(result['quality_issues'])} found):")
    for issue in result['quality_issues']:
        print(f"  [{issue['severity'].upper()}] {issue['description']}")
        if issue['suggestion']:
            print(f"    Suggestion: {issue['suggestion']}")

    return True


def test_method_detection():
    """Test automatic method detection from code."""
    print("\n" + "="*80)
    print("TEST 2: Method Detection & Citation Automation")
    print("="*80)

    agent = EnhancedNocturnalAgent()

    # Test with R code
    r_code = """
    # Run t-test
    result <- t.test(revenue ~ region, data = sales_data)

    # Run ANOVA
    model <- aov(revenue ~ region, data = sales_data)
    summary(model)
    TukeyHSD(model)

    # Linear regression
    lm_model <- lm(revenue ~ costs + region, data = sales_data)
    summary(lm_model)
    """

    print("\n🔍 Analyzing R code for statistical methods...")
    result = agent.detect_methods_from_code(r_code)

    if 'error' in result:
        print(f"❌ Error: {result['error']}")
        return False

    print(f"✅ Detected {result['total_methods']} methods:\n")

    for i, method in enumerate(result['methods'], 1):
        print(f"{i}. {method['name']} ({method['category']})")
        print(f"   Description: {method['description']}")
        print(f"   📄 Citation: {method['primary_citation'][:100]}...")
        if method['sample_size_note']:
            print(f"   📊 Note: {method['sample_size_note']}")
        print()

    # Test with Python code
    python_code = """
    from scipy import stats
    import pandas as pd

    # K-means clustering
    from sklearn.cluster import KMeans
    kmeans = KMeans(n_clusters=3)
    kmeans.fit(data)

    # Random forest
    from sklearn.ensemble import RandomForestClassifier
    rf = RandomForestClassifier()
    """

    print("🔍 Analyzing Python code for statistical methods...")
    result2 = agent.detect_methods_from_code(python_code)

    print(f"✅ Detected {result2['total_methods']} additional methods:")
    for method in result2['methods']:
        print(f"  - {method['name']}")

    return True


def test_academic_formatting():
    """Test academic writing integration."""
    print("\n" + "="*80)
    print("TEST 3: Academic Writing Integration")
    print("="*80)

    agent = EnhancedNocturnalAgent()

    # Test formatting t-test result
    ttest_result = {
        't': 2.45,
        'df': 48,
        'p': 0.018,
        'mean1': 1850,
        'mean2': 2100,
        'sd1': 300,
        'sd2': 350
    }

    print("\n📝 Formatting t-test result in APA style...")
    result = agent.format_statistical_result(ttest_result, test_type="ttest")

    if 'error' in result:
        print(f"❌ Error: {result['error']}")
        return False

    print(f"✅ Formatted result ({result['style']}):")
    print(f"\n{result['formatted_text']}\n")

    # Test formatting regression result
    regression_result = {
        'R2': 0.547,
        'F': 23.45,
        'df1': 3,
        'df2': 96,
        'p': 0.001,
        'coefficients': [
            {'name': 'costs', 'b': 1.23, 'se': 0.15, 't': 8.20, 'p': 0.001, 'beta': 0.62},
            {'name': 'region_South', 'b': 250, 'se': 85, 't': 2.94, 'p': 0.004, 'beta': 0.22}
        ]
    }

    print("📝 Formatting regression result in APA style...")
    result2 = agent.format_statistical_result(regression_result, test_type="regression")

    print(f"✅ Formatted result:")
    print(f"\n{result2['formatted_text']}\n")

    return True


def test_smart_search():
    """Test smart search across workspace."""
    print("\n" + "="*80)
    print("TEST 4: Smart Search Within Data")
    print("="*80)

    agent = EnhancedNocturnalAgent()

    # Create multiple dataframes in workspace
    globals()['sales_df'] = [
        {'date': '2024-01-01', 'revenue': 1500, 'costs': 800},
        {'date': '2024-01-02', 'revenue': 2200, 'costs': 1100},
    ]

    globals()['customer_df'] = [
        {'customer_id': 1, 'revenue_total': 5000, 'name': 'Alice'},
        {'customer_id': 2, 'revenue_total': 7500, 'name': 'Bob'},
    ]

    python_inspector = agent.workspace_manager.get_inspector("Python")
    if python_inspector:
        python_inspector.set_namespace(globals())

    # Search for columns with "revenue"
    print("\n🔍 Searching for columns containing 'revenue'...")
    result = agent.search_columns('revenue', platform="Python")

    if 'error' in result:
        print(f"❌ Error: {result['error']}")
        return False

    print(f"✅ Found {result['total_matches']} matches:")
    for match in result['results']:
        print(f"  - {match['object']}.{match['column']} ({match['context']})")

    # Find all numeric columns
    print("\n🔍 Finding all numeric columns...")
    result2 = agent.find_numeric_columns(platform="Python")

    print(f"✅ Found numeric columns in {result2['total_objects']} objects:")
    for obj in result2['results']:
        print(f"  - {obj['object']}: {obj['numeric_columns']}")

    return True


def test_code_templates():
    """Test code template generation."""
    print("\n" + "="*80)
    print("TEST 5: Code Template Generation")
    print("="*80)

    agent = EnhancedNocturnalAgent()

    # List available templates
    print("\n📋 Listing available templates...")
    result = agent.list_code_templates(language="R")

    if 'error' in result:
        print(f"❌ Error: {result['error']}")
        return False

    print(f"✅ Found {result['total']} R templates:")
    for template in result['templates'][:5]:  # Show first 5
        print(f"  - {template['name']}: {template['description']}")

    # Get a specific template
    print("\n🔧 Generating t-test template...")
    result2 = agent.get_code_template(
        'ttest_independent_r',
        data='my_data',
        variable='score',
        group_var='treatment',
        group1='control',
        group2='experimental'
    )

    if 'error' in result2:
        print(f"❌ Error: {result2['error']}")
        return False

    print(f"✅ Generated code template:")
    print("\n--- CODE ---")
    print(result2['code'][:500])  # Show first 500 chars
    print("...\n--- END CODE ---\n")

    print("📚 Citations:")
    for citation in result2['citations']:
        print(f"  - {citation[:100]}...")

    if result2['notes']:
        print("\n📝 Notes:")
        for note in result2['notes']:
            print(f"  - {note}")

    return True


def run_all_tests():
    """Run all feature tests."""
    print("\n" + "="*80)
    print("🧪 COMPREHENSIVE FEATURE TEST SUITE")
    print("="*80)

    tests = [
        ("Statistical Summary", test_statistical_summary),
        ("Method Detection", test_method_detection),
        ("Academic Formatting", test_academic_formatting),
        ("Smart Search", test_smart_search),
        ("Code Templates", test_code_templates),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            success = test_func()
            results.append((test_name, success))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' crashed: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))

    # Print summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)

    passed = sum(1 for _, success in results if success)
    total = len(results)

    for test_name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed ({passed/total*100:.0f}%)")

    if passed == total:
        print("\n🎉 ALL TESTS PASSED! 🎉")
        return 0
    else:
        print("\n⚠️  Some tests failed. See details above.")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
