# Starting the Distributed Grading System

## Quick Start Commands

### 1. Start GPT-OSS Server on Mac Studio 1 (Current Machine)
```bash
# From the ai-homework-grader-clean directory
nohup python3 gpt_oss_server_working.py > gpt_oss_server.log 2>&1 &
```

### 2. Start Qwen Server on Mac Studio 2
```bash
# SSH into Mac Studio 2 and start the server
ssh jamiehumphries@10.55.0.2 "cd ~ && nohup python3 qwen_8bit_server.py > qwen_server.log 2>&1 &"
```

### 3. Verify Both Servers Are Running
```bash
# Check Mac Studio 1 (GPT-OSS)
curl http://10.55.0.1:5001/health

# Check Mac Studio 2 (Qwen)
curl http://10.55.0.2:5002/health
```

Expected output:
```json
{"loaded":true,"model":"lmstudio-community/gpt-oss-120b-MLX-8bit","status":"healthy"}
{"loaded":true,"model":"mlx-community/Qwen3-Coder-30B-A3B-Instruct-bf16","status":"healthy"}
```

### 4. Start the Grading App
```bash
# From the ai-homework-grader-clean directory
streamlit run app.py
```

### 5. Monitor System Status (Optional)
```bash
# Terminal-based monitor
python monitor_dashboard.py

# Or web-based monitor
streamlit run monitor_app.py
```

---

## Stopping the Servers

### Stop GPT-OSS Server (Mac Studio 1)
```bash
pkill -f gpt_oss_server_working
```

### Stop Qwen Server (Mac Studio 2)
```bash
ssh jamiehumphries@10.55.0.2 "pkill -f qwen_8bit_server"
```

---

## Troubleshooting

### Check Server Logs

**Mac Studio 1 (GPT-OSS):**
```bash
tail -f gpt_oss_server.log
```

**Mac Studio 2 (Qwen):**
```bash
ssh jamiehumphries@10.55.0.2 "tail -f ~/qwen_server.log"
```

### Check Memory Usage

**Mac Studio 2:**
```bash
ssh jamiehumphries@10.55.0.2 "top -l 1 | head -10"
```

### Kill Duplicate Processes

If you see high memory usage, check for duplicate Python processes:
```bash
# On Mac Studio 2
ssh jamiehumphries@10.55.0.2 "ps aux | grep python | grep -v grep"

# Kill specific process by PID
ssh jamiehumphries@10.55.0.2 "kill <PID>"
```

### Restart Everything

```bash
# Stop all servers
pkill -f gpt_oss_server_working
ssh jamiehumphries@10.55.0.2 "pkill -f qwen_8bit_server"
ssh jamiehumphries@10.55.0.2 "pkill -f mlx_lm.server"

# Wait a few seconds
sleep 5

# Start servers again (see Quick Start above)
```

---

## System Configuration

### Mac Studio 1 (10.55.0.1:5001)
- **Model**: GPT-OSS-120B-8bit
- **Purpose**: Feedback generation
- **RAM Usage**: ~121GB
- **Server**: gpt_oss_server_working.py

### Mac Studio 2 (10.55.0.2:5002)
- **Model**: Qwen3-Coder-30B-A3B-Instruct-bf16
- **Purpose**: Code analysis
- **RAM Usage**: ~65-70GB
- **Server**: qwen_8bit_server.py (despite the name, it loads bf16)

### Expected Performance
- **Grading Time**: ~45 seconds per assignment
- **Parallel Processing**: Both models run simultaneously
- **Network**: Connected via Thunderbolt bridge (10.55.0.x)

---

## One-Line Startup Script

Create a startup script for convenience:

```bash
# Create start_all.sh
cat > start_all.sh << 'EOF'
#!/bin/bash
echo "🚀 Starting distributed grading system..."

# Start GPT-OSS on Mac Studio 1
echo "📡 Starting GPT-OSS server on Mac Studio 1..."
nohup python3 gpt_oss_server_working.py > gpt_oss_server.log 2>&1 &

# Start Qwen on Mac Studio 2
echo "📡 Starting Qwen server on Mac Studio 2..."
ssh jamiehumphries@10.55.0.2 "cd ~ && nohup python3 qwen_8bit_server.py > qwen_server.log 2>&1 &"

# Wait for servers to start
echo "⏳ Waiting for servers to load (30 seconds)..."
sleep 30

# Check status
echo "🔍 Checking server status..."
echo "Mac Studio 1 (GPT-OSS):"
curl -s http://10.55.0.1:5001/health | python3 -m json.tool

echo ""
echo "Mac Studio 2 (Qwen):"
curl -s http://10.55.0.2:5002/health | python3 -m json.tool

echo ""
echo "✅ System ready! Start the app with: streamlit run app.py"
EOF

chmod +x start_all.sh
```

Then just run:
```bash
./start_all.sh
```
