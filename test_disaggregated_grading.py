#!/usr/bin/env python3
"""
Test grading with disaggregated inference
"""
import sys
import time
from disaggregated_client import DisaggregatedClient
from model_config import get_model_config, MODEL_SETTINGS

# Test notebook
notebook_path = "submissions/16/Hillarymcallisterlesson7_hillary.ipynb"

print("\n" + "="*70)
print("TESTING DISAGGREGATED INFERENCE FOR GRADING")
print("="*70)

# Get disaggregated model config
model_name = "disaggregated:qwen3-coder:30b"
config = MODEL_SETTINGS[model_name]

print(f"\nModel: {model_name}")
print(f"Description: {config['description']}")
print(f"Prefill: {config['prefill_url']}")
print(f"Decode: {config['decode_url']}")

# Create client
client = DisaggregatedClient(
    prefill_url=config['prefill_url'],
    decode_url=config['decode_url']
)

# Create a simple grading prompt
prompt = f"""You are grading a Python homework assignment on string and datetime operations.

Assignment: Lesson 7 - String and DateTime Operations
Student: Hillary McAllister

Please provide:
1. A brief assessment of the code quality
2. Key strengths
3. Areas for improvement
4. Estimated score out of 100

Keep your response concise (under 200 words).

Student's work is in: {notebook_path}

Provide your grading feedback:"""

print("\n" + "="*70)
print("GENERATING GRADING FEEDBACK")
print("="*70)

start_time = time.time()

try:
    result = client.generate(
        prompt=prompt,
        max_tokens=500,
        temperature=0.3
    )
    
    total_time = time.time() - start_time
    
    print(f"\n✅ Generation Complete!")
    print(f"\nTiming:")
    print(f"  Prefill (DGX):  {result['prefill_time']:.3f}s")
    print(f"  Decode (Mac):   {result['decode_time']:.3f}s")
    print(f"  Total:          {result['total_time']:.3f}s")
    print(f"  Speed:          {result['tokens_per_sec']:.1f} tok/s")
    
    print(f"\n" + "="*70)
    print("GRADING FEEDBACK")
    print("="*70)
    print(result['response'])
    print("="*70)
    
    print(f"\n✅ Disaggregated inference test PASSED!")
    print(f"   Ready to use in production grading app")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    sys.exit(1)
