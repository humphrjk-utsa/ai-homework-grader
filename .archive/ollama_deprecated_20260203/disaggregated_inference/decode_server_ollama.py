#!/usr/bin/env python3
"""
Decode Server using Ollama
Receives context from prefill and generates tokens
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

@app.route('/decode', methods=['POST'])
def decode():
    """
    Generate tokens using context from prefill
    
    Request:
    {
        "context": "processed context from prefill",
        "prompt": "original prompt",
        "max_new_tokens": 100,
        "temperature": 0.7
    }
    
    Response:
    {
        "generated_text": "output text",
        "decode_time": 1.234,
        "tokens_generated": 50,
        "tokens_per_sec": 40.5
    }
    """
    global model_name, model_loaded
    
    if not model_loaded:
        return jsonify({'error': 'Model not loaded'}), 503
    
    try:
        data = request.json
        prompt = data.get('prompt', data.get('context', ''))
        max_tokens = data.get('max_new_tokens', 100)
        temperature = data.get('temperature', 0.7)
        
        if not prompt:
            return jsonify({'error': 'No prompt provided'}), 400
        
        start_time = time.time()
        
        # Generate using Ollama
        response = requests.post(
            f"{ollama_host}/api/generate",
            json={
                'model': model_name,
                'prompt': prompt,
                'stream': False,
                'options': {
                    'num_predict': max_tokens,
                    'temperature': temperature
                }
            },
            timeout=120
        )
        
        if response.status_code != 200:
            return jsonify({'error': f'Ollama error: {response.status_code}'}), 500
        
        result = response.json()
        generated_text = result.get('response', '')
        
        decode_time = time.time() - start_time
        
        # Extract Ollama metrics
        eval_count = result.get('eval_count', 0)
        eval_duration = result.get('eval_duration', 0)
        prompt_eval_count = result.get('prompt_eval_count', 0)
        prompt_eval_duration = result.get('prompt_eval_duration', 0)
        total_duration = result.get('total_duration', 0)
        load_duration = result.get('load_duration', 0)
        
        # Calculate tokens per second
        tokens_per_sec = 0
        if eval_duration > 0:
            tokens_per_sec = eval_count / (eval_duration / 1e9)
        
        logger.info(f"✅ Decode completed in {decode_time:.3f}s")
        logger.info(f"   Tokens generated: {eval_count}")
        logger.info(f"   Decode speed: {tokens_per_sec:.1f} tok/s")
        
        return jsonify({
            'generated_text': prompt + generated_text,
            'decode_time': decode_time,
            'tokens_generated': eval_count,
            'tokens_per_sec': tokens_per_sec,
            'model': model_name,
            'metrics': {
                'eval_count': eval_count,
                'eval_duration_ns': eval_duration,
                'eval_duration_s': eval_duration / 1e9,
                'tokens_per_sec': tokens_per_sec,
                'prompt_eval_count': prompt_eval_count,
                'prompt_eval_duration_ns': prompt_eval_duration,
                'prompt_eval_duration_s': prompt_eval_duration / 1e9,
                'total_duration_ns': total_duration,
                'total_duration_s': total_duration / 1e9,
                'load_duration_ns': load_duration,
                'load_duration_s': load_duration / 1e9
            }
        })
        
    except Exception as e:
        logger.error(f"❌ Decode failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/generate', methods=['POST'])
def generate_full():
    """
    Full generation (prefill + decode)
    Fallback when prefill server not available
    """
    global model_name, model_loaded
    
    if not model_loaded:
        return jsonify({'error': 'Model not loaded'}), 503
    
    try:
        data = request.json
        prompt = data.get('prompt', '')
        max_tokens = data.get('max_tokens', 100)
        temperature = data.get('temperature', 0.7)
        
        start_time = time.time()
        
        response = requests.post(
            f"{ollama_host}/api/generate",
            json={
                'model': model_name,
                'prompt': prompt,
                'stream': False,
                'options': {
                    'num_predict': max_tokens,
                    'temperature': temperature
                }
            },
            timeout=120
        )
        
        if response.status_code != 200:
            return jsonify({'error': f'Ollama error: {response.status_code}'}), 500
        
        result = response.json()
        generated_text = result.get('response', '')
        
        total_time = time.time() - start_time
        
        return jsonify({
            'response': prompt + generated_text,
            'generation_time': total_time,
            'model': model_name
        })
        
    except Exception as e:
        logger.error(f"❌ Generation failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/status', methods=['GET'])
def get_status():
    """Get detailed server status"""
    try:
        response = requests.get(f"{ollama_host}/api/tags")
        ollama_running = response.status_code == 200
        
        return jsonify({
            'server': 'Ollama Decode Server',
            'model': model_name,
            'loaded': model_loaded,
            'backend': 'Ollama',
            'ollama_running': ollama_running,
            'ollama_host': ollama_host
        })
    except Exception as e:
        return jsonify({
            'server': 'Ollama Decode Server',
            'model': model_name,
            'loaded': model_loaded,
            'backend': 'Ollama',
            'ollama_running': False,
            'error': str(e)
        })

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Ollama Decode Server')
    parser.add_argument('--model', type=str, required=True, help='Ollama model name')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to bind')
    parser.add_argument('--port', type=int, default=8001, help='Port to bind')
    parser.add_argument('--ollama-host', type=str, default='http://localhost:11434', help='Ollama host')
    
    args = parser.parse_args()
    
    ollama_host = args.ollama_host
    
    print("🖥️  Starting Ollama Decode Server...")
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
