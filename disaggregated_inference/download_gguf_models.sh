#!/bin/bash
# Download GGUF models for llama.cpp decode servers

echo "════════════════════════════════════════════════════════════════════"
echo "GGUF MODEL DOWNLOAD SCRIPT"
echo "════════════════════════════════════════════════════════════════════"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'
BOLD='\033[1m'

# Model directory
MODELS_DIR="${HOME}/models/gguf"
mkdir -p "$MODELS_DIR"

echo -e "${BOLD}Model directory: ${MODELS_DIR}${NC}"
echo ""

# Check for huggingface-cli
if ! command -v huggingface-cli &> /dev/null; then
    echo -e "${YELLOW}Installing huggingface-hub CLI...${NC}"
    pip install --upgrade huggingface-hub[cli]
fi

echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}AVAILABLE MODELS${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════${NC}"
echo ""

cat << 'EOF'
Recommended GGUF models for your setup:

1. Qwen2.5-Coder-32B (for code analysis)
   ├─ Q4_K_M: ~18GB (balanced speed/quality)
   ├─ Q5_K_M: ~22GB (better quality)
   └─ Q6_K:   ~25GB (high quality)

2. Qwen2.5-72B-Instruct (alternative large model)
   ├─ Q4_K_M: ~41GB (balanced)
   └─ Q5_K_M: ~50GB (better quality)

3. Llama-3.1-70B-Instruct (for feedback generation)
   ├─ Q4_K_M: ~39GB (balanced)
   └─ Q5_K_M: ~48GB (better quality)

4. Qwen2.5-7B-Instruct (lightweight alternative)
   └─ Q4_K_M: ~4.4GB (fast, good for testing)

EOF

echo ""
echo -e "${BOLD}Which models would you like to download?${NC}"
echo ""

# Function to download model
download_model() {
    local model_name=$1
    local model_file=$2
    local description=$3

    echo ""
    echo -e "${BOLD}Downloading: ${model_name}${NC}"
    echo -e "   ${description}"
    echo -e "   File: ${model_file}"
    echo ""

    # Create subdirectory
    model_dir="${MODELS_DIR}/$(echo $model_name | tr '/' '_')"
    mkdir -p "$model_dir"

    # Download using huggingface-cli
    huggingface-cli download \
        "$model_name" \
        "$model_file" \
        --local-dir "$model_dir" \
        --local-dir-use-symlinks False

    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✓ Downloaded successfully${NC}"
        echo -e "   Location: ${model_dir}/${model_file}"

        # Create a symlink with friendly name
        FRIENDLY_NAME=$(echo $model_file | sed 's/.gguf$//')
        ln -sf "${model_dir}/${model_file}" "${MODELS_DIR}/${FRIENDLY_NAME}.gguf" 2>/dev/null

        return 0
    else
        echo -e "${RED}✗ Download failed${NC}"
        return 1
    fi
}

# Menu
PS3=$'\n'"Select a model (or 'q' to quit): "
options=(
    "Qwen2.5-Coder-32B-Instruct (Q4_K_M) - Code analysis [RECOMMENDED]"
    "Qwen2.5-Coder-32B-Instruct (Q5_K_M) - Code analysis (higher quality)"
    "Llama-3.1-70B-Instruct (Q4_K_M) - Feedback generation [RECOMMENDED]"
    "Llama-3.1-70B-Instruct (Q5_K_M) - Feedback generation (higher quality)"
    "Qwen2.5-7B-Instruct (Q4_K_M) - Lightweight testing"
    "Qwen2.5-72B-Instruct (Q4_K_M) - Large model (requires more RAM)"
    "Download all recommended models"
    "Quit"
)

select opt in "${options[@]}"
do
    case $opt in
        "Qwen2.5-Coder-32B-Instruct (Q4_K_M) - Code analysis [RECOMMENDED]")
            download_model \
                "Qwen/Qwen2.5-Coder-32B-Instruct-GGUF" \
                "qwen2.5-coder-32b-instruct-q4_k_m.gguf" \
                "Qwen2.5-Coder-32B Q4_K_M (~18GB) - Optimized for code analysis"
            ;;

        "Qwen2.5-Coder-32B-Instruct (Q5_K_M) - Code analysis (higher quality)")
            download_model \
                "Qwen/Qwen2.5-Coder-32B-Instruct-GGUF" \
                "qwen2.5-coder-32b-instruct-q5_k_m.gguf" \
                "Qwen2.5-Coder-32B Q5_K_M (~22GB) - Higher quality"
            ;;

        "Llama-3.1-70B-Instruct (Q4_K_M) - Feedback generation [RECOMMENDED]")
            download_model \
                "meta-llama/Llama-3.1-70B-Instruct-GGUF" \
                "llama-3.1-70b-instruct-q4_k_m.gguf" \
                "Llama-3.1-70B Q4_K_M (~39GB) - Excellent for feedback"
            ;;

        "Llama-3.1-70B-Instruct (Q5_K_M) - Feedback generation (higher quality)")
            download_model \
                "meta-llama/Llama-3.1-70B-Instruct-GGUF" \
                "llama-3.1-70b-instruct-q5_k_m.gguf" \
                "Llama-3.1-70B Q5_K_M (~48GB) - Higher quality"
            ;;

        "Qwen2.5-7B-Instruct (Q4_K_M) - Lightweight testing")
            download_model \
                "Qwen/Qwen2.5-7B-Instruct-GGUF" \
                "qwen2.5-7b-instruct-q4_k_m.gguf" \
                "Qwen2.5-7B Q4_K_M (~4.4GB) - Fast, good for testing"
            ;;

        "Qwen2.5-72B-Instruct (Q4_K_M) - Large model (requires more RAM)")
            download_model \
                "Qwen/Qwen2.5-72B-Instruct-GGUF" \
                "qwen2.5-72b-instruct-q4_k_m.gguf" \
                "Qwen2.5-72B Q4_K_M (~41GB) - Very large model"
            ;;

        "Download all recommended models")
            download_model \
                "Qwen/Qwen2.5-Coder-32B-Instruct-GGUF" \
                "qwen2.5-coder-32b-instruct-q4_k_m.gguf" \
                "Qwen2.5-Coder-32B Q4_K_M"

            download_model \
                "meta-llama/Llama-3.1-70B-Instruct-GGUF" \
                "llama-3.1-70b-instruct-q4_k_m.gguf" \
                "Llama-3.1-70B Q4_K_M"
            ;;

        "Quit")
            break
            ;;

        *) echo -e "${RED}Invalid option${NC}";;
    esac
done

echo ""
echo "════════════════════════════════════════════════════════════════════"
echo -e "${BOLD}DOWNLOADED MODELS${NC}"
echo "════════════════════════════════════════════════════════════════════"
echo ""

if [ -d "$MODELS_DIR" ]; then
    echo -e "${GREEN}Models in ${MODELS_DIR}:${NC}"
    echo ""
    ls -lh "$MODELS_DIR"/*.gguf 2>/dev/null | awk '{printf "   %s  %s\n", $5, $9}' || echo "   No GGUF models found"
fi

echo ""
echo -e "${BOLD}Next Steps:${NC}"
echo ""
echo "1. Copy models to Mac Studios:"
echo "   scp ${MODELS_DIR}/*qwen*coder*.gguf humphrjk@169.254.150.102:~/models/gguf/"
echo "   scp ${MODELS_DIR}/*llama*.gguf humphrjk@169.254.150.101:~/models/gguf/"
echo ""
echo "2. Start llama.cpp decode servers:"
echo "   ./start_mac_servers_llamacpp.sh"
echo ""
echo "3. Verify status:"
echo "   python3 check_status.py"
echo ""
