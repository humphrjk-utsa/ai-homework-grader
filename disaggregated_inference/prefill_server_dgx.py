#!/usr/bin/env python3
"""
Prefill Server for DGX Spark
Processes prompts and generates KV cache, sends to Mac for decode
"""

from flask import Flask, request, jsonify
import torch
from transformers import AutoTokenizer, AutoModelForCausalLM
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
    """Load model for prefill"""
    global model, tokenizer, model_loaded, model_path
    
    try:
        logger.info(f"🔄 Loading model from {model_path_arg}...")
        model_path = model_path_arg
        
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        
        # Try to load with modelopt support for FP4 models
        try:
            import modelopt.torch.quantization as mtq
            logger.info("Loading FP4 quantized model with ModelOpt...")
            model = AutoModelForCausalLM.from_pretrained(
                model_path,
                device_map="auto",
                trust_remote_code=True
            )
        except ImportError:
            logger.warning("ModelOpt not available, loading with standard transformers...")
            model = AutoModelForCausalLM.from_pretrained(
                model_path,
                torch_dtype=torch.float16,
                device_map="auto",
                trust_remote_code=True
            )
        
        model.eval()
        
        model_loaded = True
        logger.info("✅ Model loaded successfully!")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to load model: {e}")
        import traceback
        traceback.print_exc()
        return False

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy' if model_loaded else 'loading',
        'model': model_path,
        'loaded': model_loaded,
        'device': str(next(model.parameters()).device) if model_loaded else None
    })

@app.route('/prefill', methods=['POST'])
def prefill():
    """
    Process prompt and return KV cache for decode
    
    Request:
    {
        "prompt": "text to process",
        "max_new_tokens": 100
    }
    
    Response:
    {
        "kv_cache": "base64 encoded cache",
        "input_ids": [token ids],
        "prefill_time": 0.123,
        "prompt_tokens": 50
    }
    """
    global model, tokenizer, model_loaded
    
    if not model_loaded:
        return jsonify({'error': 'Model not loaded'}), 503
    
    try:
        data = request.json
        prompt = data.get('prompt', '')
        
        if not prompt:
            return jsonify({'error': 'No prompt provided'}), 400
        
        start_time = time.time()
        
        # Tokenize
        inputs = tokenizer(prompt, return_tensors="pt").to(model.device)
        input_ids = inputs['input_ids']
        
        # Run prefill (forward pass to generate KV cache)
        with torch.no_grad():
            outputs = model(
                input_ids=input_ids,
                use_cache=True,
                return_dict=True
            )
        
        # Extract KV cache
        past_key_values = outputs.past_key_values
        
        # Serialize KV cache
        # Convert to CPU and serialize
        kv_cache_cpu = []
        for layer_cache in past_key_values:
            layer_cpu = tuple(t.cpu() for t in layer_cache)
            kv_cache_cpu.append(layer_cpu)
        
        # Pickle and base64 encode
        kv_bytes = pickle.dumps(kv_cache_cpu)
        kv_base64 = base64.b64encode(kv_bytes).decode('utf-8')
        
        prefill_time = time.time() - start_time
        
        logger.info(f"✅ Prefill completed in {prefill_time:.3f}s")
        logger.info(f"   Prompt tokens: {input_ids.shape[1]}")
        logger.info(f"   KV cache size: {len(kv_bytes) / 1024 / 1024:.2f} MB")
        
        return jsonify({
            'kv_cache': kv_base64,
            'input_ids': input_ids[0].tolist(),
            'prefill_time': prefill_time,
            'prompt_tokens': input_ids.shape[1],
            'kv_cache_size_mb': len(kv_bytes) / 1024 / 1024
        })
        
    except Exception as e:
        logger.error(f"❌ Prefill failed: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/status', methods=['GET'])
def get_status():
    """Get detailed server status"""
    if not model_loaded:
        return jsonify({'error': 'Model not loaded'}), 503
    
    return jsonify({
        'server': 'DGX Prefill Server',
        'model': model_path,
        'loaded': model_loaded,
        'device': str(next(model.parameters()).device),
        'dtype': str(next(model.parameters()).dtype),
        'memory_allocated_gb': torch.cuda.memory_allocated() / 1e9 if torch.cuda.is_available() else 0,
        'memory_reserved_gb': torch.cuda.memory_reserved() / 1e9 if torch.cuda.is_available() else 0
    })

if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='DGX Prefill Server')
    parser.add_argument('--model', type=str, required=True, help='Path to model')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to bind')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind')
    
    args = parser.parse_args()
    
    print("🖥️  Starting DGX Prefill Server...")
    print(f"📡 Model: {args.model}")
    print(f"🌐 Binding to: {args.host}:{args.port}")
    print()
    
    if load_model(args.model):
        print("🚀 Server ready! Starting Flask app...")
        app.run(host=args.host, port=args.port, debug=False, threaded=True)
    else:
        print("❌ Failed to start server - model loading failed")
