#!/bin/bash
# Eco Data Reader Launcher Script
# This script runs the application using a portable Python installation

# Check if portable Python exists
if [ -f "python/bin/python3" ]; then
    echo "Using portable Python installation..."
    PYTHON_EXE="python/bin/python3"
elif command -v python3 &> /dev/null; then
    echo "Using system Python installation..."
    PYTHON_EXE="python3"
elif command -v python &> /dev/null; then
    echo "Using system Python installation..."
    PYTHON_EXE="python"
else
    echo "ERROR: Python not found!"
    echo ""
    echo "Please either:"
    echo "  1. Install Python 3 and add it to your PATH, OR"
    echo "  2. Extract a portable Python to the 'python' folder in this directory"
    echo ""
    exit 1
fi

# Check if config.ini exists
if [ ! -f "config.ini" ]; then
    echo "ERROR: config.ini not found!"
    echo ""
    echo "Please create a config.ini file and set the ECO_SERVER_PATH."
    echo "See README for more information."
    echo ""
    exit 1
fi

# Run the application
echo "Running Eco Data Reader..."
echo ""
"$PYTHON_EXE" main.py
echo ""
echo "Application finished."
