#!/usr/bin/env python3
"""
Decode Server for Mac Studio
Receives KV cache from DGX and generates tokens using MLX
"""

from flask import Flask, request, jsonify
from mlx_lm import load, generate
import mlx.core as mx
import time
import pickle
import base64
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Global model variables
model = None
tokenizer = None
model_loaded = False
model_path = None

def load_model(model_path_arg):
    """Load MLX model for decode"""
    global model, tokenizer, model_loaded, model_path
    
    try:
        logger.info(f"🔄 Loading MLX model from {model_path_arg}...")
        model_path = model_path_arg
        
        model, tokenizer = load(model_path)
        model_loaded = True
        
        logger.info("✅ MLX model loaded successfully!")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to load model: {e}")
        return False

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy' if model_loaded else 'loading',
        'model': model_path,
        'loaded': model_loaded,
        'backend': 'MLX'
    })

@app.route('/decode', methods=['POST'])
def decode():
    """
    Generate tokens using KV cache from prefill
    
    Request:
    {
        "kv_cache": "base64 encoded cache from DGX",
        "input_ids": [token ids],
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
    global model, tokenizer, model_loaded
    
    if not model_loaded:
        return jsonify({'error': 'Model not loaded'}), 503
    
    try:
        data = request.json
        max_new_tokens = data.get('max_new_tokens', 100)
        temperature = data.get('temperature', 0.7)
        
        # For now, generate without KV cache (MLX doesn't support external KV cache easily)
        # This is a simplified version - full implementation would need MLX KV cache integration
        prompt = data.get('prompt', '')
        
        if not prompt:
            return jsonify({'error': 'No prompt provided'}), 400
        
        start_time = time.time()
        
        # Generate using MLX
        response = generate(
            model,
            tokenizer,
            prompt=prompt,
            max_tokens=max_new_tokens,
            temp=temperature,
            verbose=False
        )
        
        decode_time = time.time() - start_time
        
        # Count tokens (approximate)
        generated_tokens = len(tokenizer.encode(response)) - len(tokenizer.encode(prompt))
        tokens_per_sec = generated_tokens / decode_time if decode_time > 0 else 0
        
        logger.info(f"✅ Decode completed in {decode_time:.3f}s")
        logger.info(f"   Tokens generated: {generated_tokens}")
        logger.info(f"   Speed: {tokens_per_sec:.1f} tok/s")
        
        return jsonify({
            'generated_text': response,
            'decode_time': decode_time,
            'tokens_generated': generated_tokens,
            'tokens_per_sec': tokens_per_sec
        })
        
    except Exception as e:
        logger.error(f"❌ Decode failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/generate', methods=['POST'])
def generate_full():
    """
    Full generation (prefill + decode on Mac)
    Fallback when DGX prefill not available
    """
    global model, tokenizer, model_loaded
    
    if not model_loaded:
        return jsonify({'error': 'Model not loaded'}), 503
    
    try:
        data = request.json
        prompt = data.get('prompt', '')
        max_tokens = data.get('max_tokens', 100)
        temperature = data.get('temperature', 0.7)
        
        start_time = time.time()
        
        response = generate(
            model,
            tokenizer,
            prompt=prompt,
            max_tokens=max_tokens,
            temp=temperature,
            verbose=False
        )
        
        total_time = time.time() - start_time
        
        return jsonify({
            'response': response,
            'generation_time': total_time,
            'model': model_path
        })
        
    except Exception as e:
        logger.error(f"❌ Generation failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/status', methods=['GET'])
def get_status():
    """Get detailed server status"""
    return jsonify({
        'server': 'Mac Decode Server',
        'model': model_path,
        'loaded': model_loaded,
        'backend': 'MLX',
        'purpose': 'Token decode from DGX prefill'
    })

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Mac Decode Server')
    parser.add_argument('--model', type=str, required=True, help='Path to MLX model')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to bind')
    parser.add_argument('--port', type=int, default=8001, help='Port to bind')
    
    args = parser.parse_args()
    
    print("🖥️  Starting Mac Decode Server (MLX)...")
    print(f"📡 Model: {args.model}")
    print(f"🌐 Binding to: {args.host}:{args.port}")
    print()
    
    if load_model(args.model):
        print("🚀 Server ready! Starting Flask app...")
        app.run(host=args.host, port=args.port, debug=False, threaded=True)
    else:
        print("❌ Failed to start server - model loading failed")
