#!/usr/bin/env python3
"""
Decode Server using llama.cpp for Mac Studios
Receives context from DGX prefill and generates tokens using llama.cpp
"""

from flask import Flask, request, jsonify
import time
import logging
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
    """Load llama.cpp model for decode"""
    global model, model_loaded, model_path

    try:
        from llama_cpp import Llama

        logger.info(f"🔄 Loading llama.cpp model from {model_path_arg}...")
        model_path = model_path_arg

        # Check if model file exists
        if not os.path.exists(model_path_arg):
            logger.error(f"❌ Model file not found: {model_path_arg}")
            return False

        # Determine optimal settings for Mac Studio (Apple Silicon)
        import platform
        is_mac = platform.system() == "Darwin"

        if is_mac:
            # Mac Studio with Apple Silicon - use Metal acceleration
            logger.info("🍎 Detected macOS - using Metal acceleration")
            n_gpu_layers = 1  # Use Metal GPU
        else:
            # Check for CUDA
            try:
                import subprocess
                result = subprocess.run(['nvidia-smi'], capture_output=True, timeout=5)
                if result.returncode == 0:
                    logger.info("🎮 NVIDIA GPU detected")
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
            n_threads=8,              # CPU threads
            n_gpu_layers=n_gpu_layers, # GPU acceleration
            verbose=False,
            use_mmap=True,            # Memory mapping for efficiency
            use_mlock=False,          # Don't lock memory
            n_batch=512,              # Batch size for processing
            f16_kv=True,              # Use FP16 for KV cache (saves memory)
        )

        model_loaded = True
        logger.info("✅ llama.cpp model loaded successfully!")
        logger.info(f"   Context window: {n_ctx}")
        logger.info(f"   GPU layers: {n_gpu_layers}")
        logger.info(f"   Model path: {model_path_arg}")

        # Pre-warm GPU context to reduce first-generation overhead
        logger.info("🔥 Pre-warming GPU context...")
        try:
            warmup_start = time.time()
            dummy_tokens = [1] * 100  # 100 dummy tokens
            model.eval(dummy_tokens)
            model.reset()
            warmup_time = time.time() - warmup_start
            logger.info(f"✅ GPU context pre-warmed ({warmup_time:.3f}s)")
        except Exception as e:
            logger.warning(f"⚠️  Pre-warming failed (non-critical): {e}")

        return True

    except ImportError:
        logger.error("❌ llama-cpp-python not installed")
        logger.error("   Install with: pip install llama-cpp-python")
        return False
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
        'backend': 'llama.cpp'
    })

