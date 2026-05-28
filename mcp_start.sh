#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# 1. Try Python (Source Method)
if command -v python3 &> /dev/null; then
    echo "[VenEl_SwaMCP] Python detected. Using source/.venv approach..." >&2
    if [ ! -f ".venv/bin/python" ]; then
        echo "[VenEl_SwaMCP] Creating virtual environment..." >&2
        python3 -m venv .venv
        source .venv/bin/activate
        echo "[VenEl_SwaMCP] Installing dependencies..." >&2
        pip install -r requirements.txt
    else
        source .venv/bin/activate
    fi
    echo "[VenEl_SwaMCP] Starting server..." >&2
    python3 -m src.server
    exit $?
fi

# 2. Try Docker (Container Method)
if command -v docker &> /dev/null; then
    echo "[VenEl_SwaMCP] Python not found, but Docker detected. Running via Docker container..." >&2
    docker run -i --rm -v /var/run/docker.sock:/var/run/docker.sock ghcr.io/venkateshellur/venel_swamcp:latest
    exit $?
fi

# 3. Try Standalone Executable (Binary Method)
if [ -f "./VenEl_SwaMCP-macos" ]; then
    echo "[VenEl_SwaMCP] Neither Python nor Docker found. Running macOS standalone executable..." >&2
    ./VenEl_SwaMCP-macos
    exit $?
elif [ -f "./VenEl_SwaMCP-linux" ]; then
    echo "[VenEl_SwaMCP] Neither Python nor Docker found. Running Linux standalone executable..." >&2
    ./VenEl_SwaMCP-linux
    exit $?
fi

# Failure
echo "[VenEl_SwaMCP] ERROR: Could not start. Please install Python3, Docker, or download the standalone executable into this folder." >&2
exit 1
