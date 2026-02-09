"""
Disaggregated Inference Client — runs on Mac
Sends prompt to DGX Spark for prefill (CUDA), receives KV cache,
runs autoregressive decode locally on Mac (MLX).

Combines Spark GPU prefill speed with Mac memory-bandwidth decode speed.

Usage:
    python3 disaggregated_inference.py \
        --prefill-url http://169.254.150.106:8800 \
        --model mlx-community/Qwen3-Coder-30B-A3B-Instruct-8bit \
        --prompt-tokens 2500 --max-tokens 500 --iterations 3
"""

import argparse
import json
import os
import struct
import sys
import time

import mlx.core as mx
import numpy as np
import requests

from mlx_lm import load as mlx_load
from mlx_lm.models.cache import KVCache, make_prompt_cache


def generate_prompt(target_tokens, chars_per_token=4):
    """Generate a substantive prompt targeting a specific token count."""
    base = (
        "You are a senior software engineer. Analyze the following codebase "
        "and provide detailed recommendations for improvement.\n\n"
    )
    filler_block = (
        "The system processes incoming data through a multi-stage pipeline. "
        "First, raw inputs are validated against a schema definition that "
        "enforces type constraints and range limits. Valid records proceed to "
        "a transformation layer where business rules normalize values, compute "
        "derived fields, and flag anomalies. The transformation output feeds "
        "into an aggregation engine that groups records by configurable "
        "dimensions and computes statistical summaries. Results are cached in "
        "a distributed store with TTL-based expiration. A separate monitoring "
        "service polls the pipeline stages for throughput metrics and latency "
        "percentiles, triggering alerts when thresholds are breached. "
    )
    target_chars = target_tokens * chars_per_token
    prompt = base
    while len(prompt) < target_chars:
        prompt += filler_block
    return prompt[:target_chars]


def deserialize_kv_cache(response_bytes):
    """Deserialize KV cache from prefill server binary response."""
    meta_len = struct.unpack("<I", response_bytes[:4])[0]
    metadata = json.loads(response_bytes[4 : 4 + meta_len])
    kv_bytes = response_bytes[4 + meta_len :]

    num_layers = metadata["num_layers"]
    seq_len = metadata["seq_len"]
    num_kv_heads = metadata["num_kv_heads"]
    head_dim_k = metadata["head_dim_k"]
    head_dim_v = metadata["head_dim_v"]

    k_size = 1 * num_kv_heads * seq_len * head_dim_k * 2  # float16 = 2 bytes
    v_size = 1 * num_kv_heads * seq_len * head_dim_v * 2

    offset = 0
    kv_pairs = []
    for _ in range(num_layers):
        k = np.frombuffer(kv_bytes[offset : offset + k_size], dtype=np.float16)
        k = k.reshape(1, num_kv_heads, seq_len, head_dim_k)
        offset += k_size

        v = np.frombuffer(kv_bytes[offset : offset + v_size], dtype=np.float16)
        v = v.reshape(1, num_kv_heads, seq_len, head_dim_v)
        offset += v_size

        kv_pairs.append((mx.array(k), mx.array(v)))

    return metadata, kv_pairs


def run_disaggregated(
    prompt_text, model, tokenizer, prefill_url, max_tokens=500, messages=None
):
    """
    Run disaggregated inference: Spark prefill + Mac decode.
    Returns detailed timing breakdown.
    """
    # Phase 1: Send to Spark for prefill
    t_start = time.perf_counter()

    if messages is not None:
        payload = {"messages": messages}
    else:
        payload = {"prompt": prompt_text}

    resp = requests.post(f"{prefill_url}/prefill", json=payload, timeout=300)
    resp.raise_for_status()
    t_received = time.perf_counter()

    # Phase 2: Deserialize KV cache into MLX arrays
    metadata, kv_pairs = deserialize_kv_cache(resp.content)
    t_deserialized = time.perf_counter()

    # Phase 3: Inject into MLX cache
    cache = make_prompt_cache(model)
    for layer_idx, (keys, values) in enumerate(kv_pairs):
        cache[layer_idx].state = (keys, values)
    # Force materialization so decode timing is clean
    mx.eval(*[c.state[0] for c in cache], *[c.state[1] for c in cache])
    t_cache_ready = time.perf_counter()

    # Phase 4: Autoregressive decode on Mac
    next_token = metadata["next_token"]
    tokens = [next_token]

    # Collect EOS tokens for stopping
    eos_tokens = set()
    if hasattr(tokenizer, "eos_token_id"):
        if isinstance(tokenizer.eos_token_id, list):
            eos_tokens = set(tokenizer.eos_token_id)
        elif tokenizer.eos_token_id is not None:
            eos_tokens = {tokenizer.eos_token_id}
    for tok_str in ["<|im_end|>", "<|endoftext|>"]:
        tid = tokenizer.convert_tokens_to_ids(tok_str)
        if tid is not None and tid != tokenizer.unk_token_id:
            eos_tokens.add(tid)

    t_decode_start = time.perf_counter()

    for _ in range(max_tokens - 1):
        input_ids = mx.array([[next_token]])
        logits = model(input_ids, cache=cache)
        mx.eval(logits)
        next_token = mx.argmax(logits[:, -1, :], axis=-1).item()
        tokens.append(next_token)
        if next_token in eos_tokens:
            break

    t_end = time.perf_counter()

    # Compute metrics
    prompt_tokens = metadata["prompt_tokens"]
    completion_tokens = len(tokens)
    spark_prefill_time = metadata["prefill_time"]
    total_request_time = t_received - t_start
    network_time = total_request_time - spark_prefill_time
    kv_size_mb = metadata["kv_bytes_len"] / 1e6

    return {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "spark_prefill_time": spark_prefill_time,
        "network_transfer_time": network_time,
        "kv_size_mb": kv_size_mb,
        "deserialize_time": t_deserialized - t_received,
        "cache_inject_time": t_cache_ready - t_deserialized,
        "decode_time": t_end - t_decode_start,
        "total_time": t_end - t_start,
        "prefill_speed": prompt_tokens / spark_prefill_time if spark_prefill_time > 0 else 0,
        "decode_speed": completion_tokens / (t_end - t_decode_start) if (t_end - t_decode_start) > 0 else 0,
        "effective_transfer_gbps": (kv_size_mb / 1000) / network_time if network_time > 0 else 0,
        "throughput": (prompt_tokens + completion_tokens) / (t_end - t_start) if (t_end - t_start) > 0 else 0,
        "generated_text": tokenizer.decode(tokens),
    }


