# Ollama Persistence Setup for Mac Ultra M3

## Problem
Your 120B model keeps getting unloaded from memory, causing slow startup times for each grading session.

## Solution
Configure Ollama to keep models loaded longer using the `OLLAMA_KEEP_ALIVE` environment variable.

## Quick Fix (Temporary)

Run this in your terminal before starting the grading system:

```bash
export OLLAMA_KEEP_ALIVE=24h
ollama serve
```

Then in another terminal:
```bash
cd homework_grader
streamlit run app.py
```

## Permanent Fix

### Option 1: Update Shell Configuration
Add this line to your `~/.zshrc` file:

```bash
# Open the file (you may need sudo)
sudo nano ~/.zshrc

# Add this line at the end:
export OLLAMA_KEEP_ALIVE=24h

# Save and reload
source ~/.zshrc
```

### Option 2: Create Ollama Service (Recommended)

Create a launch agent to automatically start Ollama with persistence:

```bash
# Create the plist file
sudo nano ~/Library/LaunchAgents/com.ollama.persistent.plist
```

Add this content:
```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.ollama.persistent</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/ollama</string>
        <string>serve</string>
    </array>
    <key>EnvironmentVariables</key>
    <dict>
        <key>OLLAMA_KEEP_ALIVE</key>
        <string>24h</string>
    </dict>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

Then load it:
```bash
launchctl load ~/Library/LaunchAgents/com.ollama.persistent.plist
```

## Verification

After setup, verify the model stays loaded:

```bash
# Check if model is loaded
curl http://localhost:11434/api/ps

# Should show your gpt-oss:120b model in the response
```

## Alternative Keep-Alive Values

- `OLLAMA_KEEP_ALIVE=24h` - Keep for 24 hours
- `OLLAMA_KEEP_ALIVE=-1` - Keep indefinitely (until manual unload)
- `OLLAMA_KEEP_ALIVE=2h` - Keep for 2 hours (default is usually 5 minutes)

## Benefits for Your Setup

With 512GB RAM on Mac Ultra M3:
- **Memory usage**: 120B model uses ~70GB (only 14% of your RAM)
- **Performance**: Model stays loaded = consistent 15-30 second responses
- **Efficiency**: No 2-3 minute reload times between grading sessions
- **Reliability**: Predictable performance for batch grading

## Troubleshooting

If model still unloads:
1. Check Ollama logs: `ollama logs`
2. Verify environment variable: `echo $OLLAMA_KEEP_ALIVE`
3. Restart Ollama service with new settings
4. Monitor memory usage: `top -o MEM`

Your Mac Ultra M3 with 512GB RAM is perfect for keeping large models loaded permanently!