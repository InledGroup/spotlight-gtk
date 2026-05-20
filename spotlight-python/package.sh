#!/bin/bash

# Improved Script to package the Spotlight Python/GTK app using a Virtual Environment

# 1. Create a virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# 2. Activate venv and install dependencies
echo "Installing dependencies in virtual environment..."
./venv/bin/pip install --upgrade pip
./venv/bin/pip install pyinstaller PyGObject

# 3. Bundle the app
echo "Packaging Spotlight..."
./venv/bin/pyinstaller --noconfirm --onefile --windowed \
    --add-data "style.css:." \
    --name "Spotlight" \
    main.py

echo "------------------------------------------------"
echo "Done! You can find the executable in the 'dist' folder."
echo "Note: To run the executable, you might need 'libadwaita-1-0' and 'python3-gi' installed on the target system."
