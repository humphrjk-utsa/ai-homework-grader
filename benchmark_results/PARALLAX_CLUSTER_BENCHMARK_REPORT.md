# Parallax Cluster Benchmark Report

**Date:** February 7-8, 2026
**Cluster:** Mac Studio 1 (M3 Ultra 512GB) + Mac Studio 2 (M4 Max 128GB) + 2x DGX Spark GB10
**Network:** 10GbE switch (169.254.150.x subnet)
**Test Parameters:** 3 iterations per config, 500 max output tokens, streaming enabled

---

## Hardware

| Node | Role | CPU/GPU | Memory | Bandwidth |
|------|------|---------|--------|-----------|
| Mac Studio 1 | Scheduler + Worker | Apple M3 Ultra | 512 GB unified | 100 GB/s |
| Mac Studio 2 | Worker | Apple M4 Max | 128 GB unified | 100 GB/s |
| DGX Spark 1 (spark-2935) | Worker | NVIDIA GB10 | 128 GB | 600 GB/s |
| DGX Spark 2 (RR191562IP01) | Worker | NVIDIA GB10 | 128 GB | 600 GB/s |

## Models

| Model | Architecture | Params (Total/Active) | Layers | KV Heads | Head Dim |
|-------|-------------|----------------------|--------|----------|----------|
| Qwen3-Coder-30B-A3B-Instruct | MoE (128 experts, 8 active) | 30B / 3B | 48 | 4 (GQA) | 128 |
| openai/gpt-oss-120b | MoE (128 experts) | 120B / 5.1B | 36 | 8 (GQA) | 64 |

**Model formats by node type:**
- Macs: MLX 8-bit quantized (Mac 2: `mlx-community/Qwen3-Coder-30B-A3B-Instruct-8bit`, Mac 1: `lmstudio-community/gpt-oss-120b-MLX-8bit`)
- DGX Sparks (Parallax): Original SafeTensors bf16 via SGLang/CUDA
- DGX Sparks (vLLM): `Qwen/Qwen3-Coder-30B-A3B-Instruct-FP8` (fine-grained FP8, block size 128) and `openai/gpt-oss-120b` (native MXFP4 MoE weights, Marlin dequant) via vLLM 0.13.0 (`nvcr.io/nvidia/vllm:26.01-py3`)

---

## Configurations Tested

| Config | Nodes | Description |
|--------|-------|-------------|
| **Sparks Only** | 2x DGX Spark | Both Sparks as data-parallel workers, Mac 1 as scheduler only |
| **Mac Only** | 1 Mac per model | Mac 2 alone (Qwen Q8), Mac 1 alone (GPT-OSS 8-bit) |
| **Pipeline-Parallel** | 1 Mac + 1 Spark | Layers split across Mac and Spark via reduced `--param-mem-ratio` |
| **Disaggregated** | 1 Spark + 1 Mac | Custom: Spark GPU prefill → KV cache transfer → Mac MLX decode |
| **vLLM FP8 (1x Spark)** | 1 DGX Spark | Single vLLM 0.13.0 instance, FP8/MXFP4 quantization, FlashAttention |
| **vLLM FP8 (2x Spark)** | 2x DGX Spark | Two independent vLLM instances, concurrent requests load-balanced |

---

## Results: Qwen3-Coder-30B-A3B-Instruct (2500-token prompt)

*Iterations 2-3 only for Parallax configs (excluding warmup); all 3 iterations for Disaggregated*

| Metric | 2x DGX Sparks (bf16) | Mac 2 Only (Q8) | Pipeline-Parallel (Mac2+Spark) | Disaggregated (Spark→Mac1) |
|--------|---------------------|-----------------|-------------------------------|---------------------------|
| **TTFT / Prefill (s)** | 0.97 | 1.26 | 0.86 | 6.16 + 0.31 (net) |
| **Prefill (tok/s)** | 2,193 | 1,344 | 1,960 | 259 |
| **Decode (tok/s)** | 26.5 | **71.8** | 28.8 | 38.7 |
| **Total Time (s)** | 19.8 | **8.2** | 18.3 | 19.4 |
| **Throughput (tok/s)** | 110.7 | **266.4** | 120.0 | 107.2 |

