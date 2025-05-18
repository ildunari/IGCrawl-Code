#!/usr/bin/env bash
# Setup script for IGCrawl - installs backend and frontend dependencies
set -euo pipefail

# Check Python
python_version=$(python3 -c 'import sys; print("{}.{}".format(sys.version_info.major, sys.version_info.minor))')
if [[ $python_version < "3.11" ]]; then
  echo "Python 3.11+ required" >&2
  exit 1
fi

# Install backend requirements
cd backend
pip install -r requirements.txt
cd ..

# Install frontend dependencies
cd frontend
npm install
cd ..

echo "Setup complete."
