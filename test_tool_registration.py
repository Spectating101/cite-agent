#!/usr/bin/env python3
"""
Comprehensive Tool Registration Verification
Tests that all advanced research tools are properly registered and accessible
"""

import sys
from pathlib import Path

# Add cite_agent to path
sys.path.insert(0, str(Path(__file__).parent))

from cite_agent.function_tools import TOOLS, get_tool_names


def test_tool_registration():
    """Verify all expected advanced tools are registered"""
    
    print("=" * 80)
    print("TOOL REGISTRATION VERIFICATION")
    print("=" * 80)
    print()
    
    # Expected tools by category
    expected_tools = {
        "Core Research": [
            "search_papers",
            "get_financial_data",
            "web_search",
            "find_related_papers",
            "export_to_zotero"
        ],
        "Data Analysis": [
            "load_dataset",
            "analyze_data",
            "run_regression",
            "check_assumptions"
        ],
        "Visualization": [
            "plot_data"
        ],
        "Code Execution": [
            "run_python_code",
            "run_r_code",
            "execute_r_and_capture"
        ],
        "Qualitative Research": [
            "create_code",
            "load_transcript",
            "code_segment",
            "get_coded_excerpts",
            "auto_extract_themes",
            "calculate_kappa"
        ],
        "Data Cleaning": [
            "scan_data_quality",
            "auto_clean_data",
            "handle_missing_values"
        ],
        "Advanced Statistics": [
            "run_pca",
            "run_factor_analysis",
            "run_mediation",
            "run_moderation"
        ],
        "Power Analysis": [
            "calculate_sample_size",
            "calculate_power",
            "calculate_mde"
        ],
        "Literature Synthesis": [
            "add_paper",
            "extract_lit_themes",
            "find_research_gaps",
            "create_synthesis_matrix",
            "find_contradictions"
        ],
        "File System": [
            "list_directory",
            "read_file",
            "write_file",
            "execute_shell_command"
        ],
        "R Integration": [
            "list_r_objects",
            "get_r_dataframe",
            "detect_project"
        ],
        "Chat": [
            "chat"
        ]
    }
    
    # Get all registered tool names
    registered_tools = set(get_tool_names())
    
    print(f"📊 Total registered tools: {len(registered_tools)}")
    print()
    
    # Check each category
    total_expected = 0
    total_found = 0
    missing_tools = []
    
    for category, tools in expected_tools.items():
        print(f"🔍 {category}")
        print("-" * 80)
        
        category_found = 0
        category_missing = []
        
        for tool in tools:
            total_expected += 1
            if tool in registered_tools:
                print(f"  ✅ {tool}")
                total_found += 1
                category_found += 1
            else:
                print(f"  ❌ {tool} - MISSING")
                category_missing.append(tool)
                missing_tools.append(f"{category}::{tool}")
        
        print(f"  Category: {category_found}/{len(tools)} tools found")
        print()
    
    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Total Expected: {total_expected}")
    print(f"Total Found: {total_found}")
    print(f"Missing: {len(missing_tools)}")
    
    if missing_tools:
        print()
        print("❌ MISSING TOOLS:")
        for tool in missing_tools:
            print(f"  - {tool}")
        print()
        return False
    else:
        print()
        print("✅ ALL EXPECTED TOOLS ARE REGISTERED!")
        print()
        
        # Show tool details for advanced features
        print("=" * 80)
        print("ADVANCED TOOL DETAILS")
        print("=" * 80)
        print()
        
        advanced_categories = [
            "Visualization",
            "Qualitative Research", 
            "Advanced Statistics",
            "Power Analysis",
            "Literature Synthesis"
        ]
        
        for category in advanced_categories:
            print(f"📦 {category}")
            print("-" * 80)
            for tool_name in expected_tools[category]:
                tool = next((t for t in TOOLS if t["function"]["name"] == tool_name), None)
                if tool:
                    desc = tool["function"]["description"]
                    # Truncate long descriptions
                    if len(desc) > 100:
                        desc = desc[:100] + "..."
                    print(f"  {tool_name}")
                    print(f"    {desc}")
                    print()
            print()
        
        return True


def test_tool_schema_validity():
    """Verify all tools have valid schemas"""
    
    print("=" * 80)
    print("TOOL SCHEMA VALIDATION")
    print("=" * 80)
    print()
    
    issues = []
    
    for tool in TOOLS:
        tool_name = tool["function"]["name"]
        
        # Check required fields
        if "description" not in tool["function"]:
            issues.append(f"{tool_name}: Missing description")
        
        if "parameters" not in tool["function"]:
            issues.append(f"{tool_name}: Missing parameters")
        else:
            params = tool["function"]["parameters"]
            if "type" not in params:
                issues.append(f"{tool_name}: Parameters missing 'type'")
            if "properties" not in params:
                issues.append(f"{tool_name}: Parameters missing 'properties'")
    
    if issues:
        print("❌ SCHEMA ISSUES FOUND:")
        for issue in issues:
            print(f"  - {issue}")
        print()
        return False
    else:
        print(f"✅ All {len(TOOLS)} tool schemas are valid")
        print()
        return True


def show_tool_statistics():
    """Show statistics about registered tools"""
    
    print("=" * 80)
    print("TOOL STATISTICS")
    print("=" * 80)
    print()
    
    total_tools = len(TOOLS)
    
    # Count parameters
    total_params = 0
    required_params = 0
    optional_params = 0
    
    for tool in TOOLS:
        params = tool["function"]["parameters"]
        if "properties" in params:
            total_params += len(params["properties"])
            if "required" in params:
                required_params += len(params["required"])
                optional_params += len(params["properties"]) - len(params["required"])
            else:
                optional_params += len(params["properties"])
    
    print(f"📊 Total Tools: {total_tools}")
    print(f"📊 Total Parameters: {total_params}")
    print(f"   - Required: {required_params}")
    print(f"   - Optional: {optional_params}")
    print()
    
    # Average parameters per tool
    avg_params = total_params / total_tools if total_tools > 0 else 0
    print(f"📊 Average Parameters per Tool: {avg_params:.1f}")
    print()


if __name__ == "__main__":
    print()
    
    # Run tests
    registration_ok = test_tool_registration()
    print()
    
    schema_ok = test_tool_schema_validity()
    print()
    
    show_tool_statistics()
    print()
    
    # Final verdict
    if registration_ok and schema_ok:
        print("=" * 80)
        print("🎉 ALL VERIFICATIONS PASSED")
        print("=" * 80)
        print()
        print("✅ All advanced research tools are properly registered")
        print("✅ All tool schemas are valid")
        print("✅ cite-agent is ready for comprehensive research assistance")
        print()
        sys.exit(0)
    else:
        print("=" * 80)
        print("⚠️  VERIFICATION FAILED")
        print("=" * 80)
        print()
        sys.exit(1)
