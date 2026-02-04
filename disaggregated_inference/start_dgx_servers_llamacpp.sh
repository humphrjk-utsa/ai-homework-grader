#!/bin/bash
# Start llama.cpp prefill servers on DGX Sparks

echo "════════════════════════════════════════════════════════════════════"
echo "STARTING LLAMA.CPP PREFILL SERVERS ON DGX SPARKS"
echo "════════════════════════════════════════════════════════════════════"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'
BOLD='\033[1m'

# Server configurations
DGX_SPARK_3_IP="169.254.150.105"
DGX_SPARK_4_IP="169.254.150.106"

# Model paths on DGX Sparks (EXISTING GGUF models)
QWEN_MODEL_PATH="/home/humphrjk/models/qwen3-coder-30b-q8.gguf"
GPT_OSS_MODEL_PATH="/home/humphrjk/models/unsloth_gpt-oss-120b-GGUF_UD-Q8_K_XL_gpt-oss-120b-UD-Q8_K_XL-00001-of-00002.gguf"

# Server settings
PORT=8080  # Use 8080 since Ollama is on 8000
N_CTX=4096
N_GPU_LAYERS=-1  # Use all GPU layers (CUDA acceleration)

echo -e "${BOLD}Configuration:${NC}"
echo "   DGX Spark 3: $DGX_SPARK_3_IP:$PORT (Qwen-32B prefill)"
echo "   DGX Spark 4: $DGX_SPARK_4_IP:$PORT (Llama-70B prefill)"
echo ""

start_dgx_server() {
    local server_name=$1
    local server_ip=$2
    local model_path=$3
    local model_desc=$4

    echo -e "${BOLD}Starting ${server_name}...${NC}"
    echo "   IP: $server_ip"
    echo "   Model: $model_desc"
    echo "   Path: $model_path"
    echo ""

    # Check SSH connectivity
    if ! ssh -o ConnectTimeout=5 -o BatchMode=yes humphrjk@${server_ip} "echo 'OK'" &>/dev/null; then
        echo -e "   ${RED}✗ Cannot connect to ${server_ip}${NC}"
        echo ""
        return 1
    fi

    # Start server via SSH
    ssh humphrjk@${server_ip} << ENDSSH
        set -e

        # Navigate to project directory
        cd ~/ai-homework-grader/disaggregated_inference || {
            echo "Error: Project directory not found"
            exit 1
        }

        # Check if model exists
        if [ ! -f "${model_path}" ]; then
            echo "Error: Model file not found: ${model_path}"
            echo "Please download and copy GGUF models first"
            echo "  Run: ./download_gguf_models.sh"
            echo "  Then: scp ~/models/gguf/*.gguf humphrjk@${server_ip}:~/models/gguf/"
            exit 1
        fi

        # Check llama-cpp-python installation
        if ! python3 -c "import llama_cpp" 2>/dev/null; then
            echo "Error: llama-cpp-python not installed"
            echo "Run: ./install_llamacpp.sh"
            exit 1
        fi

        # Create logs directory
        mkdir -p ~/logs

        # Stop existing server
        pkill -f "prefill_server_llamacpp.py" 2>/dev/null || true
        sleep 2

        # Start server in background
        nohup python3 prefill_server_llamacpp.py \\
            --model "${model_path}" \\
            --host 0.0.0.0 \\
            --port ${PORT} \\
            --n-ctx ${N_CTX} \\
            --n-gpu-layers ${N_GPU_LAYERS} \\
            > ~/logs/prefill_llamacpp.log 2>&1 &

        # Get PID
        sleep 3
        SERVER_PID=\$(pgrep -f "prefill_server_llamacpp.py" | head -1)

        if [ -n "\$SERVER_PID" ]; then
            echo "Server started with PID: \$SERVER_PID"
            echo "Waiting for model to load..."
            sleep 10

            # Test health endpoint
            for i in {1..30}; do
                if curl -s http://localhost:${PORT}/health >/dev/null 2>&1; then
                    echo "Server is responding!"
                    exit 0
                fi
                sleep 2
            done

            echo "Warning: Server started but not responding to health checks"
            echo "Check logs: tail ~/logs/prefill_llamacpp.log"
        else
            echo "Error: Failed to start server"
            echo "Check logs: tail ~/logs/prefill_llamacpp.log"
            exit 1
        fi
ENDSSH

    if [ $? -eq 0 ]; then
        echo -e "   ${GREEN}✓ ${server_name} started successfully${NC}"
    else
        echo -e "   ${RED}✗ ${server_name} failed to start${NC}"
        return 1
    fi

    echo ""
}

