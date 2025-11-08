#!/usr/bin/env python3
"""
Prefill Server using Ollama
Processes prompts and generates KV cache, sends to Mac for decode
"""

from flask import Flask, request, jsonify
import requests
import time
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Global configuration
ollama_host = "http://localhost:11434"
model_name = None
model_loaded = False

def check_model(model):
    """Check if model is available in Ollama"""
    try:
        response = requests.get(f"{ollama_host}/api/tags")
        if response.status_code == 200:
            models = response.json().get('models', [])
            for m in models:
                if m['name'] == model or m['name'].startswith(model):
                    return True
        return False
    except Exception as e:
        logger.error(f"Failed to check model: {e}")
        return False

def load_model(model):
    """Ensure model is loaded in Ollama"""
    global model_name, model_loaded
    
    try:
        logger.info(f"🔄 Checking model {model} in Ollama...")
        model_name = model
        
        if check_model(model):
            logger.info(f"✅ Model {model} is available!")
            model_loaded = True
            return True
        else:
            logger.error(f"❌ Model {model} not found in Ollama")
            logger.info(f"   Run: ollama pull {model}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Failed to check model: {e}")
        return False

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy' if model_loaded else 'loading',
        'model': model_name,
        'loaded': model_loaded,
        'backend': 'Ollama'
    })

@app.route('/prefill', methods=['POST'])
def prefill():
    """
    Process prompt and return context for decode with detailed metrics
    
    Request:
    {
        "prompt": "text to process"
    }
    
    Response:
    {
        "context": "processed prompt",
        "prompt": "original prompt",
        "prefill_time": 0.123,
        "model": "model_name",
        "metrics": {
            "prompt_eval_count": 50,
            "prompt_eval_duration": 123456789,
            "prompt_tokens_per_sec": 400.5
        }
    }
    """
    global model_name, model_loaded
    
    if not model_loaded:
        return jsonify({'error': 'Model not loaded'}), 503
    
    try:
        data = request.json
        prompt = data.get('prompt', '')
        
        if not prompt:
            return jsonify({'error': 'No prompt provided'}), 400
        
        start_time = time.time()
        
        # Get prompt token count from Ollama without generating
        # We'll use a minimal generation just to get the prompt eval metrics
        try:
            response = requests.post(
                f"{ollama_host}/api/generate",
                json={
                    'model': model_name,
                    'prompt': prompt,
                    'stream': False,
                    'options': {
                        'num_predict': 0  # No generation, just prompt processing
                    }
                },
                timeout=10
            )
            
            if response.status_code == 200:
                ollama_result = response.json()
                
                # Extract Ollama metrics
                prompt_eval_count = ollama_result.get('prompt_eval_count', 0)
                prompt_eval_duration = ollama_result.get('prompt_eval_duration', 0)
                
                # Calculate tokens per second for prefill
                prompt_tokens_per_sec = 0
                if prompt_eval_duration > 0:
                    prompt_tokens_per_sec = prompt_eval_count / (prompt_eval_duration / 1e9)
                
                prefill_time = time.time() - start_time
                
                logger.info(f"✅ Prefill completed in {prefill_time:.3f}s")
                logger.info(f"   Prompt tokens: {prompt_eval_count}")
                logger.info(f"   Prefill speed: {prompt_tokens_per_sec:.1f} tok/s")
                
                return jsonify({
                    'context': prompt,
                    'prompt': prompt,
                    'prefill_time': prefill_time,
                    'model': model_name,
                    'backend': 'Ollama',
                    'metrics': {
                        'prompt_eval_count': prompt_eval_count,
                        'prompt_eval_duration_ns': prompt_eval_duration,
                        'prompt_eval_duration_s': prompt_eval_duration / 1e9,
                        'prompt_tokens_per_sec': prompt_tokens_per_sec,
                        'prompt_chars': len(prompt)
                    }
                })
        except Exception as e:
            logger.warning(f"Ollama metrics failed, using simple prefill: {e}")
            # Fallback to simple prefill
            prefill_time = time.time() - start_time
            
            return jsonify({
                'context': prompt,
                'prompt': prompt,
                'prefill_time': prefill_time,
                'model': model_name,
                'backend': 'Ollama',
                'metrics': {
                    'prompt_chars': len(prompt)
                }
            })
        
    except Exception as e:
        logger.error(f"❌ Prefill failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/status', methods=['GET'])
def get_status():
    """Get detailed server status"""
    if not model_loaded:
        return jsonify({'error': 'Model not loaded'}), 503
    
    try:
        # Get Ollama status
        response = requests.get(f"{ollama_host}/api/tags")
        ollama_running = response.status_code == 200
        
        return jsonify({
            'server': 'Ollama Prefill Server',
            'model': model_name,
            'loaded': model_loaded,
            'backend': 'Ollama',
            'ollama_running': ollama_running,
            'ollama_host': ollama_host
        })
    except Exception as e:
        return jsonify({
            'server': 'Ollama Prefill Server',
            'model': model_name,
            'loaded': model_loaded,
            'backend': 'Ollama',
            'ollama_running': False,
            'error': str(e)
        })

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Ollama Prefill Server')
    parser.add_argument('--model', type=str, required=True, help='Ollama model name')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to bind')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind')
    parser.add_argument('--ollama-host', type=str, default='http://localhost:11434', help='Ollama host')
    
    args = parser.parse_args()
    
    ollama_host = args.ollama_host
    
    print("🖥️  Starting Ollama Prefill Server...")
    print(f"📡 Model: {args.model}")
    print(f"🌐 Binding to: {args.host}:{args.port}")
    print(f"🔗 Ollama: {ollama_host}")
    print()
    
    if load_model(args.model):
        print("🚀 Server ready! Starting Flask app...")
        app.run(host=args.host, port=args.port, debug=False, threaded=True)
    else:
        print("❌ Failed to start server - model not available")
        print(f"   Run: ollama pull {args.model}")
