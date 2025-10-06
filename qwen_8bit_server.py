#!/usr/bin/env python3
"""
Qwen 8-bit Server for Mac Studio 2
Serves the Qwen3-Coder-30B-A3B-Instruct-8bit model via HTTP API
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
MODEL_NAME = 'mlx-community/Qwen3-Coder-30B-A3B-Instruct-8bit'

def load_model():
    """Load the Qwen 8-bit model"""
    global model, tokenizer, model_loaded
    
    try:
        logger.info(f"🔄 Loading {MODEL_NAME}...")
        model, tokenizer = load(MODEL_NAME)
        model_loaded = True
        logger.info(f"✅ {MODEL_NAME} loaded successfully!")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to load model: {e}")
        model_loaded = False
        return False

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy' if model_loaded else 'loading',
        'model': MODEL_NAME,
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
        
        # Ensure minimum token count
        if max_tokens < 50:
            max_tokens = 50
        
        if not prompt:
            return jsonify({'error': 'No prompt provided'}), 400
        
        logger.info(f"🚀 Generating response (max_tokens: {max_tokens})")
        start_time = time.time()
        
        # Generate response
        response_generator = generate(
            model=model,
            tokenizer=tokenizer,
            prompt=prompt,
            max_tokens=max_tokens,
            verbose=False
        )
        
        # Collect generated text
        response_text = ""
        for token in response_generator:
            response_text += token
        
        generation_time = time.time() - start_time
        logger.info(f"✅ Generated {len(response_text)} chars in {generation_time:.2f}s")
        
        return jsonify({
            'response': response_text,
            'generation_time': generation_time,
            'model': MODEL_NAME
        })
        
    except Exception as e:
        logger.error(f"❌ Generation error: {e}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    logger.info("🚀 Starting Qwen 8-bit Server...")
    
    # Load model on startup
    if load_model():
        logger.info("🌐 Starting Flask server on 0.0.0.0:5002")
        app.run(host='0.0.0.0', port=5002, threaded=True)
    else:
        logger.error("❌ Failed to start server - model loading failed")
