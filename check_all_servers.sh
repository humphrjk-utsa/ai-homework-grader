#!/bin/bash
# Check status of all disaggregated inference servers

echo "=========================================="
echo "🔍 Checking Disaggregated Inference System"
echo "=========================================="
echo ""

# Function to check server
check_server() {
    local name=$1
    local host=$2
    local port=$3
    
    echo -n "Checking $name ($host:$port)... "
    
    if timeout 3 curl -s http://$host:$port/health > /dev/null 2>&1; then
        echo "✅ RUNNING"
        # Get detailed status
        status=$(curl -s http://$host:$port/health 2>/dev/null)
        if [ ! -z "$status" ]; then
            echo "   $status" | python3 -m json.tool 2>/dev/null | grep -E "(model|status|loaded)" | sed 's/^/   /'
        fi
    else
        echo "❌ NOT RESPONDING"
    fi
    echo ""
}

echo "📡 PREFILL SERVERS (DGX Sparks):"
echo "-------------------------------------------"
check_server "DGX Spark 1 (Qwen)" "169.254.150.103" "8000"
check_server "DGX Spark 2 (GPT-OSS)" "169.254.150.104" "8000"

echo ""
echo "🍎 DECODE SERVERS (Mac Studios):"
echo "-------------------------------------------"
check_server "Mac Studio 1 (GPT-OSS)" "169.254.150.101" "8001"
check_server "Mac Studio 2 (Qwen)" "169.254.150.102" "8001"

echo ""
echo "=========================================="
echo "📋 SUMMARY"
echo "=========================================="
echo ""
echo "To start servers, you need to:"
echo ""
echo "1. On DGX Spark 1 (169.254.150.103):"
echo "   cd /path/to/ai-homework-grader/disaggregated_inference"
echo "   python3 prefill_server_ollama.py --model qwen3-coder:30b --port 8000"
echo ""
echo "2. On DGX Spark 2 (169.254.150.104):"
echo "   cd /path/to/ai-homework-grader/disaggregated_inference"
echo "   python3 prefill_server_ollama.py --model gpt-oss:120b --port 8000"
echo ""
echo "3. On Mac Studio 1 (169.254.150.101):"
echo "   cd /path/to/ai-homework-grader/disaggregated_inference"
echo "   python3 decode_server_ollama.py --model gpt-oss:120b --port 8001"
echo ""
echo "4. On Mac Studio 2 (169.254.150.102):"
echo "   cd /path/to/ai-homework-grader/disaggregated_inference"
echo "   python3 decode_server_ollama.py --model qwen3-coder:30b --port 8001"
echo ""
