# Disaggregated Inference System - Visual Diagrams

## 1. Complete System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         GRADING APPLICATION LAYER                            │
│                                                                               │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  Streamlit Web Interface (connect_web_interface.py)                   │  │
│  │  • Upload notebooks                                                    │  │
│  │  • Trigger grading                                                     │  │
│  │  • View results & metrics                                              │  │
│  └────────────────────────────┬─────────────────────────────────────────┘  │
│                                │                                             │
│  ┌────────────────────────────▼─────────────────────────────────────────┐  │
│  │  Business Analytics Grader V2 (business_analytics_grader_v2.py)      │  │
│  │  • 4-layer validation system                                          │  │
│  │  • Parallel AI analysis                                               │  │
│  │  • Score calculation & validation                                     │  │
│  └────────────────────────────┬─────────────────────────────────────────┘  │
└─────────────────────────────────┼───────────────────────────────────────────┘
                                  │
┌─────────────────────────────────▼───────────────────────────────────────────┐
│                      DISAGGREGATED INFERENCE LAYER                           │
│                                                                               │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  Disaggregated Client (disaggregated_client.py)                       │  │
│  │  • Model routing (Qwen vs GPT-OSS)                                    │  │
│  │  • Parallel request coordination                                      │  │
│  │  • Health monitoring & failover                                       │  │
│  │  • Metrics aggregation                                                │  │
│  └──────────────┬────────────────────────────────┬──────────────────────┘  │
│                 │                                 │                          │
│                 │                                 │                          │
│    ┌────────────▼──────────┐       ┌─────────────▼──────────┐              │
│    │  Qwen Request         │       │  GPT-OSS Request       │              │
│    │  (Code Analysis)      │       │  (Feedback Gen)        │              │
│    └────────────┬──────────┘       └─────────────┬──────────┘              │
└─────────────────┼──────────────────────────────────┼─────────────────────────┘
                  │                                  │
                  │                                  │
┌─────────────────▼──────────────┐  ┌──────────────▼──────────────────────────┐
│     PREFILL CLUSTER (DGX)      │  │      PREFILL CLUSTER (DGX)              │
│                                 │  │                                          │
│  ┌──────────────────────────┐  │  │  ┌──────────────────────────┐          │
│  │  DGX Spark 1             │  │  │  │  DGX Spark 2             │          │
│  │  169.254.150.103:8000    │  │  │  │  169.254.150.104:8000    │          │
│  │                          │  │  │  │                          │          │
│  │  Flask Prefill Server    │  │  │  │  Flask Prefill Server    │          │
│  │  ↓                       │  │  │  │  ↓                       │          │
│  │  Ollama                  │  │  │  │  Ollama                  │          │
│  │  ↓                       │  │  │  │  ↓                       │          │
│  │  Qwen 3.0 Coder 30B      │  │  │  │  GPT-OSS 120B            │          │
│  │  (Q8 quantized)          │  │  │  │  (Q8 quantized)          │          │
│  │  ↓                       │  │  │  │  ↓                       │          │
│  │  2x H100 GPUs            │  │  │  │  2x H100 GPUs            │          │
│  │  128GB VRAM              │  │  │  │  128GB VRAM              │          │
│  │  NVLink interconnect     │  │  │  │  NVLink interconnect     │          │
│  │                          │  │  │  │                          │          │
│  │  Output: KV Cache        │  │  │  │  Output: KV Cache        │          │
│  │  Speed: ~1500 tok/s      │  │  │  │  Speed: ~800 tok/s       │          │
│  └──────────┬───────────────┘  │  │  └──────────┬───────────────┘          │
└─────────────┼──────────────────┘  └─────────────┼──────────────────────────┘
              │                                    │
              │ ConnectX-7 (200Gb/s)              │ ConnectX-7 (200Gb/s)
              │                                    │
