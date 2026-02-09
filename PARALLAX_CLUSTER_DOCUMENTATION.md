# Parallax Distributed Inference Cluster Documentation

## Overview

This document describes the Parallax distributed inference cluster used by the AI Homework Grader application. The cluster distributes LLM inference across multiple Mac Studios and NVIDIA DGX Sparks connected via a 10Gb Thunderbolt bridge network.

## Architecture

### Hardware Configuration

| Node | Hostname/IP | Hardware | Role | Memory |
|------|-------------|----------|------|--------|
| **Mac 1** | 169.254.150.101 | Apple M3 Ultra | Scheduler + Worker | 512GB Unified |
| **Mac 2** | 169.254.150.102 | Apple M4 Ultra | Worker | 128GB Unified |
| **spark-2935** | 169.254.150.106 | NVIDIA DGX Spark (GB10) | GPU Prefill Worker | ~50GB GPU |
| **RR191562IP01** | 169.254.150.105 | NVIDIA DGX Spark (GB10) | GPU Prefill Worker | ~50GB GPU |

### Network Topology

```
                    ┌─────────────────────────────────────┐
                    │     10Gb Thunderbolt Bridge         │
                    │         169.254.150.x               │
                    └─────────────────────────────────────┘
                           │         │         │         │
                    ┌──────┴──┐ ┌────┴────┐ ┌──┴───┐ ┌───┴───┐
                    │ Mac 1   │ │ Mac 2   │ │Spark1│ │Spark2 │
                    │ .101    │ │ .102    │ │ .106 │ │ .105  │
                    │Scheduler│ │ Worker  │ │Worker│ │Worker │
                    └─────────┘ └─────────┘ └──────┘ └───────┘
```

## Software Stack

### Parallax Framework

Parallax is a distributed inference engine by Gradient Network that enables:
- **Pipeline Parallelism**: Split model layers across multiple nodes
- **P2P Networking**: Nodes discover each other automatically via libp2p
- **OpenAI-Compatible API**: Standard `/v1/chat/completions` endpoint
- **Heterogeneous Hardware**: Mix Apple Silicon (MLX) and NVIDIA GPUs (SGLang)

### Installation Locations

| Node | Installation Path | Python Version |
|------|-------------------|----------------|
| Mac 1 | `/Users/humphrjk/parallax/` | Python 3.12 (Anaconda) |
| Mac 2 | `/Users/humphrjk/parallax/` | Python 3.12 (installed from Mac 1) |
| Sparks | Docker container | Python 3.12 (in container) |

### Key Files Modified

1. **`/Users/humphrjk/parallax/src/parallax/server/server_info.py`**
   - Added M3 Ultra (56.8 TFLOPS) and M4 Ultra (68.16 TFLOPS) to `_APPLE_PEAK_FP16` dictionary
   - Required because Parallax didn't recognize these newer Apple Silicon chips

2. **`/Users/humphrjk/Library/CloudStorage/OneDrive-ionxs.ai/analytics/ai-homework-grader/disaggregated_client.py`**
   - Updated to use Parallax API instead of llama.cpp KV cache transfer
   - Maintains backward compatibility with existing grader interface

## How Orchestration Works

### Cluster Startup Sequence

1. **Scheduler Initialization (Mac 1)**
   ```bash
   cd /Users/humphrjk/parallax
   source venv/bin/activate
   parallax run -m Qwen/Qwen3-0.6B -n 4 --host 0.0.0.0
   ```
   - Starts the Parallax scheduler on port 3001
   - Loads model metadata and tokenizer
   - Begins P2P discovery broadcasting
   - Serves OpenAI-compatible API at `http://169.254.150.101:3001/v1/chat/completions`

2. **Worker Join (Mac 2)**
   ```bash
   cd /Users/humphrjk/parallax
   source venv/bin/activate
   parallax join
   ```
   - Auto-discovers scheduler via P2P
   - Receives layer assignment from scheduler
   - Loads assigned model layers into MLX
   - Allocates KV cache in unified memory

3. **GPU Workers Join (Sparks)**
   ```bash
   sudo docker run -d --gpus all --network host \
     gradientservice/parallax:latest-spark parallax join
   ```
   - Docker container with CUDA/SGLang support
   - Auto-discovers scheduler
   - Loads model layers onto GPU
   - Uses SGLang for efficient CUDA inference

### Request Flow

