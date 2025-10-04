#!/usr/bin/env python3
"""
Qwen Coder Server for Mac Studio 2
Serves the Qwen 3.0 Coder model via HTTP API
"""

from flask import Flask, request, jsonify
from mlx_lm import load, generate
import time
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Global model variables
model = None
tokenizer = None
model_loaded = False

def load_model():
    """Load the Qwen model"""
    global model, tokenizer, model_loaded
    
    try:
        logger.info("🔄 Loading Qwen 3.0 Coder model...")
        model, tokenizer = load('mlx-community/Qwen3-Coder-30B-A3B-Instruct-bf16')
        model_loaded = True
        logger.info("✅ Qwen 3.0 Coder loaded successfully!")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to load Qwen model: {e}")
        model_loaded = False
        return False

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy' if model_loaded else 'loading',
        'model': 'Qwen3-Coder-30B-A3B-Instruct-bf16',
        'loaded': model_loaded
    })

@app.route('/generate', methods=['POST'])
def generate_text():
    """Generate text using Qwen model"""
    global model, tokenizer, model_loaded
    
    if not model_loaded:
        return jsonify({'error': 'Model not loaded'}), 503
    
    try:
        data = request.json
        prompt = data.get('prompt', '')
        max_tokens = data.get('max_tokens', 2400)
        temperature = data.get('temperature', 0.1)
        
        if not prompt:
            return jsonify({'error': 'No prompt provided'}), 400
        
        logger.info(f"🚀 Generating response (max_tokens: {max_tokens})")
        logger.info(f"📝 Prompt length: {len(prompt)} chars")
        logger.info(f"📝 Prompt preview: {prompt[:200]}...")
        start_time = time.time()
        
        # Generate response (returns a generator)
        # Note: MLX-LM 0.28.1 doesn't support temp parameter in generate_step
        # Temperature control would require upgrading MLX-LM or using different sampling
        response_generator = generate(
            model=model,
            tokenizer=tokenizer,
            prompt=prompt,
            max_tokens=max_tokens,
            verbose=False
        )
        
        # Collect all generated tokens into a list first, then join
        tokens = []
        for token in response_generator:
            tokens.append(token)
        response_text = ''.join(tokens)
        
        logger.info(f"🔍 Collected {len(tokens)} tokens from generator")
        
        generation_time = time.time() - start_time
        logger.info(f"✅ Response generated in {generation_time:.2f}s")
        logger.info(f"📏 Response length: {len(response_text)} chars")
        logger.info(f"📝 Response preview: {response_text[:100] if response_text else 'EMPTY!'}")
        
        return jsonify({
            'response': response_text,
            'generation_time': generation_time,
            'tokens': len(response_text.split()),
            'model': 'Qwen3-Coder-30B-A3B-Instruct-bf16'
        })
        
    except Exception as e:
        logger.error(f"❌ Generation failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/status', methods=['GET'])
def get_status():
    """Get detailed server status"""
    return jsonify({
        'server': 'Qwen Coder Server',
        'model': 'Qwen3-Coder-30B-A3B-Instruct-bf16',
        'loaded': model_loaded,
        'mac_studio': 2,
        'purpose': 'Code Analysis',
        'optimal_tokens': 2400,
        'temperature': 0.1
    })

if __name__ == '__main__':
    print("🖥️ Starting Qwen Coder Server on Mac Studio 2...")
    print("📡 Loading model on startup...")
    
    # Load model on startup
    if load_model():
        print("🚀 Server ready! Starting Flask app...")
        app.run(host='0.0.0.0', port=5002, debug=False, threaded=True)
    else:
        print("❌ Failed to start server - model loading failed")