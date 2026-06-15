#!/bin/bash
# fhash-decode-runner.sh — Called by Finder Quick Action
# Restores hashed folder names in the selected directory

FHASH="$HOME/bin/fhash"
if [ ! -f "$FHASH" ]; then
    FHASH="$HOME/Developer/tools-set/fhash/fhash.py"
fi

if [ $# -eq 0 ]; then
    osascript -e 'display notification "Please select a folder first" with title "fhash Decode" sound name "Basso"'
    exit 1
fi

if [ ! -f "$FHASH" ]; then
    osascript -e 'display notification "fhash not installed. Run: bash install.sh" with title "fhash Decode" sound name "Basso"'
    exit 1
fi

ERRORS=0
SUCCESS=0

for f in "$@"; do
    if [ -d "$f" ]; then
        OUTPUT=$(python3 "$FHASH" decode "$f" --files --yes 2>&1)
        if [ $? -eq 0 ]; then
            LAST_LINE=$(echo "$OUTPUT" | tail -1)
            SUCCESS=$((SUCCESS + 1))
        else
            ERRORS=$((ERRORS + 1))
        fi
    fi
done

if [ $ERRORS -eq 0 ] && [ $SUCCESS -gt 0 ]; then
    osascript -e "display notification \"$LAST_LINE\" with title \"fhash Decode\" sound name \"Glass\""
elif [ $ERRORS -gt 0 ]; then
    osascript -e "display notification \"$ERRORS folder(s) failed\" with title \"fhash Decode\" sound name \"Basso\""
else
    osascript -e 'display notification "No valid folders to decode" with title "fhash Decode" sound name "Basso"'
fi
