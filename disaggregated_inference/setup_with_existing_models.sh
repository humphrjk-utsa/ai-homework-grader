#!/usr/bin/env bash
# Setup disaggregated llama.cpp using EXISTING models
# - GPT-OSS-120B Q8_K_XL (already downloaded)
# - Qwen3-Coder-30B-Instruct (need GGUF version)

set -e

echo "════════════════════════════════════════════════════════════════════"
echo "DISAGGREGATED LLAMA.CPP SETUP WITH EXISTING MODELS"
echo "════════════════════════════════════════════════════════════════════"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'
BOLD='\033[1m'

# Model paths (LOCAL)
GPT_OSS_PART1="$HOME/Library/Caches/llama.cpp/unsloth_gpt-oss-120b-GGUF_UD-Q8_K_XL_gpt-oss-120b-UD-Q8_K_XL-00001-of-00002.gguf"
GPT_OSS_PART2="$HOME/Library/Caches/llama.cpp/unsloth_gpt-oss-120b-GGUF_UD-Q8_K_XL_gpt-oss-120b-UD-Q8_K_XL-00002-of-00002.gguf"

# Target directories
MODELS_DIR="$HOME/models/gguf"
mkdir -p "$MODELS_DIR"

echo -e "${BOLD}Step 1: Verify Existing Models${NC}"
echo "─────────────────────────────────────────────────────────────"
echo ""

# Check GPT-OSS-120B
echo -n "  GPT-OSS-120B Q8 GGUF: "
if [ -f "$GPT_OSS_PART1" ] && [ -f "$GPT_OSS_PART2" ]; then
    SIZE1=$(ls -lh "$GPT_OSS_PART1" | awk '{print $5}')
    SIZE2=$(ls -lh "$GPT_OSS_PART2" | awk '{print $5}')
    echo -e "${GREEN}✓ Found${NC} (Part 1: $SIZE1, Part 2: $SIZE2)"

    # Note: This is a 2-part GGUF file
    echo -e "    ${YELLOW}Note: This is a 2-part GGUF file${NC}"
    echo -e "    ${YELLOW}llama.cpp should handle multi-part files automatically${NC}"
else
    echo -e "${RED}✗ Not found${NC}"
    echo "  Expected locations:"
    echo "    $GPT_OSS_PART1"
    echo "    $GPT_OSS_PART2"
    exit 1
fi

echo ""

# Check Qwen3-Coder
echo -n "  Qwen3-Coder-30B GGUF: "
QWEN_GGUF=$(find ~/models ~/Library/Caches -name "*qwen*30b*.gguf" -o -name "*Qwen*30B*.gguf" 2>/dev/null | head -1)

if [ -n "$QWEN_GGUF" ]; then
    SIZE=$(ls -lh "$QWEN_GGUF" | awk '{print $5}')
    echo -e "${GREEN}✓ Found${NC} at $QWEN_GGUF ($SIZE)"
else
    echo -e "${YELLOW}○ Not found (will need to download)${NC}"
    echo ""
    echo -e "${BOLD}  Qwen3-Coder-30B GGUF Download Options:${NC}"
    echo "    1. Qwen/Qwen2.5-Coder-32B-Instruct-GGUF (HuggingFace)"
    echo "    2. Search for existing file on remote machines"
    echo ""
    read -p "  Download Qwen GGUF now? (y/N) " -n 1 -r
    echo

    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo ""
        echo -e "${BLUE}Downloading Qwen2.5-Coder-32B-Instruct Q8...${NC}"

        if ! command -v huggingface-cli &> /dev/null; then
            echo "  Installing huggingface-hub CLI..."
            pip install --upgrade "huggingface_hub[cli]"
        fi

        huggingface-cli download \
            Qwen/Qwen2.5-Coder-32B-Instruct-GGUF \
            qwen2.5-coder-32b-instruct-q8_0.gguf \
            --local-dir "$MODELS_DIR/qwen2.5-coder-32b" \
            --local-dir-use-symlinks False

        QWEN_GGUF="$MODELS_DIR/qwen2.5-coder-32b/qwen2.5-coder-32b-instruct-q8_0.gguf"
        echo -e "${GREEN}✓ Downloaded${NC}"
    else
        echo -e "${YELLOW}  Skipping download. You'll need to provide Qwen GGUF manually.${NC}"
    fi