```
Client Request
      │
      ▼
┌─────────────────┐
│   Scheduler     │  (Mac 1 - port 3001)
│   - Routes req  │
│   - Manages KV  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐     ┌─────────────────┐
│  Prefill Phase  │ ──► │  Decode Phase   │
│  (GPU Workers)  │     │  (Mac Workers)  │
│  - Fast prompt  │     │  - Token-by-    │
│    processing   │     │    token gen    │
└─────────────────┘     └─────────────────┘
         │                       │
         └───────────┬───────────┘
                     ▼
              Response to Client
```

### Layer Distribution

When running Qwen3-0.6B (28 layers) with 4 nodes:
- Each node gets assigned layers 0-28 (full model on each for redundancy)
- Scheduler load-balances requests across available nodes
- With larger models, layers are sharded across nodes

## Configuration Files

### `parallax_config.json`
```json
{
  "parallax": {
    "scheduler_url": "http://169.254.150.101:3001",
    "enabled": true,
    "default_model": "Qwen/Qwen3-0.6B",
    "production_models": {
      "code_analysis": "Qwen/Qwen3-Coder-30B-A3B-Instruct",
      "feedback": "openai/gpt-oss"
    }
  },
  "cluster_nodes": {
    "mac_1": { "ip": "169.254.150.101", "role": "scheduler", "chip": "M3 Ultra", "memory_gb": 512 },
    "mac_2": { "ip": "169.254.150.102", "role": "worker", "chip": "M4 Ultra", "memory_gb": 128 },
    "spark_1": { "ip": "169.254.150.106", "hostname": "spark-2935", "role": "prefill", "gpu": "NVIDIA" },
    "spark_2": { "ip": "169.254.150.105", "hostname": "RR191562IP01", "role": "prefill", "gpu": "NVIDIA" }
  },
  "batch_processing": {
    "concurrent_enabled": true,
    "default_batch_size": 4,
    "max_batch_size": 8,
    "cooling_break_seconds": 5
  }
}
```

## Cluster Management Scripts

All scripts located in: `/Users/humphrjk/Library/CloudStorage/OneDrive-ionxs.ai/analytics/ai-homework-grader/`

### Start Cluster
```bash
./parallax_cluster_start.sh [model_name]
# Example: ./parallax_cluster_start.sh Qwen/Qwen3-0.6B
```
This script:
1. Starts scheduler on Mac 1
2. Waits for scheduler initialization
3. Joins Mac 2 as worker
4. Starts Docker containers on both Sparks
5. Verifies cluster is operational

### Stop Cluster
```bash
./parallax_cluster_stop.sh
```
This script:
1. Kills parallax processes on Mac 1
2. Kills parallax processes on Mac 2
3. Stops Docker containers on spark-2935
4. Stops Docker containers on RR191562IP01

### Check Status
```bash
./parallax_cluster_status.sh
```
Shows status of all nodes and tests inference.

## Integration with AI Homework Grader

### Detection Priority

The grader (`business_analytics_grader_v2.py`) checks backends in this order:

1. **Parallax** (highest priority)
   - Checks if `parallax_config.json` exists
   - Tests connection to scheduler
   - Uses `models/parallax_client.py`

2. **Disaggregated Client** (fallback)
   - Checks if `disaggregated_inference/config_current.json` exists
   - Now also uses Parallax (updated client)
   - Uses `disaggregated_client.py`

3. **Distributed MLX** (legacy)
   - Checks if `distributed_config.json` exists
   - Direct MLX cluster (not Parallax)

4. **Local Ollama** (final fallback)
   - Uses local Ollama server
   - Slowest option

### API Usage

```python
from disaggregated_client import DisaggregatedClient

# Initialize client
client = DisaggregatedClient()

# Single generation
response, metrics = client.generate(
    model='qwen3-coder:30b',  # Model hint (actual model from cluster config)
    prompt='Analyze this code...',
    max_tokens=2000
)

# Parallel generation (code + feedback simultaneously)
results = client.generate_parallel(
    code_prompt='Analyze this R code...',
    feedback_prompt='Generate feedback for student...',
    code_max_tokens=2400,
    feedback_max_tokens=3500
)
```

### OpenAI-Compatible Direct API

```bash
curl -X POST 'http://169.254.150.101:3001/v1/chat/completions' \
  -H 'Content-Type: application/json' \
  -d '{
    "messages": [{"role": "user", "content": "Hello"}],
    "max_tokens": 100,
    "chat_template_kwargs": {"enable_thinking": false}
  }'
```

