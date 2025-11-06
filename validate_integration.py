#!/usr/bin/env python3
"""
Integration Validation Script
Validates the Cite-Agent infrastructure without requiring dependencies
"""

import os
import sys
import json
import yaml
import ast
from pathlib import Path
from typing import List, Tuple, Dict

class ValidationResult:
    def __init__(self, name: str):
        self.name = name
        self.checks: List[Tuple[str, bool, str]] = []
    
    def add_check(self, check_name: str, passed: bool, message: str = ""):
        self.checks.append((check_name, passed, message))
    
    def all_passed(self) -> bool:
        return all(passed for _, passed, _ in self.checks)
    
    def print_results(self):
        print(f"\n{'='*70}")
        print(f"📋 {self.name}")
        print(f"{'='*70}")
        for check_name, passed, message in self.checks:
            symbol = "✅" if passed else "❌"
            print(f"{symbol} {check_name}")
            if message:
                print(f"   └─ {message}")


def validate_python_files() -> ValidationResult:
    """Validate all Python files for syntax errors"""
    result = ValidationResult("Python Syntax Validation")
    
    python_files = list(Path(".").rglob("*.py"))
    # Exclude __pycache__ and venv
    python_files = [f for f in python_files if "__pycache__" not in str(f) and "venv" not in str(f)]
    
    total_files = len(python_files)
    valid_files = 0
    
    for py_file in python_files:
        try:
            with open(py_file, 'r') as f:
                ast.parse(f.read())
            valid_files += 1
        except SyntaxError as e:
            result.add_check(f"Parse {py_file}", False, f"Syntax error: {e}")
    
    result.add_check(
        f"Python Files ({valid_files}/{total_files})",
        valid_files == total_files,
        f"All {total_files} Python files valid"
    )
    
    return result


def validate_yaml_files() -> ValidationResult:
    """Validate YAML configuration files"""
    result = ValidationResult("YAML Configuration Validation")
    
    yaml_files = [
        Path("docker-compose.yml"),
        Path("cite-agent-api/docker-compose.yml"),
        Path("cite-agent-api/prometheus.yml"),
        Path("cite-agent-api/alerting_rules.yml"),
    ]
    
    for yaml_file in yaml_files:
        if yaml_file.exists():
            try:
                with open(yaml_file, 'r') as f:
                    yaml.safe_load(f)
                result.add_check(f"YAML: {yaml_file.name}", True, "Valid YAML structure")
            except yaml.YAMLError as e:
                result.add_check(f"YAML: {yaml_file.name}", False, f"YAML error: {e}")
        else:
            result.add_check(f"YAML: {yaml_file.name}", False, "File not found")
    
    return result


def validate_json_files() -> ValidationResult:
    """Validate JSON configuration files"""
    result = ValidationResult("JSON Configuration Validation")
    
    json_files = [
        Path("cite-agent-api/grafana_dashboard.json"),
        Path("sample_data.json") if Path("sample_data.json").exists() else None,
    ]
    
    json_files = [f for f in json_files if f is not None]
    
    for json_file in json_files:
        if json_file.exists():
            try:
                with open(json_file, 'r') as f:
                    json.load(f)
                result.add_check(f"JSON: {json_file.name}", True, "Valid JSON structure")
            except json.JSONDecodeError as e:
                result.add_check(f"JSON: {json_file.name}", False, f"JSON error: {e}")
        else:
            result.add_check(f"JSON: {json_file.name}", False, "File not found")
    
    return result


def validate_project_structure() -> ValidationResult:
    """Validate required project files and directories"""
    result = ValidationResult("Project Structure Validation")
    
    required_files = [
        ("setup.py", "Setup configuration"),
        ("requirements.txt", "Dependencies"),
        ("README.md", "Documentation"),
        ("pytest.ini", "Test configuration"),
    ]
    
    required_dirs = [
        ("cite_agent", "Main package"),
        ("tests", "Test suite"),
        ("cite-agent-api", "API backend"),
        ("docs", "Documentation"),
    ]
    
    for file_name, description in required_files:
        exists = Path(file_name).exists()
        result.add_check(f"File: {file_name}", exists, description)
    
    for dir_name, description in required_dirs:
        exists = Path(dir_name).is_dir()
        result.add_check(f"Dir: {dir_name}", exists, description)
    
    return result