fi

echo ""
echo -e "${BOLD}Step 2: Install llama-cpp-python${NC}"
echo "─────────────────────────────────────────────────────────────"
echo ""

# Check local installation
echo -n "  Local machine: "
if python3 -c "import llama_cpp" 2>/dev/null; then
    VERSION=$(python3 -c "import llama_cpp; print(llama_cpp.__version__)")
    echo -e "${GREEN}✓ Already installed (v${VERSION})${NC}"
else
    echo -e "${YELLOW}Installing...${NC}"

    # Detect platform
    if [[ "$OSTYPE" == "darwin"* ]]; then
        echo "  Detected macOS - installing with Metal support..."
        CMAKE_ARGS="-DLLAMA_METAL=on" pip install --upgrade llama-cpp-python
    else
        echo "  Installing standard version..."
        pip install --upgrade llama-cpp-python
    fi

    if python3 -c "import llama_cpp" 2>/dev/null; then
        echo -e "  ${GREEN}✓ Installed successfully${NC}"
    else
        echo -e "  ${RED}✗ Installation failed${NC}"
        exit 1
    fi
fi

echo ""
echo -e "${BOLD}Step 3: Organize Model Files${NC}"
echo "─────────────────────────────────────────────────────────────"
echo ""

# Create symlinks for easier access
GPT_OSS_LINK="$MODELS_DIR/gpt-oss-120b-q8.gguf"

echo "  Creating organized structure in $MODELS_DIR..."

# For multi-part GGUF, we'll use the first part as the main file
if [ -f "$GPT_OSS_PART1" ]; then
    if [ ! -L "$GPT_OSS_LINK" ] && [ ! -f "$GPT_OSS_LINK" ]; then
        ln -s "$GPT_OSS_PART1" "$GPT_OSS_LINK" 2>/dev/null || \
        cp "$GPT_OSS_PART1" "$GPT_OSS_LINK"
    fi
    echo -e "    ${GREEN}✓${NC} GPT-OSS-120B: $GPT_OSS_LINK"
fi

if [ -n "$QWEN_GGUF" ] && [ -f "$QWEN_GGUF" ]; then
    QWEN_LINK="$MODELS_DIR/qwen-coder-30b.gguf"
    if [ ! -L "$QWEN_LINK" ] && [ ! -f "$QWEN_LINK" ]; then
        ln -s "$QWEN_GGUF" "$QWEN_LINK" 2>/dev/null || \
        cp "$QWEN_GGUF" "$QWEN_LINK"
    fi
    echo -e "    ${GREEN}✓${NC} Qwen-Coder-30B: $QWEN_LINK"
fi

echo ""
echo -e "${BOLD}Step 4: Configuration Summary${NC}"
echo "─────────────────────────────────────────────────────────────"
echo ""

cat << EOF
Model Configuration:
══════════════════════════════════════════════════════════════════

Pair 1: Qwen-30B-Coder (Code Analysis)
─────────────────────────────────────────────────────────────────
  DGX Spark 3:   ${QWEN_GGUF:-NOT_FOUND}
  Mac Studio 2:  (needs copy)

Pair 2: GPT-OSS-120B (Feedback Generation)
─────────────────────────────────────────────────────────────────
  DGX Spark 4:   $GPT_OSS_PART1
  Mac Studio 1:  (needs copy)

══════════════════════════════════════════════════════════════════

IMPORTANT:
1. Multi-part GGUF files (GPT-OSS) need BOTH parts on each machine
2. Both machines in each pair must have IDENTICAL model files
3. Verify with md5 checksums before starting servers

