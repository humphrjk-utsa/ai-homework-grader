# Setting Up Two New DGX Sparks

## Current Network Configuration

### Existing Devices (Thunderbolt Network 169.254.150.x)
- **Mac Studio 1**: 169.254.150.101 (GPT-OSS decode)
- **Mac Studio 2**: 169.254.150.102 (Qwen decode)
- **DGX Spark 1**: 169.254.150.103 (Qwen prefill)
- **DGX Spark 2**: 169.254.150.104 (GPT-OSS prefill)

### New Devices to Add
- **DGX Spark 3**: 169.254.150.105 (TBD model)
- **DGX Spark 4**: 169.254.150.106 (TBD model)

---

## Step 1: Connect DGX Spark to Thunderbolt Network

1. **Physical Connection**:
   - Connect Thunderbolt cable from new DGX Spark to the Thunderbolt network
   - Ensure the Thunderbolt interface is active

2. **Check Current IP** (on the DGX Spark):
   ```bash
   ip addr show
   # Look for the Thunderbolt interface (usually thunderbolt0 or similar)
   ```

---

## Step 2: Set Static IP on DGX Spark (Ubuntu/Linux)

### Option A: Using NetworkManager (Recommended)

1. **Find the Thunderbolt interface name**:
   ```bash
   ip link show
   # Look for interface like: thunderbolt0, enp0s20f0u1, etc.
   ```

2. **Set static IP using nmcli**:
   ```bash
   # For DGX Spark 3 (169.254.150.105)
   sudo nmcli connection modify "Thunderbolt" ipv4.addresses 169.254.150.105/16
   sudo nmcli connection modify "Thunderbolt" ipv4.method manual
   sudo nmcli connection down "Thunderbolt"
   sudo nmcli connection up "Thunderbolt"
   
   # For DGX Spark 4 (169.254.150.106)
   sudo nmcli connection modify "Thunderbolt" ipv4.addresses 169.254.150.106/16
   sudo nmcli connection modify "Thunderbolt" ipv4.method manual
   sudo nmcli connection down "Thunderbolt"
   sudo nmcli connection up "Thunderbolt"
   ```

3. **Verify**:
   ```bash
   ip addr show | grep 169.254
   ping 169.254.150.101  # Test connectivity to Mac Studio 1
   ```

### Option B: Using Netplan (Alternative)

1. **Edit netplan configuration**:
   ```bash
   sudo nano /etc/netplan/01-netcfg.yaml
   ```

2. **Add configuration** (replace `INTERFACE_NAME` with actual interface):
   ```yaml
   network:
     version: 2
     renderer: networkd
     ethernets:
       INTERFACE_NAME:  # e.g., thunderbolt0
         addresses:
           - 169.254.150.105/16  # For Spark 3
         dhcp4: no
   ```

3. **Apply configuration**:
   ```bash
   sudo netplan apply
   ```

### Option C: Manual Configuration (Temporary)

```bash
# For DGX Spark 3
sudo ip addr add 169.254.150.105/16 dev INTERFACE_NAME
sudo ip link set INTERFACE_NAME up

# For DGX Spark 4
sudo ip addr add 169.254.150.106/16 dev INTERFACE_NAME
sudo ip link set INTERFACE_NAME up
```

**Note**: This is temporary and will reset on reboot.

---

## Step 3: Install Ollama on New DGX Sparks

```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Start Ollama service
sudo systemctl start ollama
sudo systemctl enable ollama

# Verify Ollama is running
ollama list
```

---

## Step 4: Pull Required Models

### For Qwen Prefill Server:
```bash
ollama pull hopephoto/qwen3-coder-30b-a3b-instruct_q8:latest
```

### For GPT-OSS Prefill Server:
```bash
ollama pull gemma3:27b-it-q8_0
```

### Or for additional capacity:
```bash
# If you want both models on each Spark
ollama pull hopephoto/qwen3-coder-30b-a3b-instruct_q8:latest
ollama pull gemma3:27b-it-q8_0
```

---

## Step 5: Deploy Prefill Server

1. **Copy server files to DGX Spark**:
   ```bash
   # From this Mac Studio
   scp disaggregated_inference/prefill_server_ollama.py user@169.254.150.105:~/
   scp disaggregated_inference/start_dgx_servers_ollama.sh user@169.254.150.105:~/
   ```

2. **On the DGX Spark, start the prefill server**:
   ```bash
   # For Qwen model
   python3 prefill_server_ollama.py \
     --model hopephoto/qwen3-coder-30b-a3b-instruct_q8:latest \
     --port 8000 \
     --host 0.0.0.0
   
   # Or for GPT-OSS model
   python3 prefill_server_ollama.py \
     --model gemma3:27b-it-q8_0 \
     --port 8000 \
     --host 0.0.0.0
   ```

3. **Run as systemd service** (optional, for auto-start):
   ```bash
   sudo nano /etc/systemd/system/prefill-server.service
   ```
   
   Add:
   ```ini
   [Unit]
   Description=Disaggregated Inference Prefill Server
   After=network.target ollama.service
   
   [Service]
   Type=simple
   User=YOUR_USERNAME
   WorkingDirectory=/home/YOUR_USERNAME
   ExecStart=/usr/bin/python3 /home/YOUR_USERNAME/prefill_server_ollama.py --model hopephoto/qwen3-coder-30b-a3b-instruct_q8:latest --port 8000 --host 0.0.0.0
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```
   
   Enable:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable prefill-server
   sudo systemctl start prefill-server
   ```

---

## Step 6: Update Configuration

1. **Edit config file** on this Mac Studio:
   ```bash
   nano disaggregated_inference/config_current.json
   ```

2. **Add new servers**:
   ```json
   {
     "prefill_servers": [
       {
         "host": "169.254.150.103",
         "port": 8000,
         "model": "qwen",
         "name": "DGX Spark 1"
       },
       {
         "host": "169.254.150.104",
         "port": 8000,
         "model": "gpt-oss",
         "name": "DGX Spark 2"
       },
       {
         "host": "169.254.150.105",
         "port": 8000,
         "model": "qwen",
         "name": "DGX Spark 3"
       },
       {
         "host": "169.254.150.106",
         "port": 8000,
         "model": "gpt-oss",
         "name": "DGX Spark 4"
       }
     ],
     "decode_servers": [
       {
         "host": "169.254.150.102",
         "port": 8001,
         "model": "qwen",
         "name": "Mac Studio 2"
       },
       {
         "host": "169.254.150.101",
         "port": 8001,
         "model": "gpt-oss",
         "name": "Mac Studio 1"
       }
     ]
   }
   ```

---

## Step 7: Test Connectivity

```bash
# From this Mac Studio
cd disaggregated_inference

# Test new Spark 3
curl http://169.254.150.105:8000/health

# Test new Spark 4
curl http://169.254.150.106:8000/health

# Run full system test
python3 test_system.py
```

---

## Step 8: Update Load Balancing (Optional)

If you want to use all 4 Sparks for load balancing, update the orchestrator to distribute requests across all prefill servers.

---

## Troubleshooting

### Can't ping new Spark
```bash
# On DGX Spark, check firewall
sudo ufw status
sudo ufw allow from 169.254.0.0/16  # Allow Thunderbolt network

# Check if interface is up
ip link show
sudo ip link set INTERFACE_NAME up
```

### Ollama not responding
```bash
# Check Ollama status
sudo systemctl status ollama

# Check logs
journalctl -u ollama -f

# Restart Ollama
sudo systemctl restart ollama
```

### Port already in use
```bash
# Check what's using port 8000
sudo lsof -i :8000

# Kill process if needed
sudo kill -9 PID
```

---

## Quick Reference

| Device | IP Address | Port | Model | Role |
|--------|------------|------|-------|------|
| Mac Studio 1 | 169.254.150.101 | 8001 | GPT-OSS | Decode |
| Mac Studio 2 | 169.254.150.102 | 8001 | Qwen | Decode |
| DGX Spark 1 | 169.254.150.103 | 8000 | Qwen | Prefill |
| DGX Spark 2 | 169.254.150.104 | 8000 | GPT-OSS | Prefill |
| **DGX Spark 3** | **169.254.150.105** | **8000** | **Qwen** | **Prefill** |
| **DGX Spark 4** | **169.254.150.106** | **8000** | **GPT-OSS** | **Prefill** |

---

## Benefits of Adding 2 More Sparks

- **2x Prefill Capacity**: Can process 4 prompts simultaneously
- **Load Balancing**: Distribute requests across 4 Sparks
- **Redundancy**: If one Spark fails, others continue
- **Faster Batch Grading**: Process more submissions in parallel

With 4 Sparks + 2 Mac Studios, you can grade **4 submissions simultaneously**!
