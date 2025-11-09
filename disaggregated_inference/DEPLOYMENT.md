# Deployment Checklist

## Pre-Deployment

### 1. Verify Network Configuration
```bash
# Check static IPs are configured
# DGX Spark 1: 192.168.100.1 (ConnectX-7)
# DGX Spark 2: 192.168.100.2 (ConnectX-7)
# Mac Studio 1: 169.254.150.101 (Thunderbolt)
# Mac Studio 2: 169.254.150.102 (Thunderbolt)

# Test connectivity
ping -c 3 192.168.100.1
ping -c 3 192.168.100.2
ping -c 3 169.254.150.101
ping -c 3 169.254.150.102
```

### 2. Verify Models are Distributed
```bash
# Check DGX Spark 1
ssh humphrjk@169.254.150.103 'ls -lh ~/models/fp4/qwen3-coder-30b-fp4/'

# Check DGX Spark 2
ssh humphrjk@169.254.150.104 'ls -lh ~/models/fp4/gpt-oss-120b-fp4/'

# Check Mac Studio 1 (local)
ls -lh ~/models/fp4/qwen3-coder-30b-fp4/

# Check Mac Studio 2
ssh humphrjk@169.254.150.102 'ls -lh ~/models/fp4/gpt-oss-120b-fp4/'
```

### 3. Copy Server Files to All Machines
```bash
# Copy to DGX Spark 1
scp disaggregated_inference/prefill_server_dgx.py humphrjk@169.254.150.103:~/disaggregated_inference/

# Copy to DGX Spark 2
scp disaggregated_inference/prefill_server_dgx.py humphrjk@169.254.150.104:~/disaggregated_inference/

# Copy to Mac Studio 2
scp disaggregated_inference/decode_server_mac.py humphrjk@169.254.150.102:~/disaggregated_inference/
```

### 4. Install Dependencies

**On DGX Sparks:**
```bash
ssh humphrjk@169.254.150.103
pip install flask torch transformers accelerate

ssh humphrjk@169.254.150.104
pip install flask torch transformers accelerate
```

**On Mac Studios:**
```bash
# Mac Studio 1 (local)
pip install flask mlx mlx-lm

# Mac Studio 2
ssh humphrjk@169.254.150.102
pip install flask mlx mlx-lm
```

## Deployment Steps

### Step 1: Start DGX Prefill Servers
```bash
./disaggregated_inference/start_dgx_servers.sh
```

**Expected Output:**
```
🚀 Starting DGX Prefill Servers
================================

📡 Starting DGX Spark 1 (Qwen 3 Coder)...
Qwen prefill server started on 192.168.100.1:8000

📡 Starting DGX Spark 2 (GPT-OSS)...
GPT-OSS prefill server started on 192.168.100.2:8000

⏳ Waiting for servers to start...

🔍 Checking server status...
DGX Spark 1 (Qwen):
{
  "status": "healthy",
  "loaded": true,
  ...
}

DGX Spark 2 (GPT-OSS):
{
  "status": "healthy",
  "loaded": true,
  ...
}

✅ DGX prefill servers started!
```

### Step 2: Start Mac Decode Servers
```bash
./disaggregated_inference/start_mac_servers.sh
```

**Expected Output:**
```
🚀 Starting Mac Decode Servers
===============================

📡 Starting Mac Studio 1 (Qwen 3 Coder)...
Qwen decode server started on 169.254.150.101:8001

📡 Starting Mac Studio 2 (GPT-OSS)...
GPT-OSS decode server started on 169.254.150.102:8001

⏳ Waiting for servers to start...

🔍 Checking server status...
Mac Studio 1 (Qwen):
{
  "status": "healthy",
  "loaded": true,
  ...
}

Mac Studio 2 (GPT-OSS):
{
  "status": "healthy",
  "loaded": true,
  ...
}

✅ Mac decode servers started!
```

### Step 3: Verify System Health
```bash
python3 disaggregated_inference/check_status.py
```

