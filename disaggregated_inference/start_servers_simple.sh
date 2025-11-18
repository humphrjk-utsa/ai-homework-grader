#!/bin/bash
# Simple server startup without systemd

SPARK3_HOST="jamiehumphries@169.254.150.105"
SPARK4_HOST="jamiehumphries@169.254.150.106"

echo "=========================================="
echo "Starting Prefill Servers (Simple Mode)"
echo "=========================================="
echo ""

# Start Spark 3 (Qwen)
echo "Starting Spark 3 (Qwen)..."
ssh $SPARK3_HOST "nohup python3 ~/prefill_server_ollama.py --model hopephoto/qwen3-coder-30b-a3b-instruct_q8:latest --port 8000 --host 0.0.0.0 > ~/prefill.log 2>&1 &"
echo "✅ Spark 3 started"

# Start Spark 4 (GPT-OSS)
echo "Starting Spark 4 (GPT-OSS)..."
ssh $SPARK4_HOST "nohup python3 ~/prefill_server_ollama.py --model gemma3:27b-it-q8_0 --port 8000 --host 0.0.0.0 > ~/prefill.log 2>&1 &"
echo "✅ Spark 4 started"

echo ""
echo "Waiting for servers to start..."
sleep 5

echo ""
echo "Testing servers..."
for ip in "169.254.150.105" "169.254.150.106"; do
    echo -n "  $ip: "
    if curl -s --connect-timeout 3 http://$ip:8000/health > /dev/null 2>&1; then
        echo "✅ Running"
    else
        echo "⚠️ Not responding yet (check logs)"
    fi
done

echo ""
echo "=========================================="
echo "Servers Started!"
echo "=========================================="
echo ""
echo "To check logs:"
echo "  ssh $SPARK3_HOST 'tail -f ~/prefill.log'"
echo "  ssh $SPARK4_HOST 'tail -f ~/prefill.log'"
echo ""
echo "To stop servers:"
echo "  ssh $SPARK3_HOST 'pkill -f prefill_server'"
echo "  ssh $SPARK4_HOST 'pkill -f prefill_server'"
echo ""
