"""
Disaggregated Prefill Server — runs on DGX Spark (Docker container)
Loads model once in bf16, serves prefill requests via HTTP.
Returns serialized KV cache + next token to the Mac for decode.

Usage (inside Docker):
    python3 /app/server.py [--model Qwen/Qwen3-Coder-30B-A3B-Instruct] [--port 8800]

Start via:
    ssh humphrjk@169.254.150.106 "sudo docker run -d --gpus all --network host \
        -v /home/humphrjk/.cache/huggingface:/root/.cache/huggingface \
        -v /path/to/this/file.py:/app/server.py \
        gradientservice/parallax:latest-spark python3 /app/server.py"
"""

import argparse
import http.server
import io
import json
import struct
import sys
import time
import traceback

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# Globals — loaded once at startup
model = None
tokenizer = None
model_id = None


class PrefillHandler(http.server.BaseHTTPRequestHandler):
    """HTTP handler for prefill requests."""

    def log_message(self, format, *args):
        # Quieter logging
        sys.stderr.write(f"[{time.strftime('%H:%M:%S')}] {format % args}\n")

    def do_GET(self):
        if self.path == "/health":
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(
                json.dumps({"status": "ready", "model": model_id}).encode()
            )
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path != "/prefill":
            self.send_error(404)
            return

        try:
            content_length = int(self.headers["Content-Length"])
            body = self.rfile.read(content_length)
            request = json.loads(body)

            # Accept either raw prompt text or chat messages
            if "messages" in request:
                prompt_text = tokenizer.apply_chat_template(
                    request["messages"], tokenize=False, add_generation_prompt=True
                )
            else:
                prompt_text = request["prompt"]

            # Tokenize
            inputs = tokenizer(prompt_text, return_tensors="pt").to(model.device)
            input_ids = inputs["input_ids"]
            prompt_tokens = input_ids.shape[1]
            print(f"Prefill: {prompt_tokens} tokens")

            # Forward pass with KV cache
            t0 = time.perf_counter()
            with torch.no_grad():
                outputs = model(input_ids, use_cache=True)
            torch.cuda.synchronize()
            prefill_time = time.perf_counter() - t0

            # Extract KV cache
            past = outputs.past_key_values
            if hasattr(past, "key_cache"):
                # DynamicCache (transformers >= 4.36)
                num_layers = len(past.key_cache)
                keys_list = [
                    past.key_cache[i].cpu().to(torch.float16).numpy()
                    for i in range(num_layers)
                ]
                values_list = [
                    past.value_cache[i].cpu().to(torch.float16).numpy()
                    for i in range(num_layers)
                ]
            else:
                # Legacy tuple format
                num_layers = len(past)
                keys_list = [
                    past[i][0].cpu().to(torch.float16).numpy()
                    for i in range(num_layers)
                ]
                values_list = [
                    past[i][1].cpu().to(torch.float16).numpy()
                    for i in range(num_layers)
                ]

            # Sample next token (greedy)
            logits = outputs.logits[:, -1, :]
            next_token = torch.argmax(logits, dim=-1).item()

            # Serialize KV cache to binary
            # Shape: each tensor is (1, num_kv_heads, seq_len, head_dim) float16
            seq_len = keys_list[0].shape[2]
            num_kv_heads = keys_list[0].shape[1]
            head_dim_k = keys_list[0].shape[3]
            head_dim_v = values_list[0].shape[3]

            buf = io.BytesIO()
            for i in range(num_layers):
                buf.write(keys_list[i].tobytes())
                buf.write(values_list[i].tobytes())
            kv_bytes = buf.getvalue()

            metadata = {
                "next_token": next_token,
                "num_layers": num_layers,
                "seq_len": seq_len,
                "num_kv_heads": num_kv_heads,
                "head_dim_k": head_dim_k,
                "head_dim_v": head_dim_v,
                "prompt_tokens": prompt_tokens,
                "prefill_time": prefill_time,
                "kv_bytes_len": len(kv_bytes),
            }
            metadata_bytes = json.dumps(metadata).encode()

            print(
                f"  prefill={prefill_time:.3f}s  layers={num_layers}  "
                f"kv_shape=({num_kv_heads},{seq_len},{head_dim_k})  "
                f"kv_size={len(kv_bytes)/1e6:.1f}MB  next_token={next_token}"
            )

            # Response: [4-byte meta_len][metadata_json][kv_bytes]
            self.send_response(200)
            self.send_header("Content-Type", "application/octet-stream")
            total = 4 + len(metadata_bytes) + len(kv_bytes)
            self.send_header("Content-Length", str(total))
            self.end_headers()
            self.wfile.write(struct.pack("<I", len(metadata_bytes)))
            self.wfile.write(metadata_bytes)
            self.wfile.write(kv_bytes)

        except Exception as e:
            traceback.print_exc()
            self.send_response(500)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode())


def main():
    global model, tokenizer, model_id

    parser = argparse.ArgumentParser(description="Disaggregated Prefill Server")
    parser.add_argument(
        "--model",
        default="Qwen/Qwen3-Coder-30B-A3B-Instruct",
        help="HuggingFace model ID",
    )
    parser.add_argument("--port", type=int, default=8800)
    args = parser.parse_args()
    model_id = args.model

    print(f"Loading model: {model_id}")
    t0 = time.time()
    tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_id,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        trust_remote_code=True,
    )
    model.eval()
    print(f"Model loaded in {time.time() - t0:.1f}s")

    # Quick GPU memory check
    if torch.cuda.is_available():
        alloc = torch.cuda.memory_allocated() / 1e9
        total = torch.cuda.get_device_properties(0).total_memory / 1e9
        print(f"GPU memory: {alloc:.1f}GB / {total:.1f}GB")

    server = http.server.HTTPServer(("0.0.0.0", args.port), PrefillHandler)
    print(f"Prefill server ready on port {args.port}")
    server.serve_forever()


if __name__ == "__main__":
    main()
