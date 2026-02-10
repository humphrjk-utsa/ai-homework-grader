#!/bin/bash
# Verify llama.cpp installation across all machines in the cluster

echo "════════════════════════════════════════════════════════════════════"
echo "LLAMA.CPP INSTALLATION VERIFICATION"
echo "════════════════════════════════════════════════════════════════════"
echo ""

# ANSI color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Machine configurations
declare -A MACHINES
MACHINES=(
    ["Mac Studio 1"]="169.254.150.101"
    ["Mac Studio 2"]="169.254.150.102"
    ["DGX Spark 3"]="169.254.150.105"
    ["DGX Spark 4"]="169.254.150.106"
)

check_llamacpp_local() {
    echo -e "${BOLD}Checking llama.cpp on LOCAL machine...${NC}"
    echo ""

    # Check Python llama-cpp-python
    echo -n "   Python llama-cpp-python: "
    if python3 -c "import llama_cpp" 2>/dev/null; then
        VERSION=$(python3 -c "import llama_cpp; print(llama_cpp.__version__)" 2>/dev/null)
        echo -e "${GREEN}✓ Installed${NC} (v${VERSION})"
    else
        echo -e "${RED}✗ Not installed${NC}"
        echo -e "      ${YELLOW}Install with: pip install llama-cpp-python${NC}"
    fi

    # Check llama.cpp binary
    echo -n "   llama.cpp CLI binary: "
    if command -v llama-cli &> /dev/null; then
        LLAMA_PATH=$(which llama-cli)
        echo -e "${GREEN}✓ Found${NC} at $LLAMA_PATH"
    elif command -v llama &> /dev/null; then
        LLAMA_PATH=$(which llama)
        echo -e "${GREEN}✓ Found${NC} at $LLAMA_PATH"
    elif [ -f "./llama.cpp/build/bin/llama-cli" ]; then
        echo -e "${GREEN}✓ Found${NC} at ./llama.cpp/build/bin/llama-cli"
    else
        echo -e "${RED}✗ Not found${NC}"
        echo -e "      ${YELLOW}Build from: https://github.com/ggerganov/llama.cpp${NC}"
    fi

    # Check Ollama (alternative)
    echo -n "   Ollama (alternative): "
    if command -v ollama &> /dev/null; then
        OLLAMA_VERSION=$(ollama --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1)
        echo -e "${GREEN}✓ Installed${NC} (v${OLLAMA_VERSION})"
    else
        echo -e "${YELLOW}○ Not installed${NC}"
    fi

    # Check for GGUF models
    echo ""
    echo "   Searching for GGUF models..."

    # Common model directories
    MODEL_DIRS=(
        "$HOME/.cache/lm-studio/models"
        "$HOME/.ollama/models"
        "$HOME/.cache/huggingface/hub"
        "./models"
        "../models"
        "$HOME/models"
    )

    FOUND_MODELS=0
    for dir in "${MODEL_DIRS[@]}"; do
        if [ -d "$dir" ]; then
            GGUF_COUNT=$(find "$dir" -name "*.gguf" 2>/dev/null | wc -l | tr -d ' ')
            if [ "$GGUF_COUNT" -gt 0 ]; then
                echo -e "      ${GREEN}✓${NC} Found $GGUF_COUNT GGUF model(s) in $dir"
                FOUND_MODELS=$((FOUND_MODELS + GGUF_COUNT))
            fi
        fi
    done

    if [ "$FOUND_MODELS" -eq 0 ]; then
        echo -e "      ${YELLOW}○ No GGUF models found in common directories${NC}"
    else
        echo -e "      ${GREEN}Total: $FOUND_MODELS GGUF model(s)${NC}"
    fi

    echo ""
}

