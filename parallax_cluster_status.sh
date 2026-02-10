#!/bin/bash
# Parallax Cluster Status Script
# Checks status of all nodes

echo "=============================================="
echo "Parallax Cluster Status"
echo "=============================================="

# Check Mac 1 (Scheduler)
echo ""
echo "[Mac 1 - Scheduler (169.254.150.101)]"
if curl -s http://169.254.150.101:3001/ > /dev/null 2>&1; then
    echo "  Status: ✓ Online"
    PROCS=$(pgrep -f "parallax" | wc -l | tr -d ' ')
    echo "  Processes: $PROCS"
else
    echo "  Status: ✗ Offline"
fi

# Check Mac 2 (Worker)
echo ""
echo "[Mac 2 - Worker (169.254.150.102)]"
MAC2_PROCS=$(ssh humphrjk@169.254.150.102 "pgrep -f 'parallax' | wc -l" 2>/dev/null | tr -d ' ')
if [ "$MAC2_PROCS" -gt 0 ] 2>/dev/null; then
    echo "  Status: ✓ Running"
    echo "  Processes: $MAC2_PROCS"
else
    echo "  Status: ✗ Not running"
fi

# Check spark-2935
echo ""
echo "[spark-2935 (169.254.150.106)]"
SPARK1_CONTAINERS=$(ssh humphrjk@169.254.150.106 "sudo docker ps -q --filter ancestor=gradientservice/parallax:latest-spark | wc -l" 2>/dev/null | tr -d ' ')
if [ "$SPARK1_CONTAINERS" -gt 0 ] 2>/dev/null; then
    echo "  Status: ✓ Running"
    echo "  Containers: $SPARK1_CONTAINERS"
else
    echo "  Status: ✗ Not running"
fi

# Check RR191562IP01
echo ""
echo "[RR191562IP01 (169.254.150.105)]"
SPARK2_CONTAINERS=$(ssh humphrjk@169.254.150.105 "sudo docker ps -q --filter ancestor=gradientservice/parallax:latest-spark | wc -l" 2>/dev/null | tr -d ' ')
if [ "$SPARK2_CONTAINERS" -gt 0 ] 2>/dev/null; then
    echo "  Status: ✓ Running"
    echo "  Containers: $SPARK2_CONTAINERS"
else
    echo "  Status: ✗ Not running"
fi

# Test inference if scheduler is online
echo ""
echo "=============================================="
if curl -s http://169.254.150.101:3001/ > /dev/null 2>&1; then
    echo "Testing inference..."
    START=$(python3 -c "import time; print(time.time())")
    RESULT=$(curl -s -X POST 'http://169.254.150.101:3001/v1/chat/completions' \
        -H 'Content-Type: application/json' \
        -d '{"messages":[{"role":"user","content":"Say OK"}],"max_tokens":10,"chat_template_kwargs":{"enable_thinking":false}}' 2>/dev/null)
    END=$(python3 -c "import time; print(time.time())")

    if echo "$RESULT" | grep -q "choices"; then
        TOKENS=$(echo "$RESULT" | python3 -c "import sys,json; print(json.load(sys.stdin)['usage']['completion_tokens'])" 2>/dev/null || echo "?")
        TIME=$(python3 -c "print(f'{$END - $START:.2f}')")
        echo "✓ Inference working ($TOKENS tokens in ${TIME}s)"
    else
        echo "✗ Inference failed"
    fi
else
    echo "Scheduler offline - cannot test inference"
fi
echo "=============================================="