# Start DGX Spark 3 (Qwen for code analysis)
start_dgx_server \
    "DGX Spark 3" \
    "$DGX_SPARK_3_IP" \
    "$QWEN_MODEL_PATH" \
    "Qwen3-Coder-30B Q8"

# Start DGX Spark 4 (GPT-OSS for feedback)
start_dgx_server \
    "DGX Spark 4" \
    "$DGX_SPARK_4_IP" \
    "$GPT_OSS_MODEL_PATH" \
    "GPT-OSS-120B Q8"

# Verify all servers
echo ""
echo "════════════════════════════════════════════════════════════════════"
echo -e "${BOLD}VERIFYING SERVERS${NC}"
echo "════════════════════════════════════════════════════════════════════"
echo ""

sleep 3

# Check DGX Spark 3
echo -n "DGX Spark 3 ($DGX_SPARK_3_IP:$PORT): "
if curl -s "http://${DGX_SPARK_3_IP}:${PORT}/health" >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Healthy${NC}"
    RESPONSE=$(curl -s "http://${DGX_SPARK_3_IP}:${PORT}/health")
    echo "   $RESPONSE" | python3 -m json.tool 2>/dev/null || echo "   $RESPONSE"
else
    echo -e "${RED}✗ Not responding${NC}"
fi
echo ""

# Check DGX Spark 4
echo -n "DGX Spark 4 ($DGX_SPARK_4_IP:$PORT): "
if curl -s "http://${DGX_SPARK_4_IP}:${PORT}/health" >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Healthy${NC}"
    RESPONSE=$(curl -s "http://${DGX_SPARK_4_IP}:${PORT}/health")
    echo "   $RESPONSE" | python3 -m json.tool 2>/dev/null || echo "   $RESPONSE"
else
    echo -e "${RED}✗ Not responding${NC}"
fi
echo ""

echo "════════════════════════════════════════════════════════════════════"
echo -e "${BOLD}STARTUP COMPLETE${NC}"
echo "════════════════════════════════════════════════════════════════════"
echo ""
echo -e "${GREEN}llama.cpp prefill servers are now running!${NC}"
echo ""
echo "Architecture:"
echo "   DGX Spark 3 [llama.cpp Prefill] → Mac Studio 2 [llama.cpp Decode] (Qwen)"
echo "   DGX Spark 4 [llama.cpp Prefill] → Mac Studio 1 [llama.cpp Decode] (Llama)"
echo ""
echo -e "${BOLD}CRITICAL:${NC} Both DGX and Mac in each pair MUST have IDENTICAL GGUF models!"
echo ""
echo "Verify models match:"
echo "   ssh humphrjk@${DGX_SPARK_3_IP} 'md5sum ~/models/gguf/qwen*.gguf'"
echo "   ssh humphrjk@169.254.150.102 'md5 ~/models/gguf/qwen*.gguf'"
echo ""
echo "Next steps:"
echo "   1. Start Mac decode servers: ./start_mac_servers_llamacpp.sh"
echo "   2. Test system: python3 check_status.py"
echo "   3. Run benchmark: python3 benchmark_disaggregated.py"
echo ""
echo "View logs:"
echo "   ssh humphrjk@${DGX_SPARK_3_IP} 'tail -f ~/logs/prefill_llamacpp.log'"
echo "   ssh humphrjk@${DGX_SPARK_4_IP} 'tail -f ~/logs/prefill_llamacpp.log'"
echo ""
