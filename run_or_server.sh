#!/bin/bash

# run_app.sh

VENV=".venv_or"
REQUIREMENTS="requirements_or.txt"

# Check for Python 3
if ! command -v python3 &> /dev/null
then
    echo "python3 could not be found. Please install Python 3."
    exit 1
fi

# Create virtual environment if not exists
if [ ! -d "$VENV" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$VENV"
    if [ $? -ne 0 ]; then
        echo "Failed to create virtual environment."
        exit 1
    fi
fi

# Activate virtual environment
ACTIVATE="$VENV/bin/activate"
if [ -f "$ACTIVATE" ]; then
    echo "Activating virtual environment..."
    source "$ACTIVATE"
else
    echo "Activation script not found in $VENV. Virtual environment may be corrupted."
    exit 1
fi

# Install dependencies
if [ -f "$REQUIREMENTS" ]; then
    echo "Installing dependencies from $REQUIREMENTS..."
    pip install -r "$REQUIREMENTS"
    if [ $? -ne 0 ]; then
        echo "Failed to install dependencies from $REQUIREMENTS."
        exit 1
    fi
else
    echo "Requirements file not found: $REQUIREMENTS"
    exit 1
fi

# Run the application
echo "Starting application: python -m backend.dev_flask_opt.main"
python -m backend.dev_flask_opt.main