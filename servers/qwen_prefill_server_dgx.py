#!/usr/bin/env python3
"""
Qwen Prefill Server for DGX Spark 1
Handles prefill phase for disaggregated inference
"""

from flask import Flask, request, jsonify
import requests
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Ollama configuration for DGX Spark 1
OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "hopephoto/qwen3-coder-30b-a3b-instruct_q8:latest"

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'model': MODEL_NAME,
        'server': 'DGX Spark 1 - Qwen Prefill',
        'role': 'prefill'
    })

@app.route('/prefill', methods=['POST'])
def prefill():
    """
    Prefill phase: Process prompt and generate KV cache
    Returns prompt and context for decode phase
    """
    try:
        data = request.json
        prompt = data.get('prompt', '')
        
        if not prompt:
            return jsonify({'error': 'No prompt provided'}), 400
        
        logger.info(f"🚀 Prefill starting (prompt length: {len(prompt)} chars)")
        start_time = time.time()
        
        # Use Ollama to process the prompt and get KV cache
        # We'll generate just 1 token to get the prefill metrics
        response = requests.post(
            OLLAMA_URL,
            json={
                'model': MODEL_NAME,
                'prompt': prompt,
                'stream': False,
                'options': {
                    'num_predict': 1  # Just prefill, minimal decode
                }
            },
            timeout=60
        )
        
        if response.status_code != 200:
            raise Exception(f"Ollama prefill failed: {response.status_code}")
        
        result = response.json()
        prefill_time = time.time() - start_time
        
        logger.info(f"✅ Prefill completed in {prefill_time:.3f}s")
        
        # Extract metrics
        prompt_eval_count = result.get('prompt_eval_count', 0)
        prompt_eval_duration = result.get('prompt_eval_duration', 0)
        
        return jsonify({
            'prompt': prompt,
            'context': result.get('context', []),  # KV cache for decode
            'metrics': {
                'prompt_eval_count': prompt_eval_count,
                'prompt_eval_duration_ns': prompt_eval_duration,
                'prompt_tokens_per_sec': (prompt_eval_count / (prompt_eval_duration / 1e9)) if prompt_eval_duration > 0 else 0,
                'prefill_time_s': prefill_time
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Prefill failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/status', methods=['GET'])
def get_status():
    """Get detailed server status"""
    return jsonify({
        'server': 'Qwen Prefill Server',
        'model': MODEL_NAME,
        'dgx': 'Spark 1',
        'role': 'prefill',
        'purpose': 'Code Analysis Prefill'
    })

if __name__ == '__main__':
    print("🖥️ Starting Qwen Prefill Server on DGX Spark 1...")
    print(f"📡 Model: {MODEL_NAME}")
    print("🚀 Server ready!")
    app.run(host='0.0.0.0', port=8000, debug=False, threaded=True)
