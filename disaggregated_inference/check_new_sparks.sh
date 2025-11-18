#!/bin/bash
# Check status of new DGX Sparks

echo "=========================================="
echo "Checking New DGX Sparks Status"
echo "=========================================="
echo ""

# Check connectivity
echo "1. Network Connectivity:"
echo "   Spark 3 (169.254.150.105):"
if ping -c 1 -W 1 169.254.150.105 > /dev/null 2>&1; then
    echo "      ✅ Reachable"
else
    echo "      ❌ Not reachable"
fi

echo "   Spark 4 (169.254.150.106):"
if ping -c 1 -W 1 169.254.150.106 > /dev/null 2>&1; then
    echo "      ✅ Reachable"
else
    echo "      ❌ Not reachable"
fi

echo ""
echo "2. Ollama Service (port 11434):"
for ip in 169.254.150.105 169.254.150.106; do
    echo "   $ip:"
    if nc -z -w 2 $ip 11434 2>/dev/null; then
        echo "      ✅ Ollama running"
        # Try to get version
        curl -s http://$ip:11434/api/version 2>/dev/null | head -1
    else
        echo "      ❌ Ollama not running"
    fi
done

echo ""
echo "3. Prefill Server (port 8000):"
for ip in 169.254.150.105 169.254.150.106; do
    echo "   $ip:"
    if nc -z -w 2 $ip 8000 2>/dev/null; then
        echo "      ✅ Prefill server running"
        # Try to get health status
        curl -s http://$ip:8000/health 2>/dev/null || echo "      (No health endpoint)"
    else
        echo "      ❌ Prefill server not running"
    fi
done

echo ""
echo "=========================================="
echo "Next Steps:"
echo "=========================================="
echo ""
echo "If Ollama is not running on the Sparks:"
echo "  1. SSH to each Spark"
echo "  2. Install Ollama: curl -fsSL https://ollama.com/install.sh | sh"
echo "  3. Start Ollama: sudo systemctl start ollama"
echo "  4. Pull models: ollama pull hopephoto/qwen3-coder-30b-a3b-instruct_q8:latest"
echo ""
echo "If Prefill server is not running:"
echo "  1. Copy prefill_server_ollama.py to each Spark"
echo "  2. Start server: python3 prefill_server_ollama.py --model MODEL --port 8000"
echo ""
echo "For detailed instructions, see: SETUP_NEW_SPARKS.md"
echo ""
