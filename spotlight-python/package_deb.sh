#!/bin/bash
# Local script to build the .deb package with error handling
set -e

# Determine the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

# Navigate to the directory containing the source files
cd "$SCRIPT_DIR"

echo "Preparing package structure..."

# Ensure target directories exist
mkdir -p pkg/usr/share/spotlight-python
mkdir -p pkg/usr/bin
mkdir -p pkg/usr/share/applications

# Copy source files to the package structure
cp main.py pkg/usr/share/spotlight-python/
cp style.css pkg/usr/share/spotlight-python/
cp tray.py pkg/usr/share/spotlight-python/

# Build the package
echo "Building .deb package..."
dpkg-deb --build pkg ../spotlight-python.deb

echo "------------------------------------------------"
echo "Success! spotlight-python.deb created in the project root."
