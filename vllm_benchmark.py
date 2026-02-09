"""
vLLM Concurrent Benchmark — Sparks-only with FP8 models

Sends concurrent requests to vLLM instances on 2x DGX Spark GB10,
measures TTFT (streaming), decode speed, throughput, and concurrent scaling.

Usage:
    # Single server
    python3 vllm_benchmark.py --servers http://169.254.150.106:8000 \
        --model Qwen/Qwen3-Coder-30B-A3B-Instruct-FP8 \
        --prompt-tokens 2500 --max-tokens 500 --iterations 3

    # Concurrent (2 servers)
    python3 vllm_benchmark.py \
        --servers http://169.254.150.106:8000 http://169.254.150.105:8000 \
        --model Qwen/Qwen3-Coder-30B-A3B-Instruct-FP8 \
        --prompt-tokens 2500 --max-tokens 500 --iterations 3 --concurrent 2
"""

import argparse
import json
import os
import statistics
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests


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


def run_streaming_request(server_url, model, messages, max_tokens, request_id=0):
    """Send a streaming request to vLLM and measure timing."""
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0,
        "stream": True,
        "stream_options": {"include_usage": True},
    }

    t_start = time.perf_counter()
    ttft = None
    completion_tokens = 0
    generated_text = ""
    prompt_tokens = 0

    try:
        resp = requests.post(
            f"{server_url}/v1/chat/completions",
            json=payload,
            stream=True,
            timeout=300,
        )
        resp.raise_for_status()

        for line in resp.iter_lines():
            if not line:
                continue
            line = line.decode("utf-8")
            if not line.startswith("data: "):
                continue
            data_str = line[6:]
            if data_str.strip() == "[DONE]":
                break

            chunk = json.loads(data_str)

            # Get usage from final chunk if available
            usage = chunk.get("usage")
            if usage:
                prompt_tokens = usage.get("prompt_tokens", 0)
                completion_tokens = usage.get("completion_tokens", completion_tokens)

            # Extract content delta (choices may be empty in usage-only chunks)
            choices = chunk.get("choices", [])
            if not choices:
                continue
            delta = choices[0].get("delta", {})
            content = delta.get("content", "")
            if content:
                if ttft is None:
                    ttft = time.perf_counter() - t_start
                generated_text += content

        t_end = time.perf_counter()

    except Exception as e:
        t_end = time.perf_counter()
        return {
            "request_id": request_id,
            "server": server_url,
            "error": str(e),
            "total_time": t_end - t_start,
        }

    total_time = t_end - t_start
    decode_time = total_time - (ttft or total_time)

    return {
        "request_id": request_id,
        "server": server_url,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "ttft": ttft,
        "total_time": total_time,
        "decode_time": decode_time,
        "prefill_speed": prompt_tokens / ttft if ttft and ttft > 0 else 0,
        "decode_speed": completion_tokens / decode_time if decode_time > 0 else 0,
        "throughput": (prompt_tokens + completion_tokens) / total_time if total_time > 0 else 0,
        "generated_text_length": len(generated_text),
        "error": None,
    }


def run_non_streaming_request(server_url, model, messages, max_tokens, request_id=0):
    """Fallback: non-streaming request."""
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": 0,
        "stream": False,
    }

    t_start = time.perf_counter()
    try:
        resp = requests.post(
            f"{server_url}/v1/chat/completions",
            json=payload,
            timeout=300,
        )
        resp.raise_for_status()
        result = resp.json()
        t_end = time.perf_counter()

        usage = result.get("usage", {})
        prompt_tokens = usage.get("prompt_tokens", 0)
        completion_tokens = usage.get("completion_tokens", 0)
        text = result["choices"][0]["message"]["content"]

        total_time = t_end - t_start
        return {
            "request_id": request_id,
            "server": server_url,
            "prompt_tokens": prompt_tokens,
            "completion_tokens": completion_tokens,
            "ttft": None,
            "total_time": total_time,
            "decode_time": None,
            "prefill_speed": None,
            "decode_speed": None,
            "throughput": (prompt_tokens + completion_tokens) / total_time if total_time > 0 else 0,
            "generated_text_length": len(text),
            "error": None,
        }
    except Exception as e:
        t_end = time.perf_counter()
        return {
            "request_id": request_id,
            "server": server_url,
            "error": str(e),
            "total_time": t_end - t_start,
        }


