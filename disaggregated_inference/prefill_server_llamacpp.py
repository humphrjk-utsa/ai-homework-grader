#!/usr/bin/env python3
"""
Prefill Server using llama.cpp for DGX Spark
Generates KV cache and sends to Mac for decode
"""

from flask import Flask, request, jsonify
import time
import logging
import pickle
import base64
import os
import sys

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Global model variables
model = None
model_loaded = False
model_path = None

def load_model(model_path_arg, n_ctx=4096, n_gpu_layers=-1):
    """Load llama.cpp model for prefill"""
    global model, model_loaded, model_path

    try:
        from llama_cpp import Llama

        logger.info(f"🔄 Loading llama.cpp model from {model_path_arg}...")
        model_path = model_path_arg

        # Check if model file exists
        if not os.path.exists(model_path_arg):
            logger.error(f"❌ Model file not found: {model_path_arg}")
            return False

        # Determine optimal settings for DGX (NVIDIA GPU)
        import subprocess
        try:
            result = subprocess.run(['nvidia-smi'], capture_output=True, timeout=5)
            if result.returncode == 0:
                logger.info("🎮 NVIDIA GPU detected - using CUDA acceleration")
                n_gpu_layers = -1  # Use all layers on GPU
            else:
                logger.info("💻 Using CPU inference")
                n_gpu_layers = 0
        except:
            logger.info("💻 Using CPU inference")
            n_gpu_layers = 0

        # Load model with optimized settings
        model = Llama(
            model_path=model_path_arg,
            n_ctx=n_ctx,              # Context window
            n_threads=16,             # CPU threads for DGX
            n_gpu_layers=n_gpu_layers, # GPU acceleration
            verbose=False,
            use_mmap=True,            # Memory mapping
            use_mlock=False,
            n_batch=512,              # Batch size
            f16_kv=True,              # FP16 for KV cache
        )

        model_loaded = True
        logger.info("✅ llama.cpp model loaded successfully!")
        logger.info(f"   Context window: {n_ctx}")
        logger.info(f"   GPU layers: {n_gpu_layers}")

        return True

    except ImportError:
        logger.error("❌ llama-cpp-python not installed")
        logger.error("   Install with: CMAKE_ARGS='-DLLAMA_CUBLAS=on' pip install llama-cpp-python")
        return False
    except Exception as e:
        logger.error(f"❌ Failed to load model: {e}")
        import traceback
        traceback.print_exc()
        return False

def extract_llama_state(model):
    """
    Extract llama.cpp internal state after prefill

    Uses the save_state() method from llama-cpp-python which serializes:
    - KV cache (key-value pairs for each layer)
    - Token positions
    - Context state

    Returns:
        dict with state data or None if extraction fails
    """
    try:
        # Use the built-in save_state() method
        state = model.save_state()

        # Determine how to extract bytes from the state object
        if hasattr(state, 'llama_state'):
            # Newer version: LlamaState object with llama_state attribute
            state_data = state.llama_state
        elif isinstance(state, bytes):
            # Direct bytes
            state_data = state
        else:
            # Try to serialize the state object itself
            import pickle
            state_data = pickle.dumps(state)

        return {
            'state_data': state_data,
            'state_size': len(state_data),
            'n_ctx': model.n_ctx(),
            'method': 'save_state'
        }
    except Exception as e:
        logger.error(f"Failed to extract state: {e}")
        import traceback
        traceback.print_exc()
        return None

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy' if model_loaded else 'loading',
        'model': model_path,
        'loaded': model_loaded,
        'backend': 'llama.cpp (prefill)',
        'purpose': 'Generate KV cache for Mac decode'
    })

