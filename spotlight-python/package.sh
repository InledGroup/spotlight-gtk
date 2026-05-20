#!/bin/bash

# Script to package the Spotlight Python/GTK app using PyInstaller

# Check for PyInstaller
if ! command -v pyinstaller &> /dev/null
then
    echo "PyInstaller could not be found. Installing it..."
    pip install pyinstaller
fi

# Bundle the app
echo "Packaging Spotlight..."
pyinstaller --noconfirm --onefile --windowed \
    --add-data "style.css:." \
    --name "Spotlight" \
    main.py

echo "Done! You can find the executable in the 'dist' folder."