@app.route('/decode', methods=['POST'])
def decode():
    """
    Generate tokens using llama.cpp with optional state injection

    Request:
    {
        "prompt": "original prompt",
        "llama_state": "base64 encoded llama.cpp state from prefill server (optional)",
        "max_new_tokens": 100,
        "temperature": 0.7,
        "top_p": 0.9,
        "top_k": 40
    }

    Response:
    {
        "generated_text": "output text",
        "decode_time": 1.234,
        "tokens_generated": 50,
        "tokens_per_sec": 40.5,
        "method": "llamacpp_with_state" or "llamacpp_full"
    }
    """
    global model, model_loaded

    if not model_loaded:
        return jsonify({'error': 'Model not loaded'}), 503

    try:
        import base64
        import ctypes

        data = request.json
        prompt = data.get('prompt', '')
        llama_state = data.get('llama_state')  # Base64 encoded state from DGX
        n_tokens_from_prefill = data.get('n_tokens', 0)  # Token count from prefill
        is_compressed = data.get('compressed', True)  # Check if state is compressed
        max_new_tokens = data.get('max_new_tokens', 100)
        temperature = data.get('temperature', 0.7)
        top_p = data.get('top_p', 0.9)
        top_k = data.get('top_k', 40)

        if not prompt:
            return jsonify({'error': 'No prompt provided'}), 400

        start_time = time.time()
        method = 'llamacpp_full'
        state_loaded = False

        # Try to load llama.cpp state if provided
        if llama_state:
            try:
                logger.info(f"🔄 Loading llama.cpp state from DGX prefill...")

                # Decode base64 state
                state_bytes_encoded = base64.b64decode(llama_state)
                encoded_size_mb = len(state_bytes_encoded) / 1024 / 1024

                logger.info(f"   Encoded state size: {encoded_size_mb:.1f} MB")

                # Decompress if needed
                if is_compressed:
                    import zlib
                    decompression_start = time.time()
                    state_bytes = zlib.decompress(state_bytes_encoded)
                    decompression_time = time.time() - decompression_start
                    state_size_mb = len(state_bytes) / 1024 / 1024
                    logger.info(f"   Decompressed to: {state_size_mb:.1f} MB ({decompression_time:.3f}s)")
                else:
                    state_bytes = state_bytes_encoded
                    state_size_mb = encoded_size_mb
                    decompression_time = 0.0
                    logger.info(f"   Uncompressed state (no decompression needed)")

                # Load state using C API directly
                try:
                    from llama_cpp import llama_cpp
                    import ctypes

                    # Convert bytes to ctypes buffer (optimized with from_buffer_copy)
                    load_start = time.time()
                    state_buffer = (ctypes.c_uint8 * len(state_bytes)).from_buffer_copy(state_bytes)
                    buffer_copy_time = time.time() - load_start

                    logger.info(f"   Loading {len(state_bytes)} bytes into model context... (buffer copy: {buffer_copy_time:.3f}s)")

                    # Use C API to set state data
                    ctx = model._ctx.ctx
                    api_start = time.time()
                    bytes_read = llama_cpp.llama_state_set_data(ctx, state_buffer, len(state_bytes))
                    api_time = time.time() - api_start

                    if bytes_read > 0:
                        # Update model's internal token counter
                        model.n_tokens = n_tokens_from_prefill
                        logger.info(f"✅ State loaded! Read {bytes_read} bytes via C API ({api_time:.3f}s)")
                        logger.info(f"   Set n_tokens to {n_tokens_from_prefill}")

                        state_loaded = True
                        method = 'llamacpp_with_state'
                    else:
                        raise RuntimeError(f"llama_state_set_data returned {bytes_read}")

                except Exception as load_error:
                    logger.warning(f"⚠️  State loading failed: {load_error}")
                    import traceback
                    traceback.print_exc()
                    state_loaded = False

            except Exception as e:
                logger.warning(f"⚠️  Failed to load state: {e}")
                logger.warning(f"   Falling back to full generation")
                state_loaded = False

        if state_loaded:
            # State loaded - only need to decode (generate new tokens)
            logger.info(f"🚀 Decoding with existing KV cache from DGX...")

            # IMPORTANT: Pass the original prompt even though state is loaded
            # The KV cache will make re-processing the prompt very fast
            # This ensures the context is properly set up for generation
            logger.info(f"   Re-evaluating prompt with loaded KV cache...")

            response = model(
                prompt,  # Use original prompt (KV cache makes this fast)
                max_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                echo=False,
                stop=["</s>", "<|im_end|>", "<|endoftext|>", "\n\n\n"],
            )

            generated_text = response['choices'][0]['text']
            tokens_generated = response['usage']['completion_tokens']
            prompt_tokens = response['usage']['prompt_tokens']

            logger.info(f"   Prompt tokens (from cache): {prompt_tokens}")
            logger.info(f"   New tokens generated: {tokens_generated}")

        else:
            # No state or state loading failed - do full generation
            logger.info(f"🚀 Full generation (prefill + decode) with llama.cpp...")
            logger.info(f"   Prompt length: {len(prompt)} chars")

            response = model(
                prompt,
                max_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k,
                echo=False,
                stop=["</s>", "<|im_end|>", "<|endoftext|>", "\n\n\n"],
            )

            generated_text = response['choices'][0]['text']
            tokens_generated = response['usage']['completion_tokens']
            prompt_tokens = response['usage']['prompt_tokens']

        decode_time = time.time() - start_time
        tokens_per_sec = tokens_generated / decode_time if decode_time > 0 else 0

        logger.info(f"✅ Generation completed in {decode_time:.3f}s")
        logger.info(f"   Generated tokens: {tokens_generated}")
        logger.info(f"   Speed: {tokens_per_sec:.1f} tok/s")
        logger.info(f"   Method: {method}")

        return jsonify({
            'generated_text': prompt + generated_text,
            'decode_time': decode_time,
            'tokens_generated': tokens_generated,
            'tokens_per_sec': tokens_per_sec,
            'model': model_path,
            'method': method,
            'state_loaded': state_loaded,
            'metrics': {
                'completion_tokens': tokens_generated,
                'decode_time_s': decode_time,
                'tokens_per_sec': tokens_per_sec
            }
        })

    except Exception as e:
        logger.error(f"❌ Generation failed: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/generate', methods=['POST'])
def generate_full():
    """
    Full generation (prefill + decode with llama.cpp)
    This is the same as /decode since llama.cpp handles both phases
    """
    return decode()

@app.route('/status', methods=['GET'])
def get_status():
    """Get detailed server status"""
    import platform
    import psutil

    status = {
        'server': 'llama.cpp Decode Server',
        'model': model_path,
        'loaded': model_loaded,
        'backend': 'llama.cpp',
        'platform': platform.system(),
        'architecture': platform.machine(),
    }

    # Add memory info
    try:
        mem = psutil.virtual_memory()
        status['memory_total_gb'] = mem.total / 1e9
        status['memory_available_gb'] = mem.available / 1e9
        status['memory_percent'] = mem.percent
    except:
        pass

    return jsonify(status)

@app.route('/benchmark', methods=['POST'])
def benchmark():
    """
    Run a quick benchmark to test performance
    """
    global model, model_loaded

    if not model_loaded:
        return jsonify({'error': 'Model not loaded'}), 503

    try:
        test_prompt = "def fibonacci(n):"
        max_tokens = 50

        logger.info("🏃 Running benchmark...")

        start_time = time.time()
        response = model(
            test_prompt,
            max_tokens=max_tokens,
            temperature=0.7,
            echo=False,
        )

        total_time = time.time() - start_time
        tokens = response['usage']['completion_tokens']
        tokens_per_sec = tokens / total_time if total_time > 0 else 0

        return jsonify({
            'benchmark_complete': True,
            'test_prompt': test_prompt,
            'tokens_generated': tokens,
            'total_time_s': total_time,
            'tokens_per_sec': tokens_per_sec,
            'model': model_path
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='llama.cpp Decode Server for Mac Studio')
    parser.add_argument('--model', type=str, required=True, help='Path to GGUF model file')
    parser.add_argument('--host', type=str, default='0.0.0.0', help='Host to bind')
    parser.add_argument('--port', type=int, default=8001, help='Port to bind')
    parser.add_argument('--n-ctx', type=int, default=4096, help='Context window size')
    parser.add_argument('--n-gpu-layers', type=int, default=-1, help='GPU layers (-1 for all)')

    args = parser.parse_args()

    print("🖥️  Starting llama.cpp Decode Server for Mac Studio...")
    print(f"📡 Model: {args.model}")
    print(f"🌐 Binding to: {args.host}:{args.port}")
    print(f"📏 Context window: {args.n_ctx}")
    print()

    if load_model(args.model, n_ctx=args.n_ctx, n_gpu_layers=args.n_gpu_layers):
        print("🚀 Server ready! Starting Flask app...")
        print()
        print("📝 Note: llama.cpp doesn't support external KV cache injection.")
        print("   The server will do efficient prefill+decode in one pass.")
        print()
        app.run(host=args.host, port=args.port, debug=False, threaded=True)
    else:
        print("❌ Failed to start server - model loading failed")
        print()
        print("💡 Make sure you have a GGUF model file.")
        print("   Download from: https://huggingface.co/models?search=gguf")
        sys.exit(1)