def validate_integration_points() -> ValidationResult:
    """Validate key integration points in code"""
    result = ValidationResult("Integration Points Validation")
    
    # Check main agent file
    agent_file = Path("cite_agent/enhanced_ai_agent.py")
    if agent_file.exists():
        with open(agent_file, 'r') as f:
            content = f.read()
        
        checks = [
            ("CircuitBreaker import", "from .circuit_breaker import CircuitBreaker" in content),
            ("MemoryManager usage", "MemoryManager" in content),
            ("RetryHandler usage", "RetryHandler" in content),
            ("Error handling", "except" in content),
        ]
        
        for check_name, passed in checks:
            result.add_check(f"Agent: {check_name}", passed)
    
    # Check API integration
    api_file = Path("cite-agent-api/main.py")
    if api_file.exists():
        with open(api_file, 'r') as f:
            content = f.read()
        
        checks = [
            ("FastAPI setup", "FastAPI" in content),
            ("Route handlers", "@app" in content),
            ("Health check", "/health" in content),
            ("CORS enabled", "CORS" in content or "cors" in content.lower()),
        ]
        
        for check_name, passed in checks:
            result.add_check(f"API: {check_name}", passed)
    
    return result


def validate_test_coverage() -> ValidationResult:
    """Validate test file presence and coverage"""
    result = ValidationResult("Test Coverage Validation")
    
    test_files = list(Path("tests").rglob("test_*.py"))
    test_count = len(test_files)
    
    required_test_areas = [
        "cli", "agent", "integration", "end_to_end", "enhanced"
    ]
    
    found_areas = set()
    for test_file in test_files:
        for area in required_test_areas:
            if area in test_file.name.lower():
                found_areas.add(area)
    
    result.add_check(
        f"Test Files ({test_count} found)",
        test_count > 0,
        f"Found {test_count} test files"
    )
    
    result.add_check(
        f"Test Coverage ({len(found_areas)}/{len(required_test_areas)})",
        len(found_areas) == len(required_test_areas),
        f"Coverage: {', '.join(found_areas)}"
    )
    
    return result


def validate_documentation() -> ValidationResult:
    """Validate documentation completeness"""
    result = ValidationResult("Documentation Validation")
    
    docs = [
        ("README.md", "Main README"),
        ("ARCHITECTURE.md", "Architecture guide"),
        ("INSTALLATION.md", "Installation guide"),
        ("GETTING_STARTED.md", "Getting started guide"),
    ]
    
    found_count = 0
    for doc_file, description in docs:
        exists = Path(doc_file).exists()
        if exists:
            found_count += 1
        result.add_check(f"Doc: {doc_file}", exists, description)
    
    return result


def validate_dependencies() -> ValidationResult:
    """Validate requirements files"""
    result = ValidationResult("Dependencies Validation")
    
    req_files = [
        ("requirements.txt", "Main requirements"),
        ("cite_agent/requirements.txt", "Agent requirements"),
    ]
    
    for req_file, description in req_files:
        if Path(req_file).exists():
            with open(req_file, 'r') as f:
                lines = f.readlines()
            
            package_count = len([l for l in lines if l.strip() and not l.startswith("#")])
            result.add_check(
                f"Requirements: {req_file}",
                package_count > 0,
                f"{package_count} packages specified"
            )
        else:
            result.add_check(f"Requirements: {req_file}", False, "File not found")
    
    return result


def validate_docker_setup() -> ValidationResult:
    """Validate Docker configuration"""
    result = ValidationResult("Docker Configuration Validation")
    
    docker_files = [
        ("Dockerfile", "Main Dockerfile"),
        ("cite-agent-api/Dockerfile", "API Dockerfile"),
        ("docker-compose.yml", "Docker Compose"),
    ]
    
    for docker_file, description in docker_files:
        exists = Path(docker_file).exists()
        result.add_check(f"Docker: {docker_file}", exists, description)
    
    return result


def main():
    print("\n" + "="*70)
    print("🚀 CITE-AGENT INTEGRATION VALIDATION")
    print("="*70)
    print(f"🔍 Working directory: {os.getcwd()}")
    print(f"📦 Python version: {sys.version.split()[0]}")
    print("="*70)
    
    # Run all validations
    validations = [
        validate_project_structure(),
        validate_python_files(),
        validate_yaml_files(),
        validate_json_files(),
        validate_dependencies(),
        validate_docker_setup(),
        validate_integration_points(),
        validate_test_coverage(),
        validate_documentation(),
    ]
    
    # Print results
    for validation in validations:
        validation.print_results()
    
    # Summary
    all_passed = all(v.all_passed() for v in validations)
    total_checks = sum(len(v.checks) for v in validations)
    passed_checks = sum(sum(1 for _, p, _ in v.checks if p) for v in validations)
    
    print(f"\n{'='*70}")
    print(f"📊 VALIDATION SUMMARY")
    print(f"{'='*70}")
    print(f"Total Checks: {passed_checks}/{total_checks}")
    
    if all_passed:
        print("\n✅ ALL VALIDATION CHECKS PASSED\n")
        print("Your infrastructure is structurally sound!")
        print("\nNext steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run tests: pytest tests/ -v")
        print("3. Deploy: ./deploy.sh (if available)")
        print(f"\n{'='*70}\n")
        return 0
    else:
        print("\n❌ SOME VALIDATION CHECKS FAILED\n")
        print("Please review the failures above.")
        print(f"\n{'='*70}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
