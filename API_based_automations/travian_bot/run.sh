#!/bin/bash

set -e

# Activate virtual environment
source venv/bin/activate

# Check if identity is already set up (replace this with your actual check file or logic)
IDENTITY_FILE="database/identity.json"

# --rescan forces re-run of map scanner
if [[ "$1" == "--rescan" ]]; then
    echo "Rescanning map..."
    python map_scanning_main.py
    exit 0
fi

# If identity file doesn't exist, it's a first-time setup
if [[ ! -f "$IDENTITY_FILE" ]]; then
    echo "First-time setup detected. Running map scanning..."
    python map_scanning_main.py
fi

# Default behavior: launch the bot
echo "Launching main bot..."
python launcher.py