┌─────────────▼──────────────────┐  ┌─────────────▼──────────────────────────┐
│    DECODE CLUSTER (Mac)        │  │     DECODE CLUSTER (Mac)               │
│                                 │  │                                         │
│  ┌──────────────────────────┐  │  │  ┌──────────────────────────┐          │
│  │  Mac Studio 2            │  │  │  │  Mac Studio 1            │          │
│  │  169.254.150.102:8001    │  │  │  │  169.254.150.101:8001    │          │
│  │                          │  │  │  │                          │          │
│  │  Flask Decode Server     │  │  │  │  Flask Decode Server     │          │
│  │  ↓                       │  │  │  │  ↓                       │          │
│  │  Ollama                  │  │  │  │  Ollama                  │          │
│  │  ↓                       │  │  │  │  ↓                       │          │
│  │  Qwen 3.0 Coder 30B      │  │  │  │  GPT-OSS 120B            │          │
│  │  (Q8 quantized)          │  │  │  │  (Q8 quantized)          │          │
│  │  ↓                       │  │  │  │  ↓                       │          │
│  │  M4 Max (16-core)        │  │  │  │  M3 Ultra (24-core)      │          │
│  │  128GB Unified Memory    │  │  │  │  512GB Unified Memory    │          │
│  │  MLX optimized           │  │  │  │  MLX optimized           │          │
│  │                          │  │  │  │                          │          │
│  │  Output: Generated Text  │  │  │  │  Output: Generated Text  │          │
│  │  Speed: ~60 tok/s        │  │  │  │  Speed: ~25 tok/s        │          │
│  └──────────┬───────────────┘  │  │  └──────────┬───────────────┘          │
└─────────────┼──────────────────┘  └─────────────┼──────────────────────────┘
              │                                    │
              └────────────────┬───────────────────┘
                               │
                               ▼
                    ┌──────────────────────┐
                    │  Response Aggregation │
                    │  • Combine results    │
                    │  • Merge metrics      │
                    │  • Calculate speedup  │
                    └──────────────────────┘
```

## 2. Data Flow Timeline

```
TIME →

Request Initiation (t=0s)
│
├─ Qwen Request ────────────────────────────────────────────────────────┐
│  "Analyze this code..."                                               │
│                                                                        │
│  Prefill Phase (DGX Spark 1)                                         │
│  ├─ Tokenize prompt (0.1s)                                           │
│  ├─ Forward pass through layers (0.7s)                               │
│  ├─ Generate KV cache (0.1s)                                         │
│  └─ Return context (0.1s)                                            │
│  Total: 1.0s @ 1500 tok/s                                            │
│                                                                        │
│  Network Transfer (ConnectX-7)                                        │
│  └─ KV cache to Mac Studio 2 (0.05s)                                 │
│                                                                        │
│  Decode Phase (Mac Studio 2)                                         │
│  ├─ Load KV cache (0.2s)                                             │
│  ├─ Generate token 1 (0.017s)                                        │
│  ├─ Generate token 2 (0.017s)                                        │
│  ├─ ... (500 tokens)                                                 │
│  └─ Return complete text (8.5s)                                      │
│  Total: 8.5s @ 60 tok/s                                              │
│                                                                        │
│  Complete: 9.6s ◄────────────────────────────────────────────────────┘
│
│
├─ GPT-OSS Request ─────────────────────────────────────────────────────┐
│  "Generate feedback..."                                               │
│                                                                        │
│  Prefill Phase (DGX Spark 2)                                         │
│  ├─ Tokenize prompt (0.1s)                                           │
│  ├─ Forward pass through layers (1.8s)                               │
│  ├─ Generate KV cache (0.1s)                                         │
│  └─ Return context (0.1s)                                            │
│  Total: 2.1s @ 800 tok/s                                             │
│                                                                        │
│  Network Transfer (ConnectX-7)                                        │
│  └─ KV cache to Mac Studio 1 (0.08s)                                 │
│                                                                        │
│  Decode Phase (Mac Studio 1)                                         │
│  ├─ Load KV cache (0.3s)                                             │
│  ├─ Generate token 1 (0.04s)                                         │
│  ├─ Generate token 2 (0.04s)                                         │
│  ├─ ... (500 tokens)                                                 │
│  └─ Return complete text (20.0s)                                     │
│  Total: 20.0s @ 25 tok/s                                             │
│                                                                        │
│  Complete: 22.3s ◄───────────────────────────────────────────────────┘
│
│
Response Aggregation (t=22.3s)
└─ Both models complete
   Total wall time: 22.3s (limited by slower model)
   vs Sequential: 31.9s (sum of both)
   Speedup: 1.43x

