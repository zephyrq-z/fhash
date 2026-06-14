#!/bin/bash
# Build fhash macOS .app bundle using PyInstaller
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

echo "🔨 Building fhash macOS App..."

# Generate icon if missing
if [ ! -f assets/icon.icns ]; then
    echo "Generating icon..."
    python3 assets/gen_icon.py
fi

# Check PyInstaller
if ! command -v pyinstaller &>/dev/null; then
    echo "Installing PyInstaller..."
    pip3 install pyinstaller
fi

# Clean previous build
rm -rf build dist

# Build .app with icon
pyinstaller \
    --name "fhash" \
    --windowed \
    --onefile \
    --clean \
    --noconfirm \
    --icon assets/icon.icns \
    fhash_gui.py

# Ensure icon is properly placed
if [ -f dist/fhash.app/Contents/Resources/icon.icns ]; then
    cp dist/fhash.app/Contents/Resources/icon.icns dist/fhash.app/Contents/Resources/icon-windowed.icns 2>/dev/null || true
fi

echo ""
echo "✅ Build complete!"
echo "   App: dist/fhash.app"
echo ""
echo "To install to /Applications:"
echo "   cp -r dist/fhash.app /Applications/"