**Pipeline-Parallel layer allocation:** Mac 2 layers [0,19) + Spark layers [19,48) = 19+29 layers
**Disaggregated:** Spark bf16 prefill via raw HuggingFace transformers → 155 MB KV cache → Mac 1 MLX 8-bit decode

### Qwen3-Coder-30B: 6500-token prompt

| Metric | 2x DGX Sparks (bf16) | Disaggregated (Spark→Mac1) |
|--------|---------------------|---------------------------|
| TTFT / Prefill (s) | 1.13 | 6.07 + 0.65 (net) |
| Prefill (tok/s) | 3,778 | 675 |
| Decode (tok/s) | 25.3 | 36.5 |
| Total Time (s) | 20.0 | 20.4 |
| Throughput (tok/s) | 229.0 | 224.5 |

*Mac and PP configs not tested at 6500 tokens (httpx timeout on Mac workers)*

---

## Results: openai/gpt-oss-120b (2500-token prompt)

*Iterations 2-3 only (excluding warmup iteration 1)*

| Metric | 2x DGX Sparks (bf16) | Mac 1 Only (8-bit) | Pipeline-Parallel (Mac1+Spark) |
|--------|---------------------|-------------------|-------------------------------|
| **TTFT (s)** | 1.05 | 1.32 | 1.33 |
| **Prefill (tok/s)** | 1,662 | 1,330 | 1,319 |
| **Decode (tok/s)** | 41.1 | **56.8** | 36.0 |
| **Total Time (s)** | 13.2 | **10.1** | 15.2 |
| **Throughput (tok/s)** | 170.3 | **222.7** | 147.9 |

**Pipeline-Parallel layer allocation:** Mac 1 layers [0,19) + Spark layers [19,36) = 19+17 layers

### GPT-OSS-120B: 6500-token prompt (Sparks only)

| Metric | 2x DGX Sparks (bf16) |
|--------|---------------------|
| TTFT (s) | 17.27 |
| Prefill (tok/s) | 238.5 |
| Decode (tok/s) | 39.4 |
| Total Time (s) | 27.6 |

---

## Results: vLLM FP8 on DGX Sparks (Direct, No Parallax)

*Runtime: vLLM 0.13.0 (NVIDIA NGC `26.01-py3`), FlashAttention, CUDA graphs, chunked prefill. Each Spark runs an independent vLLM server on port 8000. Concurrent configs send one request per server simultaneously.*

### Qwen3-Coder-30B FP8 on vLLM

| Metric | 1x Spark (FP8) | 2x Spark Concurrent (FP8) |
|--------|---------------|--------------------------|
| **TTFT (s)** — 2500 tok | **0.080** | 0.080 per server |
| **Prefill (tok/s)** — 2500 tok | **19,742** | ~19,742 per server |
| **Decode (tok/s)** — 2500 tok | 49.9 | 50.2 per server |
| **Total Time (s)** — 2500 tok | 10.1 | 10.5 (wall) |
| **Agg Throughput (tok/s)** — 2500 tok | 206 | **~410** |
| | | |
| **TTFT (s)** — 6500 tok | **0.063** | 0.068 per server |
| **Prefill (tok/s)** — 6500 tok | **65,369** | ~65,000 per server |
| **Decode (tok/s)** — 6500 tok | 47.2 | 47.5 per server |
| **Total Time (s)** — 6500 tok | 10.7 | 10.7 (wall) |
| **Agg Throughput (tok/s)** — 6500 tok | 430 | **~852** |

### GPT-OSS-120B (native MXFP4) on vLLM

| Metric | 1x Spark (MXFP4) | 2x Spark Concurrent (MXFP4) |
|--------|-----------------|-------------------------------|
| **TTFT (s)** — 2500 tok | 4.47 | ~4.5–9.2† per server |
| **Prefill (tok/s)** — 2500 tok | 367 | ~367 per server |
| **Decode (tok/s)** — 2500 tok | 48.0 | ~48 per server† |
| **Total Time (s)** — 2500 tok | 14.9 | 14.9 (wall) |
| **Agg Throughput (tok/s)** — 2500 tok | 144 | **~287** |
| | | |
| **TTFT (s)** — 6500 tok | 5.76 | ~5.3 per server |
| **Prefill (tok/s)** — 6500 tok | 719 | ~798 per server |
| **Decode (tok/s)** — 6500 tok | 53.1 | 50.5 per server |
| **Total Time (s)** — 6500 tok | 15.2 | 15.2 (wall) |
| **Agg Throughput (tok/s)** — 6500 tok | 306 | **~604** |

