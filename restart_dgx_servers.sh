#!/bin/bash
# Script to restart DGX prefill servers with the keep_alive fix

echo "🔄 Restarting DGX Prefill Servers..."
echo ""

# DGX Spark 3 (Qwen)
echo "📡 DGX Spark 3 (169.254.150.105) - Qwen 3.0 Coder"
echo "   Killing old process..."
ssh jamiehumphries@169.254.150.105 "pkill -f 'prefill_server_ollama.py --model hopephoto'"
sleep 2

echo "   Starting new process..."
ssh jamiehumphries@169.254.150.105 "cd /home/jamiehumphries && nohup python3 prefill_server_ollama.py --model hopephoto/qwen3-coder-30b-a3b-instruct_q8:latest --host 0.0.0.0 --port 8000 > /tmp/prefill_qwen.log 2>&1 &"
sleep 2

echo "   Testing..."
curl -X POST http://169.254.150.105:8000/prefill -H "Content-Type: application/json" -d '{"prompt": "test"}' -s | jq -r '.prefill_time'
echo ""

# DGX Spark 4 (GPT-OSS)
echo "📡 DGX Spark 4 (169.254.150.106) - GPT-OSS 120B"
echo "   Killing old process..."
ssh jamiehumphries@169.254.150.106 "pkill -f 'prefill_server_ollama.py --model gpt-oss'"
sleep 2

echo "   Starting new process..."
ssh jamiehumphries@169.254.150.106 "cd /home/jamiehumphries && nohup python3 prefill_server_ollama.py --model gpt-oss:120b --host 0.0.0.0 --port 8000 > /tmp/prefill_gpt.log 2>&1 &"
sleep 2

echo "   Testing..."
curl -X POST http://169.254.150.106:8000/prefill -H "Content-Type: application/json" -d '{"prompt": "test"}' -s | jq -r '.prefill_time'
echo ""

echo "✅ Done! Both servers restarted."
echo ""
echo "Expected times:"
echo "  - DGX Spark 3 (Qwen): ~0.8s"
echo "  - DGX Spark 4 (GPT-OSS): ~1.4s"
