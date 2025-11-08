# Disaggregated Inference Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                    DISAGGREGATED INFERENCE SYSTEM                    │
│                                                                       │
│  Splits inference workload between DGX (prefill) and Mac (decode)   │
└─────────────────────────────────────────────────────────────────────┘

                              ┌──────────────┐
                              │ Orchestrator │
                              │  (Mac 1)     │
                              └──────┬───────┘
                                     │
                    ┌────────────────┴────────────────┐
                    │                                 │
                    ▼                                 ▼
        ┌───────────────────────┐       ┌───────────────────────┐
        │   PREFILL CLUSTER     │       │   DECODE CLUSTER      │
        │   (DGX Sparks)        │       │   (Mac Studios)       │
        └───────────────────────┘       └───────────────────────┘
                    │                                 │
        ┌───────────┴───────────┐         ┌──────────┴──────────┐
        │                       │         │                     │
        ▼                       ▼         ▼                     ▼
┌──────────────┐      ┌──────────────┐  ┌──────────┐  ┌──────────┐
│  DGX Spark 1 │      │  DGX Spark 2 │  │  Mac 1   │  │  Mac 2   │
│              │      │              │  │          │  │          │
│ Qwen 30B     │      │ GPT-OSS 120B │  │ Qwen 30B │  │ GPT-OSS  │
│ Prefill      │      │ Prefill      │  │ Decode   │  │ Decode   │
│              │      │              │  │          │  │          │
│ 8x H100      │      │ 8x H100      │  │ M2 Ultra │  │ M2 Ultra │
│ 640GB VRAM   │      │ 640GB VRAM   │  │ 192GB    │  │ 192GB    │
│              │      │              │  │          │  │          │
│ 192.168.     │      │ 192.168.     │  │ 169.254. │  │ 169.254. │
│ 100.1:8000   │      │ 100.2:8000   │  │ .101:8001│  │ .102:8001│
└──────────────┘      └──────────────┘  └──────────┘  └──────────┘
       │                     │                 │            │
       └─────────┬───────────┘                 └─────┬──────┘
                 │                                   │
                 │  ConnectX-7 200Gb/s              │  Thunderbolt
                 │  (Static IPs)                     │  (Static IPs)
                 └───────────────┬───────────────────┘
                                 │
                          KV Cache Transfer
```

## Data Flow

### 1. Request Initiation
```
User/App → Orchestrator
          ↓
    Select best servers
    (based on model type & health)
```

### 2. Prefill Phase (DGX)
```
Orchestrator → DGX Prefill Server
               ↓
         Tokenize prompt
               ↓
         Forward pass (parallel)
               ↓
         Generate KV cache
               ↓
         Serialize & encode
               ↓
Orchestrator ← KV cache (base64)
```

### 3. Transfer Phase
```
KV Cache → ConnectX-7 (200Gb/s)
           ↓
      Mac Studio
```

### 4. Decode Phase (Mac)
```
Orchestrator → Mac Decode Server
               ↓
         Deserialize KV cache
               ↓
         Generate tokens (sequential)
               ↓
         MLX optimized
               ↓
Orchestrator ← Generated text
```

### 5. Response
```
Orchestrator → User/App
    {
        response: "generated text",
        prefill_time: 0.5s,
        decode_time: 2.0s,
        tokens_per_sec: 50
    }
```

## Network Architecture

### ConnectX-7 Network (DGX ↔ Mac)
```
DGX Spark 1 (192.168.100.1) ─┐
                              ├─ ConnectX-7 Switch
DGX Spark 2 (192.168.100.2) ─┘      │
                                     │ 200Gb/s
                                     │
Mac Studio 1 (169.254.150.101) ─┐   │
                                 ├───┘
Mac Studio 2 (169.254.150.102) ─┘
```

### Thunderbolt Network (Mac ↔ Mac)
```
Mac Studio 1 (169.254.150.101) ←→ Mac Studio 2 (169.254.150.102)
                    40Gb/s Thunderbolt
```

## Component Details

### Prefill Server (DGX)
**Technology:** PyTorch + CUDA + Transformers
**Purpose:** Fast parallel prompt processing
**Input:** Text prompt
**Output:** KV cache + input IDs
**Optimization:** 
- FP4 quantization
- Tensor parallelism across 8x H100
- NVLink for inter-GPU communication

### Decode Server (Mac)
**Technology:** MLX (Apple Silicon optimized)
**Purpose:** Efficient sequential token generation
**Input:** KV cache from DGX
**Output:** Generated tokens
**Optimization:**
- Unified memory architecture
- Metal GPU acceleration
- FP4 quantization

### Orchestrator
**Technology:** Python + asyncio + aiohttp
**Purpose:** Coordinate prefill and decode
**Features:**
- Health monitoring
- Automatic failover
- Load balancing
- Fallback to Mac-only

## Performance Characteristics

### Prefill (DGX)
- **Qwen 30B:** ~0.5-1s for typical prompts
- **GPT-OSS 120B:** ~2-3s for typical prompts
- **Bottleneck:** Model size, prompt length
- **Scaling:** Linear with GPU count

### Decode (Mac)
- **Qwen 30B:** ~50-80 tok/s
- **GPT-OSS 120B:** ~20-30 tok/s
- **Bottleneck:** Sequential generation
- **Scaling:** Memory bandwidth limited

### Network Transfer
- **KV Cache Size:** ~100-500MB typical
- **Transfer Time:** ~0.01-0.05s (200Gb/s)
- **Negligible overhead**

## Advantages

### vs Mac-Only
✅ Faster prefill (8x H100 vs M2 Ultra)
✅ Better for long prompts
✅ Parallel processing of multiple requests
✅ Higher throughput

### vs DGX-Only
✅ More efficient decode (MLX optimization)
✅ Lower latency for token generation
✅ Better resource utilization
✅ Energy efficient

## Failure Modes & Fallbacks

### DGX Prefill Unavailable
```
Orchestrator detects failure
    ↓
Falls back to Mac-only generation
    ↓
Full inference on Mac Studio
```

### Mac Decode Unavailable
```
Orchestrator detects failure
    ↓
Cannot complete inference
    ↓
Return error to user
```

### Network Issues
```
KV cache transfer fails
    ↓
Retry with timeout
    ↓
If fails: fallback to Mac-only
```

## Monitoring Points

1. **Server Health**
   - Model loaded status
   - Memory usage
   - Response time

2. **Network Performance**
   - Transfer speed
   - Latency
   - Packet loss

3. **Inference Metrics**
   - Prefill time
   - Decode time
   - Tokens per second
   - End-to-end latency

4. **System Resources**
   - GPU utilization (DGX)
   - Memory usage (Mac)
   - CPU usage
   - Network bandwidth

## Scaling Considerations

### Horizontal Scaling
- Add more DGX Sparks for prefill capacity
- Add more Mac Studios for decode capacity
- Load balancer distributes requests

### Vertical Scaling
- Larger models (up to 120B tested)
- More GPUs per DGX (8x H100 current)
- More memory per Mac (192GB current)

### Future Enhancements
- Pipeline parallelism
- Speculative decoding
- Batch processing
- Request queuing
- Dynamic model loading
