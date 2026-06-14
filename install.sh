#!/bin/bash
# fhash installer — symlink to /usr/local/bin for global access
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TARGET="/usr/local/bin/fhash"

if [ -L "$TARGET" ] || [ -f "$TARGET" ]; then
    echo "⚠️  $TARGET already exists. Removing..."
    rm -f "$TARGET"
fi

ln -s "$SCRIPT_DIR/fhash.py" "$TARGET"
chmod +x "$SCRIPT_DIR/fhash.py"
echo "✅ fhash installed → $TARGET"
echo "   Try: fhash --help"