def run_concurrent_batch(servers, model, messages, max_tokens, num_concurrent):
    """Send num_concurrent requests distributed across servers."""
    results = []
    with ThreadPoolExecutor(max_workers=num_concurrent) as executor:
        futures = []
        for i in range(num_concurrent):
            server = servers[i % len(servers)]
            futures.append(
                executor.submit(
                    run_streaming_request, server, model, messages, max_tokens, i
                )
            )

        for future in as_completed(futures):
            results.append(future.result())

    results.sort(key=lambda r: r["request_id"])
    return results


def main():
    parser = argparse.ArgumentParser(description="vLLM Concurrent Benchmark")
    parser.add_argument(
        "--servers",
        nargs="+",
        default=["http://169.254.150.106:8000"],
        help="vLLM server URLs",
    )
    parser.add_argument(
        "--model",
        default="Qwen/Qwen3-Coder-30B-A3B-Instruct-FP8",
        help="Model name as registered in vLLM",
    )
    parser.add_argument("--prompt-tokens", type=int, default=2500)
    parser.add_argument("--max-tokens", type=int, default=500)
    parser.add_argument("--iterations", type=int, default=3)
    parser.add_argument(
        "--concurrent",
        type=int,
        default=1,
        help="Number of concurrent requests per iteration",
    )
    parser.add_argument("--output-dir", default="benchmark_results")
    parser.add_argument("--tag", default="", help="Extra tag for output filename")
    args = parser.parse_args()

    print("=" * 70)
    print("vLLM CONCURRENT BENCHMARK")
    print(f"Servers: {', '.join(args.servers)}")
    print(f"Model: {args.model}")
    print(f"Prompt: ~{args.prompt_tokens} tokens  Max output: {args.max_tokens}")
    print(f"Iterations: {args.iterations}  Concurrent: {args.concurrent}")
    print("=" * 70)

    # Health check all servers
    print("\nChecking servers...")
    for server in args.servers:
        try:
            r = requests.get(f"{server}/v1/models", timeout=10)
            models = [m["id"] for m in r.json().get("data", [])]
            print(f"  {server}: ready (models: {models})")
        except Exception as e:
            print(f"  {server}: ERROR - {e}")
            sys.exit(1)

    # Generate prompt
    prompt_text = generate_prompt(args.prompt_tokens)
    messages = [{"role": "user", "content": prompt_text}]

    # Warmup
    print("\nWarmup request...")
    w = run_streaming_request(
        args.servers[0], args.model, messages, 10, request_id=-1
    )
    if w.get("error"):
        print(f"  ERROR: {w['error']}")
        # Try non-streaming fallback
        print("  Trying non-streaming fallback...")
        w = run_non_streaming_request(
            args.servers[0], args.model, messages, 10, request_id=-1
        )
        if w.get("error"):
            print(f"  FATAL: {w['error']}")
            sys.exit(1)
    print(f"  Done: {w.get('prompt_tokens', '?')} prompt tokens")

    # Benchmark
    all_results = []
    print(f"\n--- Benchmark: ~{args.prompt_tokens} tok, {args.max_tokens} max, {args.concurrent} concurrent ---")

    for i in range(args.iterations):
        print(f"\n  Iteration {i + 1}/{args.iterations}...")
        time.sleep(2)  # Cooling between iterations

        if args.concurrent == 1:
            r = run_streaming_request(
                args.servers[0], args.model, messages, args.max_tokens, request_id=0
            )
            batch = [r]
        else:
            batch = run_concurrent_batch(
                args.servers, args.model, messages, args.max_tokens, args.concurrent
            )

        all_results.append(batch)

        # Print per-request results
        for r in batch:
            if r.get("error"):
                print(f"    Req {r['request_id']} ({r['server']}): ERROR {r['error']}")
                continue
            ttft_str = f"{r['ttft']:.3f}s" if r['ttft'] else "N/A"
            print(
                f"    Req {r['request_id']} ({r['server'].split('/')[-1]}): "
                f"TTFT={ttft_str}  "
                f"Prefill={r['prefill_speed']:.0f} tok/s  "
                f"Decode={r['decode_speed']:.1f} tok/s  "
                f"Total={r['total_time']:.3f}s  "
                f"({r['completion_tokens']} tok)"
            )

        # Print batch summary if concurrent
        if args.concurrent > 1:
            ok = [r for r in batch if not r.get("error")]
            if ok:
                batch_wall = max(r["total_time"] for r in ok)
                batch_tokens = sum(r.get("completion_tokens", 0) + r.get("prompt_tokens", 0) for r in ok)
                print(f"    Batch: wall={batch_wall:.3f}s  total_tokens={batch_tokens}  agg_throughput={batch_tokens/batch_wall:.1f} tok/s")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    # Flatten all successful results
    flat = [r for batch in all_results for r in batch if not r.get("error")]
    if not flat:
        print("  No successful results!")
        return

    def safe_stats(values):
        values = [v for v in values if v is not None]
        if not values:
            return {"mean": None, "median": None, "stdev": None, "min": None, "max": None}
        return {
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "stdev": statistics.stdev(values) if len(values) > 1 else 0,
            "min": min(values),
            "max": max(values),
        }

    ttft_stats = safe_stats([r["ttft"] for r in flat])
    decode_stats = safe_stats([r["decode_speed"] for r in flat])
    prefill_stats = safe_stats([r["prefill_speed"] for r in flat])
    total_stats = safe_stats([r["total_time"] for r in flat])
    throughput_stats = safe_stats([r["throughput"] for r in flat])

    print(f"  Requests:       {len(flat)} successful")
    print(f"  Prompt tokens:  {flat[0].get('prompt_tokens', 'N/A')}")
    if ttft_stats["mean"]:
        print(f"  TTFT:           {ttft_stats['mean']:.3f}s (median {ttft_stats['median']:.3f}s)")
    if prefill_stats["mean"]:
        print(f"  Prefill speed:  {prefill_stats['mean']:.0f} tok/s")
    if decode_stats["mean"]:
        print(f"  Decode speed:   {decode_stats['mean']:.1f} tok/s")
    print(f"  Total time:     {total_stats['mean']:.3f}s")
    print(f"  Throughput:     {throughput_stats['mean']:.1f} tok/s (per request)")

    if args.concurrent > 1:
        # Aggregate throughput = total tokens across all concurrent / wall time
        for i, batch in enumerate(all_results):
            ok = [r for r in batch if not r.get("error")]
            if ok:
                wall = max(r["total_time"] for r in ok)
                total_tok = sum(r.get("completion_tokens", 0) + r.get("prompt_tokens", 0) for r in ok)
        # Average across iterations
        walls = []
        agg_throughputs = []
        for batch in all_results:
            ok = [r for r in batch if not r.get("error")]
            if ok:
                wall = max(r["total_time"] for r in ok)
                total_tok = sum(r.get("completion_tokens", 0) + r.get("prompt_tokens", 0) for r in ok)
                walls.append(wall)
                agg_throughputs.append(total_tok / wall)
        if agg_throughputs:
            print(f"  Agg throughput: {statistics.mean(agg_throughputs):.1f} tok/s ({args.concurrent} concurrent)")

    # Save
    os.makedirs(args.output_dir, exist_ok=True)
    model_short = args.model.replace("/", "_").replace("-", "_")
    tag = f"_{args.tag}" if args.tag else ""
    ts = time.strftime("%Y%m%d_%H%M%S")
    out_path = os.path.join(
        args.output_dir,
        f"vllm_{model_short}_c{args.concurrent}{tag}_{ts}.json",
    )

    with open(out_path, "w") as f:
        json.dump(
            {
                "metadata": {
                    "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
                    "type": "vllm_benchmark",
                    "servers": args.servers,
                    "model": args.model,
                    "prompt_tokens_target": args.prompt_tokens,
                    "max_tokens": args.max_tokens,
                    "concurrent": args.concurrent,
                    "iterations": args.iterations,
                },
                "results": [
                    [{k: v for k, v in r.items() if k != "generated_text"}
                     for r in batch]
                    for batch in all_results
                ],
                "summary": {
                    "ttft": ttft_stats,
                    "prefill_speed": prefill_stats,
                    "decode_speed": decode_stats,
                    "total_time": total_stats,
                    "throughput": throughput_stats,
                },
            },
            f,
            indent=2,
        )
    print(f"\n  Saved: {out_path}")


if __name__ == "__main__":
    main()