### Step 4: Run Tests
```bash
python3 disaggregated_inference/test_system.py
```

## Post-Deployment

### Monitor Performance
```bash
# Watch logs in real-time
./disaggregated_inference/monitor_logs.sh
```

### Run Benchmarks
```bash
# Compare disaggregated vs Mac-only
python3 benchmarks/compare_disaggregated.py
```

## Troubleshooting

### Issue: Server not responding

**Check if process is running:**
```bash
# DGX
ssh humphrjk@169.254.150.103 'ps aux | grep prefill_server'

# Mac
ps aux | grep decode_server
```

**Check logs:**
```bash
# DGX
ssh humphrjk@169.254.150.103 'tail -50 ~/logs/prefill_qwen.log'

# Mac
tail -50 ~/logs/decode_qwen.log
```

**Restart server:**
```bash
./disaggregated_inference/stop_all_servers.sh
./disaggregated_inference/start_dgx_servers.sh
./disaggregated_inference/start_mac_servers.sh
```

### Issue: Model loading fails

**Check model path:**
```bash
ssh humphrjk@169.254.150.103 'ls -la ~/models/fp4/qwen3-coder-30b-fp4/'
```

**Check CUDA/MLX:**
```bash
# DGX - Check CUDA
ssh humphrjk@169.254.150.103 'nvidia-smi'

# Mac - Check MLX
python3 -c "import mlx.core as mx; print(mx.metal.is_available())"
```

### Issue: Network connectivity

**Test ports:**
```bash
nc -zv 192.168.100.1 8000
nc -zv 169.254.150.101 8001
```

**Check firewall:**
```bash
# DGX
ssh humphrjk@169.254.150.103 'sudo ufw status'

# Mac
sudo /usr/libexec/ApplicationFirewall/socketfilterfw --getglobalstate
```

### Issue: Slow performance

**Check GPU utilization:**
```bash
# DGX
ssh humphrjk@169.254.150.103 'nvidia-smi dmon -s u'
```

**Check network bandwidth:**
```bash
# Test ConnectX-7 speed
ssh humphrjk@169.254.150.103 'iperf3 -s' &
iperf3 -c 192.168.100.1
```

## Maintenance

### Update Server Code
```bash
# Stop servers
./disaggregated_inference/stop_all_servers.sh

# Update code
git pull

# Copy to remote machines
scp disaggregated_inference/prefill_server_dgx.py humphrjk@169.254.150.103:~/disaggregated_inference/
scp disaggregated_inference/prefill_server_dgx.py humphrjk@169.254.150.104:~/disaggregated_inference/
scp disaggregated_inference/decode_server_mac.py humphrjk@169.254.150.102:~/disaggregated_inference/

# Restart servers
./disaggregated_inference/start_dgx_servers.sh
./disaggregated_inference/start_mac_servers.sh
```

### View All Logs
```bash
# Create a tmux session with all logs
tmux new-session -d -s logs
tmux split-window -h
tmux split-window -v
tmux select-pane -t 0
tmux split-window -v

tmux select-pane -t 0
tmux send-keys "ssh humphrjk@169.254.150.103 'tail -f ~/logs/prefill_qwen.log'" C-m

tmux select-pane -t 1
tmux send-keys "ssh humphrjk@169.254.150.104 'tail -f ~/logs/prefill_gpt_oss.log'" C-m

tmux select-pane -t 2
tmux send-keys "tail -f ~/logs/decode_qwen.log" C-m

tmux select-pane -t 3
tmux send-keys "ssh humphrjk@169.254.150.102 'tail -f ~/logs/decode_gpt_oss.log'" C-m

tmux attach -t logs
```

## Success Criteria

- [ ] All 4 servers respond to health checks
- [ ] Prefill servers return KV cache successfully
- [ ] Decode servers generate tokens from KV cache
- [ ] Orchestrator completes end-to-end generation
- [ ] Performance better than Mac-only baseline
- [ ] Fallback works when servers unavailable
