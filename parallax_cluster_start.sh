#!/bin/bash
# Parallax Cluster Startup Script
# Starts all nodes in the cluster

echo "=============================================="
echo "Starting Parallax Cluster"
echo "=============================================="

MODEL="${1:-Qwen/Qwen3-0.6B}"
echo "Model: $MODEL"
echo ""

# Start Mac 1 (Scheduler)
echo "[1/4] Starting Mac 1 (Scheduler - localhost)..."
cd /Users/humphrjk/parallax
source venv/bin/activate
nohup parallax run -m "$MODEL" -n 4 --host 0.0.0.0 > /tmp/parallax_scheduler.log 2>&1 &
echo "  ✓ Scheduler starting (log: /tmp/parallax_scheduler.log)"

# Wait for scheduler to initialize
echo "  Waiting for scheduler to initialize..."
sleep 15

# Check if scheduler is running
if curl -s http://localhost:3001/ > /dev/null 2>&1; then
    echo "  ✓ Scheduler is online"
else
    echo "  ⚠ Scheduler may still be starting, continuing..."
fi

# Start Mac 2 (Worker)
echo ""
echo "[2/4] Starting Mac 2 (Worker - 169.254.150.102)..."
ssh humphrjk@169.254.150.102 "cd /Users/humphrjk/parallax && source venv/bin/activate && nohup parallax join > /tmp/parallax_worker.log 2>&1 &"
echo "  ✓ Worker starting (log: /tmp/parallax_worker.log on Mac 2)"

# Start spark-2935 Docker container
echo ""
echo "[3/4] Starting spark-2935 (169.254.150.106)..."
ssh humphrjk@169.254.150.106 "sudo docker run -d --gpus all --network host gradientservice/parallax:latest-spark parallax join" && echo "  ✓ Docker container started" || echo "  ✗ Failed to start container"

# Start RR191562IP01 Docker container
echo ""
echo "[4/4] Starting RR191562IP01 (169.254.150.105)..."
ssh humphrjk@169.254.150.105 "sudo docker run -d --gpus all --network host gradientservice/parallax:latest-spark parallax join" && echo "  ✓ Docker container started" || echo "  ✗ Failed to start container"

# Wait for nodes to join
echo ""
echo "Waiting for nodes to join cluster..."
sleep 30

# Check cluster status
echo ""
echo "=============================================="
echo "Cluster Status"
echo "=============================================="
if curl -s http://localhost:3001/ > /dev/null 2>&1; then
    echo "✓ Scheduler: Online (http://169.254.150.101:3001)"

    # Test inference
    echo ""
    echo "Testing inference..."
    RESULT=$(curl -s -X POST 'http://localhost:3001/v1/chat/completions' \
        -H 'Content-Type: application/json' \
        -d '{"messages":[{"role":"user","content":"Say hello"}],"max_tokens":20}' 2>/dev/null)

    if echo "$RESULT" | grep -q "choices"; then
        echo "✓ Inference working"
    else
        echo "⚠ Inference may still be initializing"
    fi
else
    echo "✗ Scheduler not responding"
fi

echo ""
echo "=============================================="
echo "Parallax Cluster Started"
echo "Dashboard: http://169.254.150.101:3001"
echo "=============================================="
