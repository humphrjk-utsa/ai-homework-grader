# Headless Mac Studio Deployment Instructions

## Overview
This package contains everything needed to run the distributed MLX homework grader across two headless Mac Studios connected via Thunderbolt bridge.

## Network Configuration
- Mac Studio 1: 10.55.0.1:5001 (Qwen Coder)
- Mac Studio 2: 10.55.0.2:5002 (Gemma)

## Deployment Steps

### 1. Copy Files to Mac Studios

**Mac Studio 1:**
```bash
# Copy the mac_studio_1 folder to Mac Studio 1
scp -r mac_studio_1/ user@10.55.0.1:~/homework_grader/
```

**Mac Studio 2:**
```bash
# Copy the mac_studio_2 folder to Mac Studio 2  
scp -r mac_studio_2/ user@10.55.0.2:~/homework_grader/
```

### 2. Setup Mac Studio 1 (SSH)

```bash
# SSH into Mac Studio 1
ssh user@10.55.0.1

# Navigate to project directory
cd ~/homework_grader

# Run installation
./install.sh

# Start the Qwen server
./start_server.sh
```

### 3. Setup Mac Studio 2 (SSH)

```bash
# SSH into Mac Studio 2
ssh user@10.55.0.2

# Navigate to project directory
cd ~/homework_grader

# Run installation
./install.sh

# Start the Gemma server
./start_server.sh
```

### 4. Verify Setup

**Check Mac Studio 1:**
```bash
ssh user@10.55.0.1
cd ~/homework_grader
./check_status.sh
```

**Check Mac Studio 2:**
```bash
ssh user@10.55.0.2
cd ~/homework_grader
./check_status.sh
```

**Test from main machine:**
```bash
# Test Qwen server
curl http://10.55.0.1:5001/health

# Test Gemma server
curl http://10.55.0.2:5002/health
```

### 5. Run Main Application

On your main machine (where you run Streamlit):
```bash
streamlit run app.py
```

The app will automatically detect the distributed system and show "🖥️ Distributed MLX System" in the sidebar.

## Troubleshooting

### Models Not Loading
- Models will download automatically on first use
- Qwen model: ~60GB download
- Gemma model: ~54GB download
- Ensure sufficient disk space and internet connection

### Network Issues
- Verify Thunderbolt bridge is active: `ifconfig bridge100`
- Test connectivity: `ping 10.55.0.1` and `ping 10.55.0.2`
- Check firewall settings on both machines

### Server Issues
- Check logs: Server output will show any errors
- Restart servers: `./start_server.sh`
- Verify Python/MLX installation: `python3 -c "import mlx_lm; print('OK')"`

## Performance Expectations

- **Model Loading**: 30-60 seconds on first startup
- **Generation Speed**: 
  - Qwen (code analysis): ~30-60 seconds
  - Gemma (feedback): ~45-90 seconds
  - Parallel processing: ~60-90 seconds total (vs 120+ sequential)

## Monitoring

Each Mac Studio has a `check_status.sh` script to monitor:
- Server health
- Model loading status
- Response times
- Memory usage

Run these periodically to ensure optimal performance.
