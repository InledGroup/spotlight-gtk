#!/bin/bash
# Local script to build the .deb package

# Copy source files to the package structure
cp spotlight-python/main.py spotlight-python/pkg/usr/share/spotlight-python/
cp spotlight-python/style.css spotlight-python/pkg/usr/share/spotlight-python/

# Build the package
dpkg-deb --build spotlight-python/pkg spotlight-python.deb

echo "Done! spotlight-python.deb created."
