#!/bin/bash
# Setup Macs Fan Control to auto-start on Mac Studio 2

echo "🌀 Setting up Macs Fan Control auto-start on Mac Studio 2..."

# Create LaunchAgent plist on Mac Studio 2
ssh 10.55.0.2 'cat > ~/Library/LaunchAgents/com.crystalidea.macsfancontrol.plist << EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.crystalidea.macsfancontrol</string>
    <key>ProgramArguments</key>
    <array>
        <string>/Applications/Macs Fan Control.app/Contents/MacOS/Macs Fan Control</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <false/>
</dict>
</plist>
EOF'

# Load the LaunchAgent
ssh 10.55.0.2 'launchctl load ~/Library/LaunchAgents/com.crystalidea.macsfancontrol.plist'

# Start it now
ssh 10.55.0.2 'launchctl start com.crystalidea.macsfancontrol'

echo "✅ Macs Fan Control will now auto-start on Mac Studio 2"
echo "✅ Started Macs Fan Control on Mac Studio 2"
