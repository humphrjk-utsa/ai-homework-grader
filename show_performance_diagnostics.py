#!/usr/bin/env python3
"""
Performance Diagnostics Display Utility
Shows detailed performance metrics for the distributed MLX system
"""

from models.distributed_mlx_client import DistributedMLXClient
import json
import time

def show_performance_summary():
    """Display current performance diagnostics"""
    
    print("📊 Distributed MLX Performance Diagnostics")
    print("=" * 60)
    
    try:
        # Load configuration
        with open('distributed_config.json', 'r') as f:
            config = json.load(f)
        
        qwen_url = config['urls']['qwen_server']
        gemma_url = config['urls']['gemma_server']
        
        # Initialize client
        client = DistributedMLXClient(qwen_url, gemma_url)
        
        # Check system status
        status = client.get_system_status()
        
        print(f"🖥️ System Status:")
        print(f"   Mac Studio 2 (Qwen): {'✅ Online' if status['qwen_available'] else '❌ Offline'}")
        print(f"   Mac Studio 1 (GPT-OSS): {'✅ Online' if status['gemma_available'] else '❌ Offline'}")
        print(f"   Distributed Ready: {'✅ Yes' if status['distributed_ready'] else '❌ No'}")
        
        if not status['distributed_ready']:
            print("\n⚠️ Cannot show performance diagnostics - system not ready")
            return
        
        # Get performance diagnostics (if available from last run)
        diagnostics = client.get_performance_diagnostics()
        
        if diagnostics['qwen_performance']['output_tokens'] == 0:
            print(f"\n💡 No recent performance data available.")
            print(f"   Run a grading session to capture performance metrics.")
            return
        
        print(f"\n📈 Latest Performance Metrics:")
        print(f"   Captured: {diagnostics['timestamp']}")
        
        # Qwen performance
        qwen = diagnostics['qwen_performance']
        print(f"\n🔧 {qwen['model']} ({qwen['server']}):")
        print(f"   📝 Prompt Tokens: {qwen['prompt_tokens']:,}")
        print(f"   📤 Output Tokens: {qwen['output_tokens']:,}")
        print(f"   🔢 Total Tokens: {qwen['total_tokens']:,}")
        print(f"   ⏱️  Generation Time: {qwen['generation_time_seconds']:.2f}s")
        print(f"   🚀 Tokens/Second: {qwen['tokens_per_second']:.1f}")
        print(f"   🧠 Prompt Eval Time: {qwen['prompt_eval_time_seconds']:.2f}s")
        
        # GPT-OSS performance
        gemma = diagnostics['gemma_performance']
        print(f"\n📝 {gemma['model']} ({gemma['server']}):")
        print(f"   📝 Prompt Tokens: {gemma['prompt_tokens']:,}")
        print(f"   📤 Output Tokens: {gemma['output_tokens']:,}")
        print(f"   🔢 Total Tokens: {gemma['total_tokens']:,}")
        print(f"   ⏱️  Generation Time: {gemma['generation_time_seconds']:.2f}s")
        print(f"   🚀 Tokens/Second: {gemma['tokens_per_second']:.1f}")
        print(f"   🧠 Prompt Eval Time: {gemma['prompt_eval_time_seconds']:.2f}s")
        
        # Combined metrics
        combined = diagnostics['combined_metrics']
        print(f"\n🌉 Combined Performance:")
        print(f"   📊 Total Tokens: {combined['total_tokens_processed']:,}")
        print(f"   📤 Output Tokens: {combined['total_output_tokens']:,}")
        print(f"   ⚡ Parallel Efficiency: {combined['parallel_efficiency']:.1f}x")
        print(f"   🚀 Combined Throughput: {combined['combined_throughput_tokens_per_second']:.1f} tok/s")
        
        # Performance analysis
        print(f"\n🎯 Performance Analysis:")
        
        qwen_tps = qwen['tokens_per_second']
        gemma_tps = gemma['tokens_per_second']
        
        if qwen_tps > 30:
            print(f"   ✅ Qwen performance: Excellent ({qwen_tps:.1f} tok/s)")
        elif qwen_tps > 20:
            print(f"   ⚠️ Qwen performance: Good ({qwen_tps:.1f} tok/s)")
        else:
            print(f"   ❌ Qwen performance: Needs optimization ({qwen_tps:.1f} tok/s)")
        
        if gemma_tps > 35:
            print(f"   ✅ GPT-OSS performance: Excellent ({gemma_tps:.1f} tok/s)")
        elif gemma_tps > 25:
            print(f"   ⚠️ GPT-OSS performance: Good ({gemma_tps:.1f} tok/s)")
        else:
            print(f"   ❌ GPT-OSS performance: Needs optimization ({gemma_tps:.1f} tok/s)")
        
        combined_tps = combined['combined_throughput_tokens_per_second']
        if combined_tps > 60:
            print(f"   ✅ Combined throughput: Excellent ({combined_tps:.1f} tok/s)")
        elif combined_tps > 40:
            print(f"   ⚠️ Combined throughput: Good ({combined_tps:.1f} tok/s)")
        else:
            print(f"   ❌ Combined throughput: Needs optimization ({combined_tps:.1f} tok/s)")
        
        # Recommendations
        print(f"\n💡 Optimization Recommendations:")
        
        if qwen['prompt_eval_time_seconds'] > 2.0:
            print(f"   • Consider reducing Qwen prompt length (current eval: {qwen['prompt_eval_time_seconds']:.1f}s)")
        
        if gemma['prompt_eval_time_seconds'] > 3.0:
            print(f"   • Consider reducing GPT-OSS prompt length (current eval: {gemma['prompt_eval_time_seconds']:.1f}s)")
        
        if combined['parallel_efficiency'] < 1.5:
            print(f"   • Parallel efficiency could be improved (current: {combined['parallel_efficiency']:.1f}x)")
        
        if qwen_tps < 25 or gemma_tps < 30:
            print(f"   • Consider checking Mac Studio memory usage and thermal throttling")
        
        print(f"\n🎉 Performance diagnostics complete!")
        
    except Exception as e:
        print(f"❌ Error displaying performance diagnostics: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    show_performance_summary()