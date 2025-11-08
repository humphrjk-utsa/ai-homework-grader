# Disaggregated Inference System - Complete Index

## 📚 Documentation

### Getting Started
- **[QUICKSTART.md](QUICKSTART.md)** - Get running in 3 steps
- **[DEPLOYMENT.md](DEPLOYMENT.md)** - Detailed deployment guide with troubleshooting
- **[README.md](README.md)** - System overview and API documentation

### Technical Details
- **[ARCHITECTURE.md](ARCHITECTURE.md)** - System architecture, data flow, and design decisions

## 🔧 Core Components

### Servers
- **[prefill_server_dgx.py](prefill_server_dgx.py)** - DGX prefill server (PyTorch/CUDA)
  - Processes prompts on 8x H100 GPUs
  - Generates KV cache for decode
  - Endpoints: `/health`, `/prefill`, `/status`

- **[decode_server_mac.py](decode_server_mac.py)** - Mac decode server (MLX)
  - Receives KV cache from DGX
  - Generates tokens on Apple Silicon
  - Endpoints: `/health`, `/decode`, `/generate`, `/status`

### Orchestration
- **[orchestrator.py](orchestrator.py)** - Coordinates prefill and decode
  - Health monitoring
  - Request routing
  - Automatic fallback
  - Load balancing

## 🚀 Deployment Scripts

### Startup
- **[deploy_to_machines.sh](deploy_to_machines.sh)** - Deploy files to all machines
- **[start_dgx_servers.sh](start_dgx_servers.sh)** - Start DGX prefill servers
- **[start_mac_servers.sh](start_mac_servers.sh)** - Start Mac decode servers
- **[stop_all_servers.sh](stop_all_servers.sh)** - Stop all servers

### Monitoring
- **[check_status.py](check_status.py)** - Check health of all servers
- **[monitor_logs.sh](monitor_logs.sh)** - View all logs in tmux

### Testing
- **[test_system.py](test_system.py)** - End-to-end system tests

## 📊 System Configuration

### Network Topology
```
DGX Spark 1:  192.168.100.1:8000   (Qwen 30B Prefill)
DGX Spark 2:  192.168.100.2:8000   (GPT-OSS 120B Prefill)
Mac Studio 1: 169.254.150.101:8001 (Qwen 30B Decode)
Mac Studio 2: 169.254.150.102:8001 (GPT-OSS 120B Decode)
```

### Models
- **Qwen 3 Coder 30B** (FP4 quantized)
  - Path: `~/models/fp4/qwen3-coder-30b-fp4/`
  - Use case: Code generation
  
- **GPT-OSS 120B** (FP4 quantized)
  - Path: `~/models/fp4/gpt-oss-120b-fp4/`
  - Use case: General text generation

## 🎯 Quick Reference

### Start Everything
```bash
# 1. Deploy files
./disaggregated_inference/deploy_to_machines.sh

# 2. Start DGX servers
./disaggregated_inference/start_dgx_servers.sh

# 3. Start Mac servers
./disaggregated_inference/start_mac_servers.sh

# 4. Check status
python3 disaggregated_inference/check_status.py

# 5. Run tests
python3 disaggregated_inference/test_system.py
```

### Monitor
```bash
# Check status
python3 disaggregated_inference/check_status.py

# View all logs
./disaggregated_inference/monitor_logs.sh

# Check individual server
curl http://192.168.100.1:8000/health
```

### Stop Everything
```bash
./disaggregated_inference/stop_all_servers.sh
```

## 🔍 Troubleshooting

### Server not responding
```bash
# Check if running
ps aux | grep server

# Check logs
tail -f ~/logs/prefill_qwen.log
tail -f ~/logs/decode_qwen.log

# Restart
./disaggregated_inference/stop_all_servers.sh
./disaggregated_inference/start_dgx_servers.sh
./disaggregated_inference/start_mac_servers.sh
```