## Setting Up the Cluster from Scratch

### Prerequisites

1. All machines connected via 10Gb Thunderbolt bridge
2. SSH access configured between all nodes
3. Python 3.12 installed on Macs
4. Docker with NVIDIA runtime on Sparks

### Step 1: Install Parallax on Mac 1

```bash
cd /Users/humphrjk
git clone https://github.com/gradientnetwork/parallax.git
cd parallax
python3.12 -m venv venv
source venv/bin/activate
pip install -e .
```

### Step 2: Patch for M3/M4 Ultra Support

Edit `src/parallax/server/server_info.py`, add to `_APPLE_PEAK_FP16`:
```python
"M3 Ultra": 56.8,   # 2x M3 Max
"M4 Ultra": 68.16,  # 2x M4 Max
```

### Step 3: Copy to Mac 2

```bash
# Copy Python installer
scp /tmp/python-3.12.2-macos11.pkg humphrjk@169.254.150.102:/tmp/
ssh humphrjk@169.254.150.102 "sudo installer -pkg /tmp/python-3.12.2-macos11.pkg -target /"

# Create venv and copy packages
ssh humphrjk@169.254.150.102 "/usr/local/bin/python3.12 -m venv /Users/humphrjk/parallax/venv"
rsync -av /Users/humphrjk/parallax/venv/lib/python3.12/site-packages/ \
  humphrjk@169.254.150.102:/Users/humphrjk/parallax/venv/lib/python3.12/site-packages/
rsync -av /Users/humphrjk/parallax/src/ humphrjk@169.254.150.102:/Users/humphrjk/parallax/src/

# Copy model cache
rsync -av ~/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/ \
  humphrjk@169.254.150.102:~/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/

# Create entry script
scp /Users/humphrjk/parallax/venv/bin/parallax humphrjk@169.254.150.102:/Users/humphrjk/parallax/venv/bin/
```

### Step 4: Pull Docker Image on Sparks

```bash
ssh humphrjk@169.254.150.106 "sudo docker pull gradientservice/parallax:latest-spark"
ssh humphrjk@169.254.150.105 "sudo docker pull gradientservice/parallax:latest-spark"
```

### Step 5: Start the Cluster

```bash
./parallax_cluster_start.sh Qwen/Qwen3-0.6B
```

## Troubleshooting

### Common Issues

1. **"Unknown Apple silicon chip" error**
   - Add chip to `_APPLE_PEAK_FP16` in `server_info.py`

2. **Mac 2 can't download models (no internet)**
   - Copy model cache from Mac 1 via rsync
   - Models stored in `~/.cache/huggingface/hub/`

3. **Sparks connecting via relay instead of local**
   - Use `parallax join` without specifying peer ID
   - Auto-discovery works on local network

4. **High CPU/fans after stopping cluster**
   - Check for leftover processes: `ps aux | grep -E "parallax|llama|python.*model"`
   - Kill any remaining LLM servers

5. **VS Code slow with many open files**
   - Kill heavy VS Code processes
   - Clear workspace storage if tabs keep reopening

### Checking for Leftover Processes

```bash
# On all machines
ps aux | grep -iE "llama|gguf|ollama|parallax|mlx.*server|decode_server|prefill_server" | grep -v grep
```

## Performance Metrics

With Qwen3-0.6B on 4-node cluster:
- **Single request**: ~80-160 tokens/second
- **Parallel efficiency**: ~1.8x (two requests simultaneously)
- **Cluster capacity**: 16+ concurrent requests

## Files Reference

| File | Purpose |
|------|---------|
| `parallax_config.json` | Cluster configuration |
| `disaggregated_client.py` | Python client for Parallax API |
| `models/parallax_client.py` | Alternative Parallax client |
| `business_analytics_grader_v2.py` | Main grader (uses Parallax) |
| `parallax_cluster_start.sh` | Start all nodes |
| `parallax_cluster_stop.sh` | Stop all nodes |
| `parallax_cluster_status.sh` | Check cluster status |
| `test_parallax_integration.py` | Integration tests |

## Contact & Resources

- **Parallax GitHub**: https://github.com/gradientnetwork/parallax
- **Parallax Dashboard**: http://169.254.150.101:3001 (when running)
- **Model Source**: HuggingFace (auto-downloaded)
