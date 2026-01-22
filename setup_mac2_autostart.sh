#!/bin/bash
# Add Macs Fan Control to Login Items on Mac Studio 2

echo "🌀 Setting up Macs Fan Control auto-start on Mac Studio 2..."
echo ""
echo "This will add Macs Fan Control to Login Items so it starts automatically."
echo ""

# Use osascript to add to Login Items
ssh 10.55.0.2 'osascript -e '"'"'
tell application "System Events"
    make new login item at end with properties {path:"/Applications/Macs Fan Control.app", hidden:false}
end tell
'"'"''

if [ $? -eq 0 ]; then
    echo "✅ Successfully added Macs Fan Control to Login Items on Mac Studio 2"
    echo "✅ It will now start automatically when Mac Studio 2 boots"
    echo ""
    echo "To start it now without rebooting, run:"
    echo "  ssh 10.55.0.2"
    echo "  open -a 'Macs Fan Control'"
else
    echo "❌ Failed to add to Login Items"
    echo ""
    echo "Manual steps:"
    echo "1. On Mac Studio 2, open System Settings"
    echo "2. Go to General → Login Items"
    echo "3. Click + and add /Applications/Macs Fan Control.app"
fi
