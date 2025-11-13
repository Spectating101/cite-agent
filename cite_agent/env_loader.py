#!/usr/bin/env python3
"""
Environment loader for integration credentials
Loads credentials from ~/.cite-agent.env automatically
"""

import os
from pathlib import Path
from typing import Dict


def load_integration_env():
    """
    Load integration credentials from ~/.cite-agent.env

    This is called automatically when integration clients are imported.
    Users don't need to manually set environment variables.
    """
    env_file = Path.home() / ".cite-agent.env"

    if not env_file.exists():
        return  # No env file, will use system environment variables

    try:
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()

                # Skip comments and empty lines
                if not line or line.startswith('#'):
                    continue

                # Parse KEY=VALUE
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()

                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]

                    # Only set if not already in environment
                    if key not in os.environ:
                        os.environ[key] = value

    except Exception as e:
        # Silently fail - don't break if env file is malformed
        pass


# Auto-load on import
load_integration_env()
