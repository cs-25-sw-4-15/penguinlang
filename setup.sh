#!/bin/sh
set -e #exit on fail

# Checking (and installing) Python 3.11
uv venv --python 3.11

# Installing dependencies
uv pip install -r pyproject.toml

echo "Setup complete. To activate the environment, run:"
echo "  source .venv/bin/activate  (on macOS/Linux)"
echo "  .venv\\Scripts\\activate    (on Windows)"