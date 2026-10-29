#!/usr/bin/env bash
# ==============================================================================
# TruVex AI - Unix/macOS One-Click Launcher
# ==============================================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "============================================================"
echo "  Starting TruVex AI Unified Platform..."
echo "============================================================"

if [ -f ".venv/bin/python" ]; then
    exec .venv/bin/python run.py "$@"
elif [ -f "venv/bin/python" ]; then
    exec venv/bin/python run.py "$@"
else
    exec python3 run.py "$@"
fi
