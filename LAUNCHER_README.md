# AI Homework Grader - Desktop Launcher

## Quick Start

### Option 1: Use the App Bundle (Recommended)
1. Drag `AI Homework Grader.app` to your Desktop or Applications folder
2. Double-click to launch
3. The app will:
   - Open Terminal with the grader running
   - Automatically open your browser to http://localhost:8505
   - Keep running until you close the Terminal window

### Option 2: Use the Command Line
```bash
cd /Users/humphrjk/GitHub/ai-homework-grader-clean
source .venv/bin/activate
python3 -m streamlit run app.py --server.port 8505
```

### Option 3: Use the Python Script
```bash
cd /Users/humphrjk/GitHub/ai-homework-grader-clean
python3 setup/start.py
```

## Stopping the Application

- Close the Terminal window, or
- Press `Ctrl+C` in the Terminal

## Troubleshooting

**App won't open:**
- Right-click the app and select "Open" (first time only)
- Or go to System Preferences > Security & Privacy and allow it

**Port already in use:**
- Check if another instance is running
- Kill it with: `lsof -ti:8505 | xargs kill -9`

**Virtual environment not found:**
- Make sure you're in the project directory
- Recreate with: `python3 -m venv .venv`
- Install dependencies: `pip install -r requirements.txt`

## System Requirements

- macOS 10.13 or later
- Python 3.8+
- Streamlit installed in virtual environment
- Ollama running (for AI grading)

## Network Configuration

The app runs on:
- **Local:** http://localhost:8505
- **Network:** http://10.176.26.7:8505 (accessible from other devices)

## Multi-Mac Setup

Mac 1 (Current): 10.55.0.1
Mac 2 (Remote): 10.55.0.2 (jamiehumphries@10.55.0.2)

Both connected via Thunderbolt bridge for distributed processing.