### Network issues
```bash
# Test connectivity
ping 192.168.100.1
curl http://192.168.100.1:8000/health

# Check ports
nc -zv 192.168.100.1 8000
```

### Model not loading
```bash
# Check model exists
ls ~/models/fp4/qwen3-coder-30b-fp4/

# Check CUDA (DGX)
nvidia-smi

# Check MLX (Mac)
python3 -c "import mlx.core as mx; print(mx.metal.is_available())"
```

## 📈 Performance Expectations

### Qwen 3 Coder 30B
- Prefill: ~0.5-1s (DGX)
- Decode: ~50-80 tok/s (Mac)
- Better than Mac-only: ~30 tok/s

### GPT-OSS 120B
- Prefill: ~2-3s (DGX)
- Decode: ~20-30 tok/s (Mac)
- Better than Mac-only: ~10 tok/s

## 🔗 Integration

### Python API
```python
from disaggregated_inference.orchestrator import DisaggregatedInference

config = {
    'prefill_servers': [
        {'host': '192.168.100.1', 'port': 8000, 'model': 'qwen'},
    ],
    'decode_servers': [
        {'host': '169.254.150.101', 'port': 8001, 'model': 'qwen'},
    ]
}

orchestrator = DisaggregatedInference(config)
result = await orchestrator.generate(
    prompt="def fibonacci(n):",
    model_type="qwen",
    max_tokens=100
)
```

### REST API
```bash
# Prefill (DGX)
curl -X POST http://192.168.100.1:8000/prefill \
  -H "Content-Type: application/json" \
  -d '{"prompt": "def fibonacci(n):"}'

# Decode (Mac)
curl -X POST http://169.254.150.101:8001/decode \
  -H "Content-Type: application/json" \
  -d '{"kv_cache": "...", "max_new_tokens": 100}'
```

## 📝 File Summary

| File | Purpose | Type |
|------|---------|------|
| QUICKSTART.md | Quick start guide | Doc |
| DEPLOYMENT.md | Deployment guide | Doc |
| README.md | System overview | Doc |
| ARCHITECTURE.md | Technical architecture | Doc |
| INDEX.md | This file | Doc |
| prefill_server_dgx.py | DGX prefill server | Code |
| decode_server_mac.py | Mac decode server | Code |
| orchestrator.py | Request coordinator | Code |
| check_status.py | Health checker | Tool |
| test_system.py | System tests | Tool |
| deploy_to_machines.sh | Deployment script | Script |
| start_dgx_servers.sh | Start DGX servers | Script |
| start_mac_servers.sh | Start Mac servers | Script |
| stop_all_servers.sh | Stop all servers | Script |
| monitor_logs.sh | Log monitoring | Script |

## 🎓 Learning Path

1. **Understand the concept** → Read [ARCHITECTURE.md](ARCHITECTURE.md)
2. **Get it running** → Follow [QUICKSTART.md](QUICKSTART.md)
3. **Deploy properly** → Use [DEPLOYMENT.md](DEPLOYMENT.md)
4. **Integrate it** → See [README.md](README.md) API section
5. **Troubleshoot** → Check [DEPLOYMENT.md](DEPLOYMENT.md) troubleshooting

## 🚦 Status Indicators

### ✅ All Systems Operational
- All 4 servers responding
- Models loaded
- Network connectivity good
- Ready for inference

### ⚠️ Degraded Mode
- Some servers unavailable
- Fallback to Mac-only
- Reduced performance

### ❌ System Down
- No servers responding
- Need to restart
- Check logs for errors

## 📞 Support

For issues:
1. Check [DEPLOYMENT.md](DEPLOYMENT.md) troubleshooting section
2. Run `python3 disaggregated_inference/check_status.py`
3. Check logs: `./disaggregated_inference/monitor_logs.sh`
4. Review [ARCHITECTURE.md](ARCHITECTURE.md) for design details
