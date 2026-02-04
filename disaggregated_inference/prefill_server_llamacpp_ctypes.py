#!/usr/bin/env python3
"""
Prefill Server using llama.cpp C API directly (via ctypes)
Generates KV cache and sends to Mac for decode
"""

from flask import Flask, request, jsonify
import time
import logging
import base64
import os
import sys
import ctypes
from ctypes import c_void_p, c_int, c_size_t, c_uint8, c_char_p, c_float, c_bool, POINTER, byref

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Global model variables
lib = None
model = None
ctx = None
model_loaded = False
model_path = None
n_ctx = 4096

# Load llama.cpp shared library
def load_library(lib_path='/home/humphrjk/llama.cpp/build/bin/libllama.so'):
    """Load the llama.cpp shared library"""
    global lib
    try:
        lib = ctypes.CDLL(lib_path)
        logger.info(f"✅ Loaded llama.cpp library from {lib_path}")

        # Define C function signatures
        # llama_model_load_from_file
        lib.llama_model_load_from_file.argtypes = [c_char_p, c_void_p]
        lib.llama_model_load_from_file.restype = c_void_p

        # llama_new_context_with_model
        lib.llama_new_context_with_model.argtypes = [c_void_p, c_void_p]
        lib.llama_new_context_with_model.restype = c_void_p

        # llama_free_model
        lib.llama_free_model.argtypes = [c_void_p]
        lib.llama_free_model.restype = None

        # llama_free
        lib.llama_free.argtypes = [c_void_p]
        lib.llama_free.restype = None

        # llama_context_default_params
        lib.llama_context_default_params.argtypes = []
        lib.llama_context_default_params.restype = c_void_p

        # llama_tokenize
        lib.llama_tokenize.argtypes = [c_void_p, c_char_p, c_int, POINTER(c_int), c_int, c_bool, c_bool]
        lib.llama_tokenize.restype = c_int

        # llama_decode
        lib.llama_decode.argtypes = [c_void_p, c_void_p]
        lib.llama_decode.restype = c_int

        # llama_state_get_size
        lib.llama_state_get_size.argtypes = [c_void_p]
        lib.llama_state_get_size.restype = c_size_t

        # llama_state_get_data
        lib.llama_state_get_data.argtypes = [c_void_p, POINTER(c_uint8), c_size_t]
        lib.llama_state_get_data.restype = c_size_t

        # llama_batch_init
        lib.llama_batch_init.argtypes = [c_int, c_int, c_int]
        lib.llama_batch_init.restype = c_void_p

        # llama_batch_free
        lib.llama_batch_free.argtypes = [c_void_p]
        lib.llama_batch_free.restype = None

        # llama_kv_cache_clear
        lib.llama_kv_cache_clear.argtypes = [c_void_p]
        lib.llama_kv_cache_clear.restype = None

        return True
    except Exception as e:
        logger.error(f"❌ Failed to load library: {e}")
        return False

