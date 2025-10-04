# 🖥️ Headless Mac Studio Deployment Guide

## Quick Setup for Your Thunderbolt-Connected Mac Studios

### 📦 What's Ready
Your deployment package is in `mac_studio_deployment/` with everything needed for both machines.

### 🚀 Step-by-Step Deployment

#### 1. Copy Files to Mac Studio 1 (10.55.0.1)
```bash
# Copy the entire mac_studio_1 folder to Mac Studio 1
scp -r mac_studio_deployment/mac_studio_1/ user@10.55.0.1:~/homework_grader/

# Or if using rsync:
rsync -av mac_studio_deployment/mac_studio_1/ user@10.55.0.1:~/homework_grader/
```

#### 2. Copy Files to Mac Studio 2 (10.55.0.2)
```bash
# Copy the entire mac_studio_2 folder to Mac Studio 2
scp -r mac_studio_deployment/mac_studio_2/ user@10.55.0.2:~/homework_grader/

# Or if using rsync:
rsync -av mac_studio_deployment/mac_studio_2/ user@10.55.0.2:~/homework_grader/
```

#### 3. Setup Mac Studio 1 (SSH)
```bash
# SSH into Mac Studio 1
ssh user@10.55.0.1

# Navigate and setup
cd ~/homework_grader
chmod +x *.sh
./install.sh

# Start the Qwen Coder server (runs in foreground)
./start_server.sh
```

#### 4. Setup Mac Studio 2 (SSH in new terminal)
```bash
# SSH into Mac Studio 2
ssh user@10.55.0.2

# Navigate and setup
cd ~/homework_grader
chmod +x *.sh
./install.sh

# Start the Gemma server (runs in foreground)
./start_server.sh
```

#### 5. Verify Both Servers
```bash
# Test from your main machine
curl http://10.55.0.1:5001/health
curl http://10.55.0.2:5002/health

# Should return JSON with status: "healthy"
```

#### 6. Run Your Main App
```bash
# On your main machine where you have the full project
streamlit run app.py
```

### 🔧 What Each Script Does

**install.sh**: 
- Installs Python dependencies (mlx-lm, flask, etc.)
- Checks for and loads the MLX models
- Sets up the environment

**start_server.sh**:
- Starts the model server (Qwen on Mac 1, Gemma on Mac 2)
- Runs on ports 5001 and 5002 respectively
- Shows logs in real-time

**check_status.sh**:
- Checks if the server is running
- Shows model status and performance info
- Useful for monitoring

### 📊 Expected Behavior

1. **First Run**: Models will download automatically (~60GB each)
2. **Startup Time**: 30-60 seconds to load models into memory
3. **Performance**: True parallel processing across both machines
4. **Monitoring**: Check status anytime with `./check_status.sh`

### 🔍 Troubleshooting

**If servers won't start:**
```bash
# Check Python and MLX
python3 -c "import mlx_lm; print('MLX OK')"

# Check network connectivity
ping 10.55.0.1
ping 10.55.0.2
```

**If models won't load:**
- Ensure sufficient disk space (120GB+ free)
- Check internet connection for model downloads
- Models cache in `~/.cache/huggingface/hub/`

### 🎯 Success Indicators

✅ Both servers respond to health checks  
✅ Streamlit app shows "🖥️ Distributed MLX System"  
✅ Sidebar shows "✅ Mac Studio 1: Qwen Coder" and "✅ Mac Studio 2: Gemma"  
✅ Grading uses parallel processing across both machines  

### 💡 Pro Tips

- Keep SSH sessions open to monitor server logs
- Use `screen` or `tmux` to run servers in background
- Monitor with `./check_status.sh` periodically
- Restart servers if performance degrades

Your distributed system will give you true parallel AI processing with ~2x performance improvement over single-machine operation!