check_llamacpp_remote() {
    local machine_name=$1
    local machine_ip=$2

    echo -e "${BOLD}Checking llama.cpp on ${machine_name} (${machine_ip})...${NC}"
    echo ""

    # Test SSH connectivity
    if ! ssh -o ConnectTimeout=5 -o BatchMode=yes -o StrictHostKeyChecking=no humphrjk@${machine_ip} "echo 'SSH OK'" &>/dev/null; then
        echo -e "   ${RED}✗ SSH connection failed${NC}"
        echo -e "      ${YELLOW}Please verify SSH access: ssh humphrjk@${machine_ip}${NC}"
        echo ""
        return 1
    fi

    # Check Python llama-cpp-python
    echo -n "   Python llama-cpp-python: "
    if ssh humphrjk@${machine_ip} "python3 -c 'import llama_cpp' 2>/dev/null"; then
        VERSION=$(ssh humphrjk@${machine_ip} "python3 -c 'import llama_cpp; print(llama_cpp.__version__)' 2>/dev/null")
        echo -e "${GREEN}✓ Installed${NC} (v${VERSION})"
    else
        echo -e "${RED}✗ Not installed${NC}"
        echo -e "      ${YELLOW}Install with: ssh humphrjk@${machine_ip} 'pip install llama-cpp-python'${NC}"
    fi

    # Check llama.cpp binary
    echo -n "   llama.cpp CLI binary: "
    if ssh humphrjk@${machine_ip} "command -v llama-cli &>/dev/null"; then
        LLAMA_PATH=$(ssh humphrjk@${machine_ip} "which llama-cli")
        echo -e "${GREEN}✓ Found${NC} at $LLAMA_PATH"
    elif ssh humphrjk@${machine_ip} "command -v llama &>/dev/null"; then
        LLAMA_PATH=$(ssh humphrjk@${machine_ip} "which llama")
        echo -e "${GREEN}✓ Found${NC} at $LLAMA_PATH"
    else
        echo -e "${RED}✗ Not found${NC}"
    fi

    # Check Ollama
    echo -n "   Ollama (alternative): "
    if ssh humphrjk@${machine_ip} "command -v ollama &>/dev/null"; then
        OLLAMA_VERSION=$(ssh humphrjk@${machine_ip} "ollama --version 2>/dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -1")
        echo -e "${GREEN}✓ Installed${NC} (v${OLLAMA_VERSION})"

        # List Ollama models
        echo "      Installed models:"
        ssh humphrjk@${machine_ip} "ollama list 2>/dev/null" | while read line; do
            if [[ $line != NAME* ]]; then
                MODEL_NAME=$(echo $line | awk '{print $1}')
                if [[ -n "$MODEL_NAME" ]]; then
                    echo -e "         - $MODEL_NAME"
                fi
            fi
        done
    else
        echo -e "${YELLOW}○ Not installed${NC}"
    fi

    # Check for GGUF models
    echo ""
    echo "   Searching for GGUF models..."
    GGUF_COUNT=$(ssh humphrjk@${machine_ip} "find ~ -name '*.gguf' 2>/dev/null | wc -l | tr -d ' '")
    if [ "$GGUF_COUNT" -gt 0 ]; then
        echo -e "      ${GREEN}✓ Found $GGUF_COUNT GGUF model(s)${NC}"
    else
        echo -e "      ${YELLOW}○ No GGUF models found${NC}"
    fi

    echo ""
}

# Check local machine
check_llamacpp_local

# Check remote machines
for machine_name in "${!MACHINES[@]}"; do
    machine_ip="${MACHINES[$machine_name]}"
    check_llamacpp_remote "$machine_name" "$machine_ip"
done

echo "════════════════════════════════════════════════════════════════════"
echo -e "${BOLD}CURRENT IMPLEMENTATION STATUS${NC}"
echo "════════════════════════════════════════════════════════════════════"
echo ""
echo -e "${BLUE}The disaggregated inference system currently uses:${NC}"
echo ""
echo "   • DGX Sparks (Prefill):  HuggingFace Transformers"
echo "     └─ File: prefill_server_dgx.py"
echo "     └─ Uses: AutoModelForCausalLM with PyTorch"
echo ""
echo "   • Mac Studios (Decode):  MLX (Apple Metal)"
echo "     └─ File: decode_server_mac.py"
echo "     └─ Uses: mlx_lm.load() and mlx_lm.generate()"
echo ""
echo -e "${YELLOW}⚠ NOTE: llama.cpp is NOT currently integrated into the${NC}"
echo -e "${YELLOW}   disaggregated architecture. It's only used in:${NC}"
echo "   • PC-based standalone client (models/pc_llamacpp_client.py)"
echo ""
echo -e "${BLUE}Alternative backend available:${NC}"
echo "   • Ollama (both prefill and decode)"
echo "     └─ Files: prefill_server_ollama.py, decode_server_ollama.py"
echo ""

echo "════════════════════════════════════════════════════════════════════"
echo -e "${BOLD}RECOMMENDATIONS${NC}"
echo "════════════════════════════════════════════════════════════════════"
echo ""
echo "To integrate llama.cpp into your disaggregated architecture:"
echo ""
echo "1. Create llama.cpp-based prefill server:"
echo "   • Implement KV cache extraction from llama.cpp"
echo "   • Deploy to DGX Sparks"
echo ""
echo "2. Create llama.cpp-based decode server:"
echo "   • Implement KV cache ingestion for decode-only"
echo "   • Deploy to Mac Studios"
echo ""
echo "3. Or use Ollama (already implemented):"
echo "   • Start servers: ./start_dgx_servers_ollama.sh"
echo "   •              ./start_mac_servers_ollama.sh"
echo ""
echo "════════════════════════════════════════════════════════════════════"