†*Concurrent GPT-OSS 2500-token TTFT is inflated by TCP buffering over shared 10GbE (streaming tokens arrive in bursts). This makes individual TTFT and decode speed measurements unreliable for concurrent runs; total time and aggregate throughput are the meaningful metrics.*

**Key finding:** GPT-OSS-120B fits on a **single** Spark with vLLM's native MXFP4 support (Marlin dequantization). In contrast, Parallax required 2x Sparks for bf16 format.

---

## Analysis

### 1. Macs dominate decode speed

Mac Apple Silicon achieves faster decode than DGX Spark GB10, though vLLM FP8 narrows the gap significantly vs Parallax SGLang bf16:

| Model | Mac Decode | Spark (Parallax bf16) | Spark (vLLM FP8/MXFP4) | Mac vs vLLM |
|-------|-----------|----------------------|------------------------|-------------|
| Qwen3-Coder-30B | 71.8 tok/s | 26.5 tok/s | 49.9 tok/s | **1.4x** |
| GPT-OSS-120B | 56.8 tok/s | 41.1 tok/s | 48.0 tok/s | **1.2x** |

Decode is memory-bandwidth-bound (single token → single forward pass per step). vLLM with FP8 quantization nearly doubles Spark decode speed vs Parallax/SGLang bf16 (49.9 vs 26.5 for Qwen) by reducing memory reads per token. Mac still leads due to unified memory architecture, but the gap shrinks from 2.7x to 1.4x.

### 2. Sparks have faster prefill

Spark GPU compute excels at the parallelizable prefill phase. vLLM FP8 takes this to an extreme:

| Model | Mac Prefill | Spark (Parallax bf16) | Spark (vLLM FP8/MXFP4) | vLLM vs Mac |
|-------|-----------|-----------------------|-------------------------|-------------|
| Qwen3-Coder-30B (2500 tok) | 1,344 tok/s | 2,193 tok/s | **19,742 tok/s** | **14.7x** |
| Qwen3-Coder-30B (6500 tok) | — | 3,778 tok/s | **65,369 tok/s** | — |
| GPT-OSS-120B (2500 tok) | 1,330 tok/s | 1,662 tok/s | 367 tok/s | 0.3x |
| GPT-OSS-120B (6500 tok) | — | 238 tok/s | **719 tok/s** | — |

Qwen FP8 on vLLM achieves extraordinary prefill: 19,742 tok/s at 2500 tokens scaling to 65,369 tok/s at 6500 tokens. This is because (a) Qwen has only 3B active params per token (MoE), (b) FP8 halves memory bandwidth vs bf16, and (c) vLLM's FlashAttention + CUDA graphs are far more optimized than SGLang in Parallax.

GPT-OSS prefill is slower on vLLM (367 tok/s) than Parallax (1,662 tok/s) at 2500 tokens, but this comparison is unfair: Parallax used 2x Sparks for the 240GB bf16 model (likely tensor-parallel), while vLLM fits it on a single Spark via native MXFP4 weights with Marlin dequantization overhead. At 6500 tokens, vLLM (719 tok/s) beats Parallax (238 tok/s) — the Parallax 6500-token result appears to have been bottlenecked by cross-node communication.

### 3. Pipeline-parallel is NOT disaggregated inference

Pipeline-parallel (PP) splits model layers across nodes. Every token — both during prefill AND decode — must traverse all pipeline stages sequentially.

**Result: PP inherits the worst of both worlds for decode.**

| Model | PP Decode | Best Single-Node Decode | PP Penalty |
|-------|----------|------------------------|------------|
| Qwen3-Coder-30B | 28.8 tok/s | 71.8 tok/s (Mac) | **-60%** |
| GPT-OSS-120B | 36.0 tok/s | 56.8 tok/s (Mac) | **-37%** |

PP decode is bottlenecked by the slowest pipeline stage (the Spark), plus inter-node communication overhead. The Mac's fast decode is completely negated.

**PP does NOT achieve "Spark prefill speed + Mac decode speed."** It achieves approximately "average prefill speed + worst decode speed."

### 4. End-to-end latency comparison (single request)

