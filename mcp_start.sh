#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if .venv exists
if [ ! -f ".venv/bin/python" ]; then
    echo "[VenEl_SwaMCP] Creating virtual environment..." >&2
    python3 -m venv .venv
    if [ $? -ne 0 ]; then
        echo "[VenEl_SwaMCP] Failed to create virtual environment. Make sure python3 is installed." >&2
        exit 1
    fi
    
    echo "[VenEl_SwaMCP] Installing dependencies..." >&2
    source .venv/bin/activate
    pip install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "[VenEl_SwaMCP] Failed to install dependencies." >&2
        exit 1
    fi
else
    source .venv/bin/activate
fi

# Run the server
echo "[VenEl_SwaMCP] Starting server..." >&2
python -m src.server
