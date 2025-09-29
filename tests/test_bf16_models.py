#!/usr/bin/env python3
"""
Test the bf16 models - let them download if needed
"""

import time
import sys
sys.path.append('.')

from simple_mlx_client import SimpleMLXClient

def test_bf16_models():
    """Test both bf16 models - downloads allowed"""
    
    print("🎯 Testing BF16 Models (Downloads Allowed)")
    print("=" * 60)
    
    models_to_test = [
        {
            'name': 'Qwen3 Coder BF16',
            'model_id': 'mlx-community/Qwen3-Coder-30B-A3B-Instruct-bf16',
            'prompt': 'Analyze this R code:\n\ndata <- read.csv("file.csv")\nsummary(data)\n\nIs this correct?'
        },
        {
            'name': 'Gemma-3 BF16', 
            'model_id': 'mlx-community/gemma-3-27b-it-bf16',
            'prompt': 'Provide educational feedback for this R code:\n\ndata <- read.csv("file.csv")\nsummary(data)\n\nFocus on what the student did well.'
        }
    ]
    
    results = []
    
    for model_info in models_to_test:
        print(f"\n🧪 Testing: {model_info['name']}")
        print(f"📦 Model: {model_info['model_id']}")
        print("-" * 60)
        
        try:
            # Initialize client
            start_time = time.time()
            print("🚀 Initializing client...")
            
            client = SimpleMLXClient(model_info['model_id'])
            
            # Test generation
            print("📝 Testing generation...")
            print(f"💬 Prompt: {model_info['prompt'][:50]}...")
            
            response = client.generate_response(
                model_info['prompt'], 
                max_tokens=200
            )
            
            total_time = time.time() - start_time
            
            print(f"✅ SUCCESS!")
            print(f"⏱️  Total time: {total_time:.1f}s")
            print(f"📄 Response preview: {response[:150]}...")
            
            results.append({
                'name': model_info['name'],
                'model_id': model_info['model_id'],
                'success': True,
                'time': total_time,
                'response_length': len(response) if response else 0
            })
            
        except Exception as e:
            print(f"❌ FAILED: {e}")
            results.append({
                'name': model_info['name'],
                'model_id': model_info['model_id'],
                'success': False,
                'error': str(e)
            })
    
    # Summary
    print(f"\n{'='*60}")
    print("📊 SUMMARY")
    print(f"{'='*60}")
    
    successful = [r for r in results if r['success']]
    failed = [r for r in results if not r['success']]
    
    print(f"✅ Successful: {len(successful)}/2")
    print(f"❌ Failed: {len(failed)}/2")
    
    if successful:
        print(f"\n🎯 Working Models:")
        for result in successful:
            print(f"  ✅ {result['name']}: {result['time']:.1f}s")
    
    if failed:
        print(f"\n💥 Failed Models:")
        for result in failed:
            print(f"  ❌ {result['name']}: {result['error'][:100]}...")
    
    # Performance assessment
    if len(successful) == 2:
        total_time = sum(r['time'] for r in successful)
        print(f"\n🚀 Combined Performance: {total_time:.1f}s")
        
        if total_time < 120:
            print("🎯 EXCELLENT: Ready for production!")
        elif total_time < 300:
            print("✅ GOOD: Acceptable for grading")
        else:
            print("⚠️  SLOW: May need optimization")
    
    return results

if __name__ == "__main__":
    test_bf16_models()