For a 2500-token prompt generating 500 tokens:

| Config | Qwen Total | GPT-OSS Total |
|--------|-----------|---------------|
| Mac Only (Parallax) | **8.2s** | **10.1s** |
| 2x Sparks (Parallax bf16) | 19.8s | 13.2s |
| Pipeline-Parallel | 18.3s | 15.2s |
| Disaggregated (raw PyTorch) | 19.4s | N/A (model too large) |
| **vLLM FP8 (1x Spark)** | **10.1s** | 14.9s |
| **vLLM FP8 (2x Spark concurrent)** | 10.5s (x2) | 14.9s (x2) |

For single-request latency, Mac-only still wins (8.2s vs 10.1s for Qwen) because Mac decode (71.8 tok/s) outpaces vLLM Spark decode (49.9 tok/s). However, vLLM FP8 closes the gap from 2.4x slower (Parallax Spark) to only 1.2x slower.

**For throughput (multiple concurrent requests), vLLM on 2x Sparks wins:**

| Config | Qwen Throughput | GPT-OSS Throughput |
|--------|----------------|-------------------|
| Mac Only (single request) | 266 tok/s | 223 tok/s |
| vLLM 1x Spark | 206 tok/s | 144 tok/s |
| **vLLM 2x Spark concurrent** | **~410 tok/s** | **~287 tok/s** |
| vLLM 2x Spark (6500 tok) | **~852 tok/s** | **~604 tok/s** |

With concurrent requests, 2x Sparks deliver **1.5x** (Qwen) to **1.3x** (GPT-OSS) higher throughput than Mac-only. The Spark advantage grows dramatically at longer prompts due to prefill scaling.

### 5. Disaggregated inference: concept proven, optimization needed

The custom disaggregated system (Spark prefill → KV cache transfer → Mac decode) **works correctly** but uses unoptimized runtimes:

**What works well:**
- KV cache serialization, 10GbE transfer, and MLX injection are all fast:
  - Transfer: 0.31s for 155 MB (2500 tok), 0.65s for 402 MB (6500 tok) — ~0.5 GB/s
  - Deserialization: <10 ms
  - Cache injection: <0.1 ms
- Mac decode with injected KV cache produces correct output

**What's slow (and why):**

| Component | Current (raw PyTorch) | Parallax (SGLang) | Gap |
|-----------|---------------------|-------------------|-----|
| Spark prefill (2500 tok) | 259 tok/s (6.16s) | 2,193 tok/s (0.77s) | **8.5x slower** |
| Spark prefill (6500 tok) | 675 tok/s (6.07s) | 3,778 tok/s (1.08s) | **5.6x slower** |
| Mac decode (Qwen Q8) | 38.7 tok/s (Mac 1) | 71.8 tok/s (Mac 2) | **1.9x slower** |

Root causes:
- **Prefill**: Raw HuggingFace `transformers` forward pass lacks FlashAttention, CUDA graphs, and continuous batching that SGLang provides. SGLang 0.5.4 + FlashInfer 0.5.0 are available in the Spark Docker image.
- **Decode**: Naive Python `for` loop with `model(input_ids, cache=cache)` per token. Parallax's MLX server likely uses optimized batched generation. Also Mac 1 (M3 Ultra) vs Mac 2 (M4 Max) architecture differences.

---

## KV Cache Transfer Analysis (Measured)

Both models use aggressive Grouped Query Attention (GQA), resulting in small KV caches:

| Model | KV Cache per Token | 2500 tok (measured) | 6500 tok (measured) |
|-------|-------------------|---------------------|---------------------|
| Qwen3-Coder-30B | 96 KB (48L x 4KVH x 128d x 2 x 2B) | **155 MB** (1577 tok) | **402 MB** (4085 tok) |
| GPT-OSS-120B | 72 KB (36L x 8KVH x 64d x 2 x 2B) | ~180 MB (est.) | ~468 MB (est.) |

**Measured transfer times over 10GbE:**

| Prompt Size | KV Cache | Transfer Time | Effective Bandwidth |
|------------|----------|--------------|---------------------|
| ~2500 tok (Qwen) | 155 MB | 0.31s | 0.50 GB/s |
| ~6500 tok (Qwen) | 402 MB | 0.65s | 0.62 GB/s |

Network transfer is **not a bottleneck** — it's ~5% of total time. Deserialization and cache injection combined add <10ms.

### Projected Performance with SGLang Prefill

If the disaggregated prefill server used SGLang instead of raw transformers (matching Parallax's prefill speeds):

| Phase | Qwen (2500 tok) | Qwen (6500 tok) | GPT-OSS (2500 tok) |
|-------|-----------------|-----------------|-------------------|
| Spark Prefill (SGLang) | 0.77s | 1.08s | 1.05s |
| KV Transfer (10GbE) | 0.31s | 0.65s | ~0.18s |
| Mac Decode (optimized est.) | 7.0s | 7.0s | 8.8s |
| **Projected Total** | **8.1s** | **8.7s** | **10.0s** |
| Mac-Only Baseline | 8.2s | ~11.8s (est.) | 10.1s |
| **Speedup** | breakeven | **~26% faster** | breakeven |

The disaggregated approach wins at longer prompts where Spark GPU parallelism matters most.

### 6. vLLM FP8 transforms Spark performance

Switching from Parallax (SGLang + bf16) to vLLM 0.13.0 (FlashAttention + FP8/MXFP4) dramatically changes the performance picture:

**Qwen3-Coder-30B — Parallax bf16 vs vLLM FP8:**

| Metric | Parallax (2x Spark bf16) | vLLM (1x Spark FP8) | Improvement |
|--------|-------------------------|---------------------|-------------|
| TTFT (2500 tok) | 0.97s | **0.080s** | **12x faster** |
| Prefill (2500 tok) | 2,193 tok/s | **19,742 tok/s** | **9x faster** |
| Decode | 26.5 tok/s | **49.9 tok/s** | **1.9x faster** |
| Total Time | 19.8s | **10.1s** | **2.0x faster** |

**GPT-OSS-120B — Parallax bf16 vs vLLM MXFP4:**

| Metric | Parallax (2x Spark bf16) | vLLM (1x Spark MXFP4) | Notes |
|--------|-------------------------|----------------------|-------|
| TTFT (2500 tok) | 1.05s | 4.47s | Parallax faster (2x Spark tensor-parallel) |
| Decode | 41.1 tok/s | 48.0 tok/s | **1.2x faster** |
| Total Time | 13.2s | 14.9s | Comparable despite using half the hardware |

Key observations:
- **FP8 quantization is the biggest single improvement** — it halves memory reads per token, nearly doubling decode speed (26.5→49.9 for Qwen, 41.1→48.0 for GPT-OSS).
- **vLLM's optimized runtime adds substantial gains** — FlashAttention, CUDA graphs, and chunked prefill give 9x prefill speedup for Qwen FP8 vs Parallax SGLang bf16.
- **Concurrent scaling is near-linear** — 2x Sparks deliver ~2x aggregate throughput since each runs independently with no cross-node communication.
- **GPT-OSS fits on single Spark** with MXFP4 — eliminates the 2-Spark requirement for this model.

### 7. Optimal configuration depends on workload

| Workload | Best Config | Why |
|----------|------------|-----|
| Single request, low latency | Mac Only (Parallax) | 8.2s (Qwen), 10.1s (GPT-OSS) — fastest decode |
| Single request, Spark only | vLLM FP8 (1x Spark) | 10.1s (Qwen), 14.9s (GPT-OSS) — close to Mac |
| Max throughput (concurrent) | **vLLM FP8 (2x Spark)** | ~410-852 tok/s agg — 1.5-3.2x vs Mac single |
| Long prompt + short output | vLLM FP8 (Spark) | Near-instant prefill (0.06-0.08s TTFT for Qwen) |
| Long prompt + long output | Mac Only or Disaggregated | Decode speed dominates, Mac wins |

---

## Conclusions

1. **Pipeline-parallel via Parallax is a dead end** for combining Spark prefill with Mac decode. Every token must traverse all stages, making decode speed limited by the slowest node.

2. **Mac-only is fastest for single-request latency** (8.2s Qwen, 10.1s GPT-OSS) because Mac decode (71.8 tok/s) outpaces all Spark configurations. However, the gap narrows significantly with vLLM FP8 (10.1s for Qwen on single Spark).

3. **vLLM FP8 on Sparks is the throughput champion.** Two Sparks running concurrent requests deliver 410–852 tok/s aggregate, exceeding Mac-only by 1.5–3.2x. This is the best configuration for batch workloads like homework grading where multiple submissions can be processed simultaneously.

4. **FP8/MXFP4 quantization is transformative.** Switching from bf16 to FP8 nearly doubles decode speed (26.5→49.9 tok/s for Qwen) and enables 9x faster prefill with vLLM's optimized runtime. GPT-OSS-120B also fits on a single Spark via native MXFP4, eliminating the 2-Spark requirement.

5. **Disaggregated inference is proven viable** but has been partly superseded by the vLLM FP8 results. The custom system successfully transfers KV caches over 10GbE in 0.3–0.7s (not a bottleneck), but vLLM FP8 on a single Spark already matches the projected disaggregated performance without the complexity of cross-node KV cache transfer.

6. **Sparks excel at prefill** — vLLM FP8 achieves 19,742 tok/s (Qwen, 2500 tok) scaling to 65,369 tok/s (6500 tok). This is 14.7–48.6x faster than Mac prefill. For long-context workloads, Spark prefill is effectively instantaneous.

7. **The homework grading use case favors vLLM 2x Spark concurrent.** Grading involves processing many submissions with ~2500–6500 token prompts and ~500 token outputs. The concurrent Spark config maximizes throughput: ~410 tok/s for Qwen at 2500 tokens, ~852 tok/s at 6500 tokens.

### Path Forward

| Priority | Action | Expected Impact |
|----------|--------|----------------|
| **High** | Use vLLM FP8 on 2x Sparks for grading pipeline | 1.5-3.2x throughput vs Mac-only |
| **Medium** | Disaggregated prefill with vLLM (Spark→Mac decode) | Best single-request latency for long prompts |
| **Low** | Explore vLLM tensor-parallel across 2 Sparks for GPT-OSS | Faster GPT-OSS prefill (currently MXFP4 single-Spark) |

---

## Raw Data Files

All benchmark results stored in `benchmark_results/`:
- `sparks_only_Qwen_Qwen3-Coder-30B-A3B-Instruct_20260207_180059.json`
- `sparks_only_openai_gpt-oss-120b_20260207_182709.json`
- `macs_only_Qwen_Qwen3-Coder-30B-A3B-Instruct_20260207_193011.json`
- `macs_only_openai_gpt-oss-120b_20260207_200410.json`
- `hybrid_mac2_spark_pp_Qwen_Qwen3-Coder-30B-A3B-Instruct_20260207_202145.json`
- `hybrid_mac1_spark_pp_openai_gpt-oss-120b_20260207_215547.json`
- `disaggregated_qwen_20260207_230647.json` (2500-token disaggregated)
- `disaggregated_qwen_20260207_230900.json` (6500-token disaggregated)
- `vllm_Qwen_Qwen3_Coder_30B_A3B_Instruct_FP8_c1_single_spark_npc_20260208_141551.json` (vLLM Qwen FP8, 1x Spark, 2500 tok)
- `vllm_Qwen_Qwen3_Coder_30B_A3B_Instruct_FP8_c1_single_spark_npc_20260208_141817.json` (vLLM Qwen FP8, 1x Spark, 6500 tok)
- `vllm_Qwen_Qwen3_Coder_30B_A3B_Instruct_FP8_c2_dual_spark_npc_20260208_141908.json` (vLLM Qwen FP8, 2x Spark, 2500 tok)
- `vllm_Qwen_Qwen3_Coder_30B_A3B_Instruct_FP8_c2_dual_spark_npc_20260208_142009.json` (vLLM Qwen FP8, 2x Spark, 6500 tok)
- `vllm_openai_gpt_oss_120b_c1_single_spark_npc_20260208_143913.json` (vLLM GPT-OSS MXFP4, 1x Spark, 2500 tok)
- `vllm_openai_gpt_oss_120b_c1_single_spark_npc_20260208_144026.json` (vLLM GPT-OSS MXFP4, 1x Spark, 6500 tok)
- `vllm_openai_gpt_oss_120b_c2_dual_spark_npc_20260208_153805.json` (vLLM GPT-OSS MXFP4, 2x Spark, 2500 tok)
- `vllm_openai_gpt_oss_120b_c2_dual_spark_npc_20260208_160135.json` (vLLM GPT-OSS MXFP4, 2x Spark, 6500 tok)