@app.route('/prefill', methods=['POST'])
def prefill():
    """
    Process prompt and return llama.cpp state (including KV cache)

    Request:
    {
        "prompt": "text to process"
    }

    Response:
    {
        "llama_state": "base64 encoded llama.cpp state",
        "state_size_mb": 245.3,
        "prompt": "original prompt",
        "prefill_time": 0.234,
        "prompt_tokens": 50
    }
    """
    global model, model_loaded

    if not model_loaded:
        return jsonify({'error': 'Model not loaded'}), 503

    try:
        data = request.json
        prompt = data.get('prompt', '')

        if not prompt:
            return jsonify({'error': 'No prompt provided'}), 400

        start_time = time.time()

        logger.info(f"🚀 Processing prefill for prompt ({len(prompt)} chars)...")

        # Tokenize prompt (to get token count)
        tokens = model.tokenize(prompt.encode('utf-8'))
        n_tokens = len(tokens)

        logger.info(f"   Prompt tokens: {n_tokens}")

        # Run prefill (eval the prompt to populate KV cache)
        model.reset()  # Clear previous state

        # Process tokens in larger batches for better GPU throughput on DGX
        batch_size = 2048  # Increased from 512 for better DGX performance
        for i in range(0, len(tokens), batch_size):
            batch = tokens[i:i+batch_size]
            model.eval(batch)

        # Extract llama.cpp state using C API directly
        try:
            from llama_cpp import llama_cpp
            import ctypes

            # Get state size from C API
            ctx = model._ctx.ctx
            state_size = llama_cpp.llama_get_state_size(ctx)

            logger.info(f"   C API state size: {state_size / 1024 / 1024:.1f} MB")

            # Allocate buffer and copy state data
            state_buffer = (ctypes.c_uint8 * state_size)()
            bytes_copied = llama_cpp.llama_state_get_data(ctx, state_buffer, state_size)

            logger.info(f"   Copied {bytes_copied} bytes")

            # Convert to Python bytes
            state_bytes = bytes(state_buffer[:bytes_copied])

            # Compression optimization: only compress if state > 10 MB
            # For small states, compression overhead > network transfer time
            state_size_mb = len(state_bytes) / 1024 / 1024

            if state_size_mb > 10.0:
                # Large state: compression saves network time
                import zlib
                compression_start = time.time()
                state_bytes_compressed = zlib.compress(state_bytes, level=6)
                compression_time = time.time() - compression_start

                state_base64 = base64.b64encode(state_bytes_compressed).decode('utf-8')
                compressed_size_mb = len(state_bytes_compressed) / 1024 / 1024
                compression_ratio = len(state_bytes) / len(state_bytes_compressed)
                use_compression = True
            else:
                # Small state: skip compression (overhead > benefit)
                state_bytes_compressed = state_bytes
                state_base64 = base64.b64encode(state_bytes).decode('utf-8')
                compressed_size_mb = state_size_mb
                compression_ratio = 1.0
                compression_time = 0.0
                use_compression = False

        except Exception as e:
            logger.error(f"❌ Failed to extract state using C API: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': f'Failed to extract state: {e}'}), 500

        prefill_time = time.time() - start_time

        logger.info(f"✅ Prefill completed in {prefill_time:.3f}s")
        logger.info(f"   State size: {state_size_mb:.1f} MB")
        if use_compression:
            logger.info(f"   Compressed: {compressed_size_mb:.1f} MB ({compression_ratio:.1f}x reduction)")
            logger.info(f"   Compression time: {compression_time:.3f}s")
        else:
            logger.info(f"   No compression (state < 10 MB, compression overhead > benefit)")
        logger.info(f"   Prefill speed: {n_tokens / prefill_time:.1f} tok/s")

        return jsonify({
            'llama_state': state_base64,
            'state_size_mb': state_size_mb,
            'compressed_size_mb': compressed_size_mb,
            'compression_ratio': compression_ratio,
            'compressed': use_compression,  # Flag for decode server
            'prompt': prompt,
            'prefill_time': prefill_time,
            'prompt_tokens': n_tokens,
            'prefill_speed': n_tokens / prefill_time if prefill_time > 0 else 0,
            'n_tokens': n_tokens,  # Send token count for decode server
            'method': 'c_api_adaptive_compression'
        })

    except Exception as e:
        logger.error(f"❌ Prefill failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/status', methods=['GET'])
def get_status():
    """Get detailed server status"""
    status = {
        'server': 'llama.cpp Prefill Server (DGX)',
        'model': model_path,
        'loaded': model_loaded,
        'backend': 'llama.cpp',
        'purpose': 'Prefill for disaggregated inference'
    }

    if model_loaded:
        try:
            status['n_ctx'] = model.n_ctx()
            status['n_vocab'] = model.n_vocab()
        except:
            pass

    return jsonify(status)

if __name__ == '__main__':
    import argparse
    import ctypes

    parser = argparse.ArgumentParser(description='llama.cpp Prefill Server for DGX')
    parser.add_argument('--model', type=str, required=True, help='Path to GGUF model file')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to bind')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind')
    parser.add_argument('--n-ctx', type=int, default=4096, help='Context window size')
    parser.add_argument('--n-gpu-layers', type=int, default=-1, help='GPU layers (-1 for all)')

    args = parser.parse_args()

    print("🎮 Starting llama.cpp Prefill Server for DGX...")
    print(f"📡 Model: {args.model}")
    print(f"🌐 Binding to: {args.host}:{args.port}")
    print(f"📏 Context window: {args.n_ctx}")
    print()

    if load_model(args.model, n_ctx=args.n_ctx, n_gpu_layers=args.n_gpu_layers):
        print("🚀 Server ready! Starting Flask app...")
        print()
        print("📝 This server generates llama.cpp KV cache for Mac decode.")
        print("   The state includes the full llama.cpp context after prefill.")
        print()
        app.run(host=args.host, port=args.port, debug=False, threaded=True)
    else:
        print("❌ Failed to start server - model loading failed")
        sys.exit(1)