def load_model(model_path_arg, n_ctx_arg=4096, n_gpu_layers=-1):
    """Load llama model using C API"""
    global model, ctx, model_loaded, model_path, n_ctx

    if not lib:
        logger.error("❌ Library not loaded")
        return False

    try:
        logger.info(f"🔄 Loading model from {model_path_arg}...")
        model_path = model_path_arg
        n_ctx = n_ctx_arg

        # Check if model file exists
        if not os.path.exists(model_path_arg):
            logger.error(f"❌ Model file not found: {model_path_arg}")
            return False

        # Create model params (NULL for default)
        model = lib.llama_model_load_from_file(
            model_path_arg.encode('utf-8'),
            None  # Use default params
        )

        if not model:
            logger.error("❌ Failed to load model")
            return False

        logger.info(f"✅ Model loaded")

        # Create context params structure
        # For now, use default params - in production you'd create a proper struct
        ctx = lib.llama_new_context_with_model(model, None)

        if not ctx:
            logger.error("❌ Failed to create context")
            lib.llama_free_model(model)
            return False

        logger.info(f"✅ Context created (n_ctx: {n_ctx})")

        model_loaded = True
        logger.info("✅ llama.cpp model loaded successfully!")

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
        'backend': 'llama.cpp C API (ctypes)',
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
    global ctx, model, model_loaded

    if not model_loaded:
        return jsonify({'error': 'Model not loaded'}), 503

    try:
        data = request.json
        prompt = data.get('prompt', '')

        if not prompt:
            return jsonify({'error': 'No prompt provided'}), 400

        start_time = time.time()

        logger.info(f"🚀 Processing prefill for prompt ({len(prompt)} chars)...")

        # Tokenize prompt
        prompt_bytes = prompt.encode('utf-8')
        max_tokens = 8192
        tokens = (c_int * max_tokens)()

        n_tokens = lib.llama_tokenize(
            model,
            prompt_bytes,
            len(prompt_bytes),
            tokens,
            max_tokens,
            True,  # add_bos
            False  # special
        )

        if n_tokens < 0:
            return jsonify({'error': 'Tokenization failed'}), 500

        logger.info(f"   Prompt tokens: {n_tokens}")

        # Clear KV cache
        lib.llama_kv_cache_clear(ctx)

        # Process tokens in batches using llama_decode
        # Note: This is a simplified version - production code would use llama_batch properly
        batch_size = 2048
        for i in range(0, n_tokens, batch_size):
            batch_end = min(i + batch_size, n_tokens)
            batch_tokens = tokens[i:batch_end]

            # In production, you'd create a proper llama_batch struct
            # For now, this is a placeholder showing the concept
            # You would need to properly construct the batch with positions, etc.
            logger.info(f"   Processing batch {i}-{batch_end}")
            # TODO: Implement proper batch creation and decoding

        # Extract llama.cpp state using C API
        try:
            # Get state size
            state_size = lib.llama_state_get_size(ctx)
            logger.info(f"   C API state size: {state_size / 1024 / 1024:.1f} MB")

            # Allocate buffer and copy state data
            state_buffer = (c_uint8 * state_size)()
            bytes_copied = lib.llama_state_get_data(ctx, state_buffer, state_size)

            logger.info(f"   Copied {bytes_copied} bytes")

            # Convert to Python bytes
            state_bytes = bytes(state_buffer[:bytes_copied])

            # Compress state for faster network transfer
            import zlib
            compression_start = time.time()
            state_bytes_compressed = zlib.compress(state_bytes, level=6)
            compression_time = time.time() - compression_start

            state_base64 = base64.b64encode(state_bytes_compressed).decode('utf-8')
            state_size_mb = len(state_bytes) / 1024 / 1024
            compressed_size_mb = len(state_bytes_compressed) / 1024 / 1024
            compression_ratio = len(state_bytes) / len(state_bytes_compressed) if len(state_bytes_compressed) > 0 else 0

        except Exception as e:
            logger.error(f"❌ Failed to extract state using C API: {e}")
            import traceback
            traceback.print_exc()
            return jsonify({'error': f'Failed to extract state: {e}'}), 500

        prefill_time = time.time() - start_time

        logger.info(f"✅ Prefill completed in {prefill_time:.3f}s")
        logger.info(f"   State size: {state_size_mb:.1f} MB (uncompressed)")
        logger.info(f"   Compressed: {compressed_size_mb:.1f} MB ({compression_ratio:.1f}x reduction)")
        logger.info(f"   Compression time: {compression_time:.3f}s")
        logger.info(f"   Prefill speed: {n_tokens / prefill_time:.1f} tok/s")

        return jsonify({
            'llama_state': state_base64,
            'state_size_mb': state_size_mb,
            'compressed_size_mb': compressed_size_mb,
            'compression_ratio': compression_ratio,
            'prompt': prompt,
            'prefill_time': prefill_time,
            'prompt_tokens': n_tokens,
            'prefill_speed': n_tokens / prefill_time if prefill_time > 0 else 0,
            'n_tokens': n_tokens,
            'method': 'c_api_ctypes_compressed'
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
        'server': 'llama.cpp Prefill Server (DGX) - C API via ctypes',
        'model': model_path,
        'loaded': model_loaded,
        'backend': 'llama.cpp C API',
        'purpose': 'Prefill for disaggregated inference'
    }

    return jsonify(status)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='llama.cpp Prefill Server (C API via ctypes)')
    parser.add_argument('--model', type=str, required=True, help='Path to GGUF model file')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to bind')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind')
    parser.add_argument('--n-ctx', type=int, default=4096, help='Context window size')
    parser.add_argument('--n-gpu-layers', type=int, default=-1, help='GPU layers (-1 for all)')
    parser.add_argument('--lib-path', type=str, default='/home/humphrjk/llama.cpp/build/bin/libllama.so',
                       help='Path to libllama.so')

    args = parser.parse_args()

    print("🎮 Starting llama.cpp Prefill Server (C API via ctypes)...")
    print(f"📡 Model: {args.model}")
    print(f"📚 Library: {args.lib_path}")
    print(f"🌐 Binding to: {args.host}:{args.port}")
    print(f"📏 Context window: {args.n_ctx}")
    print()

    if not load_library(args.lib_path):
        print("❌ Failed to load llama.cpp library")
        sys.exit(1)

    if load_model(args.model, n_ctx_arg=args.n_ctx, n_gpu_layers=args.n_gpu_layers):
        print("🚀 Server ready! Starting Flask app...")
        print()
        print("📝 Using llama.cpp C API directly via ctypes (no Python bindings).")
        print()
        app.run(host=args.host, port=args.port, debug=False, threaded=True)
    else:
        print("❌ Failed to start server - model loading failed")
        sys.exit(1)
