#!/usr/bin/env python3
"""
Standalone Gemma Server for Mac Studio 1
Run this directly on Mac Studio 1 to serve Gemma model
"""

from flask import Flask, request, jsonify
from mlx_lm import load, generate
import time

app = Flask(__name__)

# Load Gemma model
print("🔄 Loading Gemma model...")
model, tokenizer = load("mlx-community/gemma-3-27b-it-bf16")
print("✅ Gemma model loaded!")

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "loaded": True,
        "model": "gemma-3-27b-it-bf16",
        "status": "healthy"
    })

@app.route('/generate', methods=['POST'])
def generate_text():
    try:
        data = request.json
        prompt = data.get('prompt', '')
        max_tokens = data.get('max_tokens', 3800)
        temperature = data.get('temperature', 0.3)
        
        start_time = time.time()
        
        # Generate response
        response = generate(
            model,
            tokenizer,
            prompt=prompt,
            max_tokens=max_tokens,
            temp=temperature,
            verbose=False
        )
        
        generation_time = time.time() - start_time
        
        return jsonify({
            "response": response,
            "generation_time": generation_time,
            "model": "gemma-3-27b-it-bf16"
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting Gemma server on port 5001...")
    app.run(host='0.0.0.0', port=5001, debug=False)
