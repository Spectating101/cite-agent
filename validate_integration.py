#!/usr/bin/env python3
"""
Quick Validation Script
Validates basic integration without requiring full dependencies
"""

import sys
import ast
from pathlib import Path


def validate_syntax(file_path):
    """Validate Python syntax"""
    try:
        with open(file_path, 'r') as f:
            ast.parse(f.read())
        return True, None
    except SyntaxError as e:
        return False, str(e)


def check_imports(file_path):
    """Check if imports are valid"""
    imports = []
    try:
        with open(file_path, 'r') as f:
            tree = ast.parse(f.read())

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    imports.append(alias.name)
            elif isinstance(node, ast.ImportFrom):
                if node.module:
                    imports.append(node.module)

        return True, imports
    except Exception as e:
        return False, str(e)


def main():
    print("="*60)
    print("Cite-Agent Integration Validation")
    print("="*60 + "\n")

    repo_root = Path(__file__).parent
    files_to_check = [
        "cite_agent/enhanced_ai_agent.py",
        "cite_agent/session_memory_manager.py",
        "cite_agent/timeout_retry_handler.py",
        "cite_agent/prometheus_metrics.py",
        "cite_agent/unified_observability.py",
        "tests/stress_test_concurrent.py",
        "tests/test_end_to_end_integration.py",
    ]

    all_valid = True

    print("1. Checking Python Syntax\n")
    for file_path in files_to_check:
        full_path = repo_root / file_path
        if not full_path.exists():
            print(f"   ❌ {file_path} - FILE NOT FOUND")
            all_valid = False
            continue

        valid, error = validate_syntax(full_path)
        if valid:
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} - {error}")
            all_valid = False

    print("\n2. Checking Enhanced Agent Integration\n")

    # Check that enhanced_ai_agent has the right imports
    agent_file = repo_root / "cite_agent/enhanced_ai_agent.py"
    if agent_file.exists():
        with open(agent_file, 'r') as f:
            content = f.read()

        required_imports = [
            "get_memory_manager",
            "get_retry_handler"
        ]

        for imp in required_imports:
            if imp in content:
                print(f"   ✅ {imp} imported")
            else:
                print(f"   ❌ {imp} NOT imported")
                all_valid = False

        # Check for key method calls
        if "self.memory_manager" in content:
            print(f"   ✅ memory_manager used")
        else:
            print(f"   ❌ memory_manager NOT used")
            all_valid = False

        if "self.retry_handler" in content:
            print(f"   ✅ retry_handler used")
        else:
            print(f"   ❌ retry_handler NOT used")
            all_valid = False

        if "_check_and_archive_if_needed" in content:
            print(f"   ✅ archival check implemented")
        else:
            print(f"   ❌ archival check NOT implemented")
            all_valid = False

    print("\n3. Checking Docker Compose\n")

    docker_compose = repo_root / "docker-compose.yml"
    if docker_compose.exists():
        with open(docker_compose, 'r') as f:
            content = f.read()

        required_services = [
            "postgres",
            "redis",
            "api",
            "prometheus",
            "grafana"
        ]

        for service in required_services:
            if f"{service}:" in content:
                print(f"   ✅ {service} service defined")
            else:
                print(f"   ❌ {service} service MISSING")
                all_valid = False
    else:
        print(f"   ❌ docker-compose.yml NOT FOUND")
        all_valid = False

    print("\n4. Checking Monitoring Configuration\n")

    monitoring_files = [
        "monitoring/prometheus.yml",
        "monitoring/alerts.yml",
        "monitoring/grafana/dashboards/cite-agent-overview.json",
    ]

    for file_path in monitoring_files:
        full_path = repo_root / file_path
        if full_path.exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} NOT FOUND")
            all_valid = False

    print("\n5. Checking Documentation\n")

    doc_files = [
        "DEPLOY.md",
        "WHATS_NEW.md",
        ".env.example",
        "deploy.sh",
    ]

    for file_path in doc_files:
        full_path = repo_root / file_path
        if full_path.exists():
            print(f"   ✅ {file_path}")
        else:
            print(f"   ❌ {file_path} NOT FOUND")
            all_valid = False

    # Check deploy.sh is executable
    deploy_script = repo_root / "deploy.sh"
    if deploy_script.exists():
        import os
        if os.access(deploy_script, os.X_OK):
            print(f"   ✅ deploy.sh is executable")
        else:
            print(f"   ⚠️  deploy.sh NOT executable (run: chmod +x deploy.sh)")

    print("\n" + "="*60)
    if all_valid:
        print("✅ All Validation Checks PASSED")
        print("="*60 + "\n")
        print("Next steps:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Run tests: pytest tests/test_end_to_end_integration.py -v")
        print("3. Deploy: ./deploy.sh")
        return 0
    else:
        print("❌ Some Validation Checks FAILED")
        print("="*60 + "\n")
        print("Please fix the issues above before deploying.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
