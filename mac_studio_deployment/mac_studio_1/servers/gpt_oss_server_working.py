#!/usr/bin/env python3
"""
Gemma Server for Mac Studio 2
Serves the Gemma 3.0 model via HTTP API
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
MODEL_NAME = 'lmstudio-community/gpt-oss-120b-MLX-8bit'  # Dynamic model name

def load_model():
    """Load the GPT-OSS model"""
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
    """Generate text using Gemma model"""
    global model, tokenizer, model_loaded
    
    if not model_loaded:
        return jsonify({'error': 'Model not loaded'}), 503
    
    try:
        data = request.json
        prompt = data.get('prompt', '')
        max_tokens = data.get('max_tokens', 3800)
        temperature = data.get('temperature', 0.3)
        
        # Ensure minimum token count to avoid MLX crashes
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
        
        # Collect all tokens
        response_text = ''.join(response_generator)
        
        generation_time = time.time() - start_time
        logger.info(f"✅ Response generated in {generation_time:.2f}s")
        
        return jsonify({
            'response': response_text,
            'generation_time': generation_time,
            'tokens': len(response_text.split()),
            'model': MODEL_NAME
        })
        
    except Exception as e:
        logger.error(f"❌ Generation failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/status', methods=['GET'])
def get_status():
    """Get detailed server status"""
    return jsonify({
        'server': 'GPT-OSS Feedback Server',
        'model': MODEL_NAME,
        'loaded': model_loaded,
        'mac_studio': 1,
        'purpose': 'Feedback Generation',
        'optimal_tokens': 1200,
        'temperature': 0.3
    })

if __name__ == '__main__':
    print("🖥️ Starting GPT-OSS-120B Server on Mac Studio 1...")
    print("📡 Loading model on startup...")
    
    # Load model on startup
    if load_model():
        print("🚀 Server ready! Starting Flask app...")
        app.run(host='0.0.0.0', port=5001, debug=False, threaded=True)
    else:
        print("❌ Failed to start server - model loading failed")