def main():
    parser = argparse.ArgumentParser(description="Disaggregated Inference Benchmark")
    parser.add_argument("--prefill-url", default="http://169.254.150.106:8800")
    parser.add_argument("--model", default="mlx-community/Qwen3-Coder-30B-A3B-Instruct-8bit")
    parser.add_argument("--prompt-tokens", type=int, default=2500)
    parser.add_argument("--max-tokens", type=int, default=500)
    parser.add_argument("--iterations", type=int, default=3)
    parser.add_argument("--output-dir", default="benchmark_results")
    args = parser.parse_args()

    print("=" * 70)
    print("DISAGGREGATED INFERENCE BENCHMARK")
    print(f"Prefill: DGX Spark @ {args.prefill_url}")
    print(f"Decode:  Mac MLX ({args.model})")
    print(f"Prompt: ~{args.prompt_tokens} tokens  Max output: {args.max_tokens}")
    print(f"Iterations: {args.iterations}")
    print("=" * 70)

    # Check prefill server
    print("\nChecking prefill server...")
    try:
        r = requests.get(f"{args.prefill_url}/health", timeout=10)
        print(f"  Server ready: {r.json()}")
    except Exception as e:
        print(f"  ERROR: Prefill server not reachable: {e}")
        sys.exit(1)

    # Load MLX model
    print(f"\nLoading MLX model: {args.model}")
    t0 = time.time()
    model, tokenizer = mlx_load(args.model)
    print(f"  Loaded in {time.time() - t0:.1f}s")

    # Generate prompt
    prompt_text = generate_prompt(args.prompt_tokens)
    messages = [{"role": "user", "content": prompt_text}]

    # Warmup
    print("\nWarmup request...")
    w = run_disaggregated(
        prompt_text, model, tokenizer, args.prefill_url,
        max_tokens=10, messages=messages,
    )
    print(f"  Done: {w['prompt_tokens']}p tokens, prefill {w['spark_prefill_time']:.2f}s")

    # Benchmark
    results = []
    print(f"\n--- ~{args.prompt_tokens} tokens, {args.max_tokens} max output ---")

    for i in range(args.iterations):
        print(f"\n  Iteration {i + 1}/{args.iterations}...")
        r = run_disaggregated(
            prompt_text, model, tokenizer, args.prefill_url,
            max_tokens=args.max_tokens, messages=messages,
        )
        results.append(r)

        print(f"    Spark prefill:  {r['spark_prefill_time']:.3f}s  ({r['prefill_speed']:.0f} tok/s)")
        print(f"    Network xfer:   {r['network_transfer_time']:.3f}s  ({r['kv_size_mb']:.0f}MB @ {r['effective_transfer_gbps']:.2f} GB/s)")
        print(f"    Deserialize:    {r['deserialize_time']:.3f}s")
        print(f"    Cache inject:   {r['cache_inject_time']:.3f}s")
        print(f"    Mac decode:     {r['decode_time']:.3f}s  ({r['decode_speed']:.1f} tok/s, {r['completion_tokens']} tok)")
        print(f"    TOTAL:          {r['total_time']:.3f}s  ({r['throughput']:.1f} tok/s)")

    # Summary
    avg = lambda k: sum(r[k] for r in results) / len(results)
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"  Prompt tokens:     {results[0]['prompt_tokens']}")
    print(f"  Completion tokens: {avg('completion_tokens'):.0f}")
    print(f"  Spark prefill:     {avg('spark_prefill_time'):.3f}s  ({avg('prefill_speed'):.0f} tok/s)")
    print(f"  Network transfer:  {avg('network_transfer_time'):.3f}s  ({avg('kv_size_mb'):.0f}MB)")
    print(f"  Mac decode:        {avg('decode_time'):.3f}s  ({avg('decode_speed'):.1f} tok/s)")
    print(f"  Total:             {avg('total_time'):.3f}s")
    print(f"  Throughput:        {avg('throughput'):.1f} tok/s")

    # Save
    os.makedirs(args.output_dir, exist_ok=True)
    ts = time.strftime("%Y%m%d_%H%M%S")
    out_path = os.path.join(args.output_dir, f"disaggregated_qwen_{ts}.json")
    with open(out_path, "w") as f:
        json.dump({
            "metadata": {
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "type": "disaggregated",
                "prefill_server": args.prefill_url,
                "decode_model": args.model,
                "prompt_tokens_target": args.prompt_tokens,
                "max_tokens": args.max_tokens,
            },
            "results": [{k: v for k, v in r.items() if k != "generated_text"} for r in results],
            "summary": {k: avg(k) for k in ["spark_prefill_time", "network_transfer_time", "decode_time", "total_time", "prefill_speed", "decode_speed", "throughput"]},
        }, f, indent=2)
    print(f"\n  Saved: {out_path}")


if __name__ == "__main__":
    main()