Next Steps:
──────────────────────────────────────────────────────────────────
1. Copy models to remote machines
2. Install llama-cpp-python on DGX Sparks (CUDA) and Macs (Metal)
3. Start servers with: ./start_dgx_servers_llamacpp.sh
4. Start servers with: ./start_mac_servers_llamacpp.sh
5. Run benchmark: python3 benchmark_disaggregated.py

EOF

echo ""
read -p "Proceed with remote installation? (y/N) " -n 1 -r
echo

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Setup paused. Run this script again to continue."
    exit 0
fi

echo ""
echo -e "${BOLD}Step 5: Install on Remote Machines${NC}"
echo "─────────────────────────────────────────────────────────────"
echo ""

# Remote machines
declare -A REMOTES
REMOTES=(
    ["Mac Studio 1"]="169.254.150.101"
    ["Mac Studio 2"]="169.254.150.102"
    ["DGX Spark 3"]="169.254.150.105"
    ["DGX Spark 4"]="169.254.150.106"
)

for name in "${!REMOTES[@]}"; do
    ip="${REMOTES[$name]}"
    echo -e "${BOLD}${name} (${ip})${NC}"

    if ! ssh -o ConnectTimeout=5 -o BatchMode=yes humphrjk@${ip} "echo OK" &>/dev/null; then
        echo -e "  ${RED}✗ Cannot connect${NC}"
        echo ""
        continue
    fi

    # Detect platform
    PLATFORM=$(ssh humphrjk@${ip} "uname -s")

    # Install llama-cpp-python
    echo -n "  Installing llama-cpp-python: "

    if [[ "$PLATFORM" == "Darwin" ]]; then
        # Mac - use Metal
        ssh humphrjk@${ip} "CMAKE_ARGS='-DLLAMA_METAL=on' pip3 install --upgrade llama-cpp-python" >/dev/null 2>&1
    else
        # Linux/DGX - use CUDA
        ssh humphrjk@${ip} "CMAKE_ARGS='-DLLAMA_CUBLAS=on' pip3 install --upgrade llama-cpp-python" >/dev/null 2>&1
    fi

    if ssh humphrjk@${ip} "python3 -c 'import llama_cpp'" 2>/dev/null; then
        VERSION=$(ssh humphrjk@${ip} "python3 -c 'import llama_cpp; print(llama_cpp.__version__)'")
        echo -e "${GREEN}✓ v${VERSION}${NC}"
    else
        echo -e "${RED}✗ Failed${NC}"
    fi

    # Create models directory
    ssh humphrjk@${ip} "mkdir -p ~/models/gguf" 2>/dev/null

    echo ""
done

echo ""
echo "════════════════════════════════════════════════════════════════════"
echo -e "${BOLD}SETUP COMPLETE${NC}"
echo "════════════════════════════════════════════════════════════════════"
echo ""
echo -e "${GREEN}llama-cpp-python installed on all reachable machines!${NC}"
echo ""
echo -e "${YELLOW}NEXT: Copy model files to remote machines${NC}"
echo ""
echo "Copy GPT-OSS-120B to Mac Studio 1 and DGX Spark 4:"
echo "  scp '$GPT_OSS_PART1' humphrjk@169.254.150.101:~/models/gguf/"
echo "  scp '$GPT_OSS_PART2' humphrjk@169.254.150.101:~/models/gguf/"
echo "  scp '$GPT_OSS_PART1' humphrjk@169.254.150.106:~/models/gguf/"
echo "  scp '$GPT_OSS_PART2' humphrjk@169.254.150.106:~/models/gguf/"
echo ""

if [ -n "$QWEN_GGUF" ]; then
    echo "Copy Qwen-Coder-30B to Mac Studio 2 and DGX Spark 3:"
    echo "  scp '$QWEN_GGUF' humphrjk@169.254.150.102:~/models/gguf/"
    echo "  scp '$QWEN_GGUF' humphrjk@169.254.150.105:~/models/gguf/"
else
    echo -e "${YELLOW}Note: Qwen GGUF not found. You'll need to:${NC}"
    echo "  1. Download Qwen GGUF model"
    echo "  2. Copy to Mac Studio 2 and DGX Spark 3"
fi

echo ""
