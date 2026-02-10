#!/bin/bash
# Start llama.cpp decode servers on Mac Studios

echo "════════════════════════════════════════════════════════════════════"
echo "STARTING LLAMA.CPP DECODE SERVERS ON MAC STUDIOS"
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
MAC_STUDIO_1_IP="169.254.150.101"
MAC_STUDIO_2_IP="169.254.150.102"

# Model paths on Mac Studios (EXISTING GGUF models)
QWEN_MODEL_PATH="${HOME}/models/gguf/qwen3-coder-30b-q8.gguf"
GPT_OSS_MODEL_PATH="${HOME}/Library/Caches/llama.cpp/unsloth_gpt-oss-120b-GGUF_UD-Q8_K_XL_gpt-oss-120b-UD-Q8_K_XL-00001-of-00002.gguf"

# Server settings
PORT=8081  # Use 8081 since Ollama/old servers are on 8001
N_CTX=4096  # Context window
N_GPU_LAYERS=-1  # Use Metal acceleration on Mac

echo -e "${BOLD}Configuration:${NC}"
echo "   Mac Studio 1: $MAC_STUDIO_1_IP:$PORT (Llama-3.1-70B for feedback)"
echo "   Mac Studio 2: $MAC_STUDIO_2_IP:$PORT (Qwen2.5-Coder-32B for code analysis)"
echo ""

# Function to start server on Mac
start_mac_server() {
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
            echo "Please download GGUF models first:"
            echo "  ./download_gguf_models.sh"
            exit 1
        fi

        # Stop existing server
        pkill -f "decode_server_llamacpp.py" 2>/dev/null || true
        sleep 2

        # Start server in background
        nohup python3 decode_server_llamacpp.py \\
            --model "${model_path}" \\
            --host 0.0.0.0 \\
            --port ${PORT} \\
            --n-ctx ${N_CTX} \\
            --n-gpu-layers ${N_GPU_LAYERS} \\
            > ~/logs/decode_llamacpp.log 2>&1 &

        # Get PID
        sleep 3
        SERVER_PID=\$(pgrep -f "decode_server_llamacpp.py" | head -1)

        if [ -n "\$SERVER_PID" ]; then
            echo "Server started with PID: \$SERVER_PID"
            echo "Waiting for model to load..."
            sleep 5

            # Test health endpoint
            for i in {1..30}; do
                if curl -s http://localhost:${PORT}/health >/dev/null 2>&1; then
                    echo "Server is responding!"
                    exit 0
                fi
                sleep 1
            done

            echo "Warning: Server started but not responding to health checks"
            echo "Check logs: tail ~/logs/decode_llamacpp.log"
        else
            echo "Error: Failed to start server"
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

# Create logs directory on Mac Studios
echo "Creating logs directories..."
ssh humphrjk@${MAC_STUDIO_1_IP} "mkdir -p ~/logs" 2>/dev/null || true
ssh humphrjk@${MAC_STUDIO_2_IP} "mkdir -p ~/logs" 2>/dev/null || true
echo ""

# Start Mac Studio 2 (Qwen for code analysis)
start_mac_server \
    "Mac Studio 2" \
    "$MAC_STUDIO_2_IP" \
    "$QWEN_MODEL_PATH" \
    "Qwen3-Coder-30B Q8"

# Start Mac Studio 1 (GPT-OSS for feedback)
start_mac_server \
    "Mac Studio 1" \
    "$MAC_STUDIO_1_IP" \
    "$GPT_OSS_MODEL_PATH" \
    "GPT-OSS-120B Q8"

# Verify all servers
echo ""
echo "════════════════════════════════════════════════════════════════════"
echo -e "${BOLD}VERIFYING SERVERS${NC}"
echo "════════════════════════════════════════════════════════════════════"
echo ""

sleep 3

# Check Mac Studio 1
echo -n "Mac Studio 1 ($MAC_STUDIO_1_IP:$PORT): "
if curl -s "http://${MAC_STUDIO_1_IP}:${PORT}/health" >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Healthy${NC}"
    RESPONSE=$(curl -s "http://${MAC_STUDIO_1_IP}:${PORT}/health")
    echo "   $RESPONSE" | python3 -m json.tool 2>/dev/null || echo "   $RESPONSE"
else
    echo -e "${RED}✗ Not responding${NC}"
fi
echo ""

# Check Mac Studio 2
echo -n "Mac Studio 2 ($MAC_STUDIO_2_IP:$PORT): "
if curl -s "http://${MAC_STUDIO_2_IP}:${PORT}/health" >/dev/null 2>&1; then
    echo -e "${GREEN}✓ Healthy${NC}"
    RESPONSE=$(curl -s "http://${MAC_STUDIO_2_IP}:${PORT}/health")
    echo "   $RESPONSE" | python3 -m json.tool 2>/dev/null || echo "   $RESPONSE"
else
    echo -e "${RED}✗ Not responding${NC}"
fi
echo ""

echo "════════════════════════════════════════════════════════════════════"
echo -e "${BOLD}STARTUP COMPLETE${NC}"
echo "════════════════════════════════════════════════════════════════════"
echo ""
echo -e "${GREEN}llama.cpp decode servers are now running!${NC}"
echo ""
echo "Architecture:"
echo "   DGX Spark 3 → [Prefill] → Mac Studio 2 [llama.cpp Decode - Qwen]"
echo "   DGX Spark 4 → [Prefill] → Mac Studio 1 [llama.cpp Decode - Llama]"
echo ""
echo "Next steps:"
echo "   1. Start DGX prefill servers: ./start_dgx_servers.sh"
echo "   2. Test system: python3 check_status.py"
echo "   3. Run benchmark: python3 test_disaggregated_inference.py"
echo ""
echo "View logs:"
echo "   ssh humphrjk@${MAC_STUDIO_1_IP} 'tail -f ~/logs/decode_llamacpp.log'"
echo "   ssh humphrjk@${MAC_STUDIO_2_IP} 'tail -f ~/logs/decode_llamacpp.log'"
echo ""
echo "Stop servers:"
echo "   ./stop_all_servers.sh"
echo ""