```

## 3. Network Topology

```
                    ┌─────────────────────────────────┐
                    │   ConnectX-7 Switch             │
                    │   200 Gb/s (25 GB/s)            │
                    │   RDMA-capable                  │
                    └──┬────────────────────────────┬─┘
                       │                            │
         ┌─────────────┴──────────┐    ┌───────────┴────────────┐
         │                        │    │                        │
    ┌────▼─────┐            ┌────▼─────┐                       │
    │ DGX #1   │            │ DGX #2   │                       │
    │ .103     │            │ .104     │                       │
    │ Qwen     │            │ GPT-OSS  │                       │
    │ Prefill  │            │ Prefill  │                       │
    └──────────┘            └──────────┘                       │
                                                                │
                                                                │
                    ┌───────────────────────────────────────────┘
                    │
                    │ Thunderbolt Bridge
                    │
         ┌──────────┴───────────┐
         │                      │
    ┌────▼─────┐          ┌────▼─────┐
    │ Mac #1   │◄────────►│ Mac #2   │
    │ .101     │          │ .102     │
    │ GPT-OSS  │ Thunder- │ Qwen     │
    │ Decode   │ bolt 4   │ Decode   │
    │          │ 40Gb/s   │          │
    └──────────┘          └──────────┘
         │                      │
         └──────────┬───────────┘
                    │
              Orchestrator
           (runs on Mac #1)
```

## 4. Request Flow Sequence

```
┌─────────┐     ┌──────────────┐     ┌─────────┐     ┌─────────┐
│ Client  │     │ Orchestrator │     │ DGX     │     │ Mac     │
└────┬────┘     └──────┬───────┘     └────┬────┘     └────┬────┘
     │                 │                   │               │
     │ generate()      │                   │               │
     ├────────────────►│                   │               │
     │                 │                   │               │
     │                 │ POST /prefill     │               │
     │                 ├──────────────────►│               │
     │                 │                   │               │
     │                 │                   │ Tokenize      │
     │                 │                   │ Forward pass  │
     │                 │                   │ Gen KV cache  │
     │                 │                   │               │
     │                 │ KV cache + metrics│               │
     │                 │◄──────────────────┤               │
     │                 │                   │               │
     │                 │ POST /decode      │               │
     │                 │ (with KV cache)   │               │
     │                 ├───────────────────────────────────►│
     │                 │                   │               │
     │                 │                   │               │ Load cache
     │                 │                   │               │ Generate
     │                 │                   │               │ tokens
     │                 │                   │               │
     │                 │ Generated text + metrics          │
     │                 │◄───────────────────────────────────┤
     │                 │                   │               │
     │ response +      │                   │               │
     │ metrics         │                   │               │
     │◄────────────────┤                   │               │
     │                 │                   │               │
```

## 5. Parallel Execution Pattern

```
SEQUENTIAL EXECUTION (Old Way):
═══════════════════════════════════════════════════════════════

Thread 1:  [Qwen: 10s]────────────────────────────────────────┐
                                                               │
Thread 1:                              [GPT-OSS: 22s]─────────┤
                                                               │
                                                               ▼
                                                    Total: 32s


PARALLEL EXECUTION (Disaggregated):
═══════════════════════════════════════════════════════════════

Thread 1:  [Qwen: 10s]────────────────────────────────────────┐
           DGX1→Mac2                                           │
                                                               ├─► Merge
Thread 2:  [GPT-OSS: 22s]─────────────────────────────────────┤
           DGX2→Mac1                                           │
                                                               ▼
                                                    Total: 22s

SPEEDUP: 32s / 22s = 1.45x
```

## 6. Hardware Resource Utilization

```
DGX SPARK 1 (Qwen Prefill):
┌────────────────────────────────────────────────────────────┐
│ GPU 0 ████████████████████░░░░  85%  50GB / 64GB          │
│ GPU 1 ████████████████████░░░░  85%  50GB / 64GB          │
│                                                            │
│ NVLink: ████████████████████████  900 GB/s                │
│ Power:  ████████████░░░░░░░░░░░░  1.0 kW / 1.5 kW         │
└────────────────────────────────────────────────────────────┘

MAC STUDIO 1 (GPT-OSS Decode - M3 Ultra):
┌────────────────────────────────────────────────────────────┐
│ CPU:    ████████████████░░░░░░░░  65%  (24 cores)         │
│ GPU:    ██████████████████░░░░░░  70%  (80 cores)         │
│ Memory: ████████████████░░░░░░░░  85GB / 512GB            │
│ Power:  ████████░░░░░░░░░░░░░░░░  180W / 250W             │
└────────────────────────────────────────────────────────────┘

MAC STUDIO 2 (Qwen Decode - M4 Max):
┌────────────────────────────────────────────────────────────┐
│ CPU:    ██████████████████░░░░░░  75%  (16 cores)         │
│ GPU:    ████████████████████░░░░  80%  (40 cores)         │
│ Memory: ████████████░░░░░░░░░░░░  45GB / 128GB            │
│ Power:  ██████░░░░░░░░░░░░░░░░░░  140W / 200W             │
└────────────────────────────────────────────────────────────┘

NETWORK:
┌────────────────────────────────────────────────────────────┐
│ 10GbE:      ████░░░░░░░░░░░░░░░░  1 Gb/s / 10 Gb/s        │
│ ConnectX-7: ██░░░░░░░░░░░░░░░░░░  2 Gb/s / 200 Gb/s       │
│ Thunder 5:  ███░░░░░░░░░░░░░░░░░  3 Gb/s / 120 Gb/s       │
│ Latency:    0.5ms (avg)                                    │
│ Packets:    20K/s                                          │
└────────────────────────────────────────────────────────────┘
```

## 7. Metrics Dashboard Layout

```
┌─────────────────────────────────────────────────────────────────────┐
│                    DISAGGREGATED INFERENCE METRICS                   │
├─────────────────────────────────────────────────────────────────────┤
│                                                                       │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐  │
│  │ Qwen Performance │  │ GPT-OSS Perform. │  │ Combined Metrics │  │
│  ├──────────────────┤  ├──────────────────┤  ├──────────────────┤  │
│  │ Prefill:  0.8s   │  │ Prefill:  2.1s   │  │ Total: 22.3s     │  │
│  │ @ 1500 tok/s     │  │ @ 800 tok/s      │  │                  │  │
│  │                  │  │                  │  │ Speedup: 1.43x   │  │
│  │ Decode:   8.5s   │  │ Decode:  20.0s   │  │                  │  │
│  │ @ 60 tok/s       │  │ @ 25 tok/s       │  │ Throughput:      │  │
│  │                  │  │                  │  │ 45 tok/s avg     │  │
│  │ Total:    9.3s   │  │ Total:   22.1s   │  │                  │  │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘  │
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │ Server Health Status                                            ││
│  ├─────────────────────────────────────────────────────────────────┤│
│  │ ✅ DGX Spark 1 (Qwen Prefill)    - Healthy - 169.254.150.103  ││
│  │ ✅ DGX Spark 2 (GPT-OSS Prefill) - Healthy - 169.254.150.104  ││
│  │ ✅ Mac Studio 1 (GPT-OSS Decode) - Healthy - 169.254.150.101  ││
│  │ ✅ Mac Studio 2 (Qwen Decode)    - Healthy - 169.254.150.102  ││
│  └─────────────────────────────────────────────────────────────────┘│
│                                                                       │
│  ┌─────────────────────────────────────────────────────────────────┐│
│  │ Request History (Last 10)                                       ││
│  ├─────────────────────────────────────────────────────────────────┤│
│  │ #10  Qwen     9.3s   ✅  1500→60 tok/s                         ││
│  │ #9   GPT-OSS  22.1s  ✅  800→25 tok/s                          ││
│  │ #8   Qwen     9.5s   ✅  1480→58 tok/s                         ││
│  │ #7   GPT-OSS  21.8s  ✅  820→26 tok/s                          ││
│  │ #6   Qwen     9.1s   ✅  1520→62 tok/s                         ││
│  └─────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────┘
```

## 8. Failure Modes & Recovery

```
SCENARIO 1: DGX Prefill Server Down
═══════════════════════════════════════════════════════════════

Client Request
      │
      ▼
Orchestrator detects DGX offline
      │
      ├─► Attempt retry (1x)
      │
      ├─► Still offline
      │
      ▼
Fallback to Mac-only inference
      │
      ├─► Mac does full prefill + decode
      │   (slower but functional)
      │
      ▼
Return response with warning
"Using fallback mode - slower performance"


SCENARIO 2: Mac Decode Server Down
═══════════════════════════════════════════════════════════════

Client Request
      │
      ▼
DGX completes prefill successfully
      │
      ▼
Orchestrator attempts decode on Mac
      │
      ├─► Connection timeout
      │
      ├─► Retry (1x)
      │
      ├─► Still offline
      │
      ▼
Return error to client
"Decode server unavailable - request failed"
(No fallback - KV cache not compatible with other servers)


SCENARIO 3: Network Congestion
═══════════════════════════════════════════════════════════════

DGX completes prefill
      │
      ▼
Transfer KV cache to Mac
      │
      ├─► Slow transfer detected (>1s)
      │
      ├─► Log warning
      │
      ├─► Continue with decode
      │
      ▼
Complete request successfully
(Slightly slower but functional)
```

---

**Document Version:** 1.0  
**Last Updated:** November 9, 2025  
**Companion to:** DISAGGREGATED_INFERENCE_SYSTEM_DOCUMENTATION.md
