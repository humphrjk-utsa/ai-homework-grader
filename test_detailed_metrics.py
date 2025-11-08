#!/usr/bin/env python3
"""
Test disaggregated inference with detailed Ollama-style metrics
"""
from disaggregated_client import DisaggregatedClient
from model_config import MODEL_SETTINGS
import json

print("\n" + "="*80)
print("DISAGGREGATED INFERENCE - DETAILED PERFORMANCE METRICS")
print("="*80)

# Test with Qwen model
model_name = "disaggregated:qwen3-coder:30b"
config = MODEL_SETTINGS[model_name]

print(f"\nModel: {model_name}")
print(f"Prefill Server: {config['prefill_url']}")
print(f"Decode Server: {config['decode_url']}")

client = DisaggregatedClient(
    prefill_url=config['prefill_url'],
    decode_url=config['decode_url']
)

prompt = "Write a Python function to calculate the factorial of a number:"

print("\n" + "="*80)
print("GENERATING...")
print("="*80)

result = client.generate(
    prompt=prompt,
    max_tokens=200,
    temperature=0.3
)

print("\n" + "="*80)
print("PERFORMANCE METRICS (Ollama-style)")
print("="*80)

metrics = result.get('metrics', {})

print("\n📊 PREFILL PHASE (DGX Spark 1)")
print("-" * 80)
prefill = metrics.get('prefill', {})
print(f"  Time:              {prefill.get('time_s', 0):.4f} seconds")
print(f"  Prompt Tokens:     {prefill.get('prompt_tokens', 0)}")
print(f"  Speed:             {prefill.get('tokens_per_sec', 0):.1f} tokens/sec")
print(f"  Duration (ns):     {prefill.get('duration_ns', 0):,}")

print("\n📊 DECODE PHASE (Mac Studio 2)")
print("-" * 80)
decode = metrics.get('decode', {})
print(f"  Time:              {decode.get('time_s', 0):.4f} seconds")
print(f"  Tokens Generated:  {decode.get('tokens_generated', 0)}")
print(f"  Speed:             {decode.get('tokens_per_sec', 0):.1f} tokens/sec")
print(f"  Eval Duration:     {decode.get('eval_duration_ns', 0):,} ns")
print(f"  Total Duration:    {decode.get('total_duration_ns', 0):,} ns")

print("\n📊 TOTAL PERFORMANCE")
print("-" * 80)
total = metrics.get('total', {})
print(f"  Total Time:        {total.get('time_s', 0):.4f} seconds")
print(f"  Prompt Tokens:     {total.get('prompt_tokens', 0)}")
print(f"  Generated Tokens:  {total.get('generated_tokens', 0)}")
print(f"  Total Tokens:      {total.get('total_tokens', 0)}")
print(f"  Overall Speed:     {total.get('overall_tokens_per_sec', 0):.1f} tokens/sec")

print("\n📊 BREAKDOWN")
print("-" * 80)
print(f"  Prefill %:         {(prefill.get('time_s', 0) / total.get('time_s', 1) * 100):.1f}%")
print(f"  Decode %:          {(decode.get('time_s', 0) / total.get('time_s', 1) * 100):.1f}%")

print("\n" + "="*80)
print("GENERATED OUTPUT")
print("="*80)
print(result.get('response', '')[:500])
print("="*80)

print("\n✅ Detailed metrics test complete!")
