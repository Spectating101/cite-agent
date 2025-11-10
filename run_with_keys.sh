#!/bin/bash
# Load .env.local and run command
set -a
source .env.local 2>/dev/null || true
set +a
exec "$@"
