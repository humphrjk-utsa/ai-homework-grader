#!/bin/bash
# Verify existing llama.cpp and model setup on all machines

echo "════════════════════════════════════════════════════════════════════"
echo "VERIFYING EXISTING LLAMA.CPP AND MODEL SETUP"
echo "════════════════════════════════════════════════════════════════════"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'
BOLD='\033[1m'

# Machines
declare -A MACHINES
MACHINES=(
    ["Local"]="localhost"
    ["Mac Studio 1"]="169.254.150.101"
    ["Mac Studio 2"]="169.254.150.102"
    ["DGX Spark 3"]="169.254.150.105"
    ["DGX Spark 4"]="169.254.150.106"
)

check_machine() {
    local machine_name=$1
    local machine_ip=$2

    echo -e "${BOLD}${machine_name} (${machine_ip})${NC}"
    echo "─────────────────────────────────────────────────────────────"

    if [ "$machine_ip" = "localhost" ]; then
        # Local machine
        echo -n "  llama-cpp-python: "
        if python3 -c "import llama_cpp; print(llama_cpp.__version__)" 2>/dev/null; then
            VERSION=$(python3 -c "import llama_cpp; print(llama_cpp.__version__)")
            echo -e "${GREEN}✓ v${VERSION}${NC}"
        else
            echo -e "${RED}✗ Not installed${NC}"
        fi

        echo ""
        echo "  GGUF Models found:"
        GGUF_FILES=$(find ~/models ~/Library/Caches/llama.cpp -name "*.gguf" 2>/dev/null | wc -l | tr -d ' ')
        if [ "$GGUF_FILES" -gt 0 ]; then
            find ~/models ~/Library/Caches/llama.cpp -name "*.gguf" 2>/dev/null | while read file; do
                SIZE=$(ls -lh "$file" | awk '{print $5}')
                BASENAME=$(basename "$file")
                echo -e "    ${GREEN}✓${NC} $BASENAME ($SIZE)"
            done
        else
            echo -e "    ${YELLOW}○ No GGUF files found${NC}"
        fi

    else
        # Remote machine
        if ! ssh -o ConnectTimeout=5 -o BatchMode=yes humphrjk@${machine_ip} "echo 'OK'" &>/dev/null 2>&1; then
            echo -e "  ${RED}✗ Cannot connect via SSH${NC}"
            echo ""
            return 1
        fi

        echo -n "  llama-cpp-python: "
        if ssh humphrjk@${machine_ip} "python3 -c 'import llama_cpp; print(llama_cpp.__version__)'" 2>/dev/null; then
            VERSION=$(ssh humphrjk@${machine_ip} "python3 -c 'import llama_cpp; print(llama_cpp.__version__)'" 2>/dev/null)
            echo -e "${GREEN}✓ v${VERSION}${NC}"
        else
            echo -e "${RED}✗ Not installed${NC}"
        fi

        echo ""
        echo "  GGUF Models found:"
        ssh humphrjk@${machine_ip} "find ~/models ~/Library/Caches/llama.cpp -name '*.gguf' 2>/dev/null" | while read file; do
            SIZE=$(ssh humphrjk@${machine_ip} "ls -lh '$file' 2>/dev/null | awk '{print \$5}'")
            BASENAME=$(basename "$file")
            echo -e "    ${GREEN}✓${NC} $BASENAME ($SIZE)"
        done

        GGUF_COUNT=$(ssh humphrjk@${machine_ip} "find ~/models ~/Library/Caches/llama.cpp -name '*.gguf' 2>/dev/null | wc -l | tr -d ' '")
        if [ "$GGUF_COUNT" -eq 0 ]; then
            echo -e "    ${YELLOW}○ No GGUF files found${NC}"
        fi
    fi

    echo ""
}

# Check all machines
for machine_name in "${!MACHINES[@]}"; do
    machine_ip="${MACHINES[$machine_name]}"
    check_machine "$machine_name" "$machine_ip"
done

echo "════════════════════════════════════════════════════════════════════"
echo -e "${BOLD}SUMMARY${NC}"
echo "════════════════════════════════════════════════════════════════════"
echo ""
echo "Models identified:"
echo ""
echo "LOCAL:"
echo "  GPT-OSS-120B Q8_K_XL (2 parts, ~60GB total)"
echo "    - Part 1: ~/Library/Caches/llama.cpp/unsloth_gpt-oss-120b-GGUF_UD-Q8_K_XL_gpt-oss-120b-UD-Q8_K_XL-00001-of-00002.gguf"
echo "    - Part 2: ~/Library/Caches/llama.cpp/unsloth_gpt-oss-120b-GGUF_UD-Q8_K_XL_gpt-oss-120b-UD-Q8_K_XL-00002-of-00002.gguf"
echo ""
echo "  Qwen3-Coder-30B-Instruct: ~/models/Qwen3-Coder-30B-A3B-Instruct-8bit/ (MLX format)"
echo "    Note: This is MLX format, not GGUF. Need to find or convert to GGUF for llama.cpp"
echo ""
echo "REQUIRED:"
echo "  ✓ GPT-OSS-120B Q8 GGUF - Found locally"
echo "  ? Qwen3-Coder-30B GGUF - Need to locate or convert"
echo ""
