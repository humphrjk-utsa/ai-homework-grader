#!/bin/bash
# Install llama.cpp Python bindings on all Mac Studios and DGX Sparks

echo "════════════════════════════════════════════════════════════════════"
echo "LLAMA.CPP INSTALLATION SCRIPT"
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
MAC_STUDIO_1="169.254.150.101"
MAC_STUDIO_2="169.254.150.102"
DGX_SPARK_3="169.254.150.105"
DGX_SPARK_4="169.254.150.106"

install_llamacpp_local() {
    echo -e "${BOLD}Installing llama.cpp on LOCAL machine...${NC}"
    echo ""

    # Check Python version
    PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
    echo "   Python version: $PYTHON_VERSION"

    # Detect platform
    OS=$(uname -s)
    ARCH=$(uname -m)
    echo "   Platform: $OS ($ARCH)"

    # Install based on platform
    if [[ "$OS" == "Darwin" ]]; then
        echo -e "   ${GREEN}Installing for macOS with Metal support...${NC}"

        # Check for Homebrew
        if ! command -v brew &> /dev/null; then
            echo -e "   ${YELLOW}Homebrew not found. Installing Homebrew...${NC}"
            /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        fi

        # Install dependencies
        echo "   Installing build dependencies..."
        brew install cmake

        # Install llama-cpp-python with Metal support
        echo "   Installing llama-cpp-python with Metal acceleration..."
        CMAKE_ARGS="-DLLAMA_METAL=on" pip install --upgrade --force-reinstall llama-cpp-python --no-cache-dir

    elif [[ "$OS" == "Linux" ]]; then
        # Check for NVIDIA GPU
        if command -v nvidia-smi &> /dev/null; then
            echo -e "   ${GREEN}Installing for Linux with CUDA support...${NC}"

            # Install with CUDA
            CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip install --upgrade --force-reinstall llama-cpp-python --no-cache-dir
        else
            echo -e "   ${YELLOW}Installing for Linux (CPU only)...${NC}"
            pip install --upgrade llama-cpp-python
        fi
    else
        echo -e "   ${YELLOW}Installing standard version...${NC}"
        pip install --upgrade llama-cpp-python
    fi

    # Verify installation
    echo ""
    echo -n "   Verifying installation: "
    if python3 -c "import llama_cpp; print(llama_cpp.__version__)" 2>/dev/null; then
        VERSION=$(python3 -c "import llama_cpp; print(llama_cpp.__version__)")
        echo -e "${GREEN}✓ Success${NC} (v$VERSION)"
    else
        echo -e "${RED}✗ Failed${NC}"
        return 1
    fi

    # Install additional dependencies
    echo ""
    echo "   Installing additional dependencies..."
    pip install flask psutil

    echo ""
}

install_llamacpp_remote() {
    local machine_name=$1
    local machine_ip=$2

    echo -e "${BOLD}Installing llama.cpp on ${machine_name} (${machine_ip})...${NC}"
    echo ""

    # Test SSH connectivity
    if ! ssh -o ConnectTimeout=5 -o BatchMode=yes humphrjk@${machine_ip} "echo 'SSH OK'" &>/dev/null; then
        echo -e "   ${RED}✗ SSH connection failed${NC}"
        echo -e "      ${YELLOW}Skipping ${machine_name}${NC}"
        echo ""
        return 1
    fi

    # Detect platform and install
    ssh humphrjk@${machine_ip} bash << 'ENDSSH'
        # Detect platform
        OS=$(uname -s)
        ARCH=$(uname -m)
        echo "   Platform: $OS ($ARCH)"

        # Install based on platform
        if [[ "$OS" == "Darwin" ]]; then
            echo "   Installing for macOS with Metal support..."

            # Check for Homebrew
            if ! command -v brew &> /dev/null; then
                echo "   Installing Homebrew..."
                /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
            fi

            # Install dependencies
            brew install cmake 2>/dev/null || true

            # Install llama-cpp-python with Metal
            CMAKE_ARGS="-DLLAMA_METAL=on" pip3 install --upgrade --force-reinstall llama-cpp-python --no-cache-dir

        elif [[ "$OS" == "Linux" ]]; then
            # Check for NVIDIA GPU
            if command -v nvidia-smi &> /dev/null; then
                echo "   Installing for Linux with CUDA support..."
                CMAKE_ARGS="-DLLAMA_CUBLAS=on" pip3 install --upgrade --force-reinstall llama-cpp-python --no-cache-dir
            else
                echo "   Installing for Linux (CPU only)..."
                pip3 install --upgrade llama-cpp-python
            fi
        fi

        # Install additional dependencies
        pip3 install flask psutil

        # Verify
        echo ""
        echo -n "   Verifying: "
        if python3 -c "import llama_cpp; print('OK')" 2>/dev/null; then
            VERSION=$(python3 -c "import llama_cpp; print(llama_cpp.__version__)")
            echo "✓ Success (v$VERSION)"
        else
            echo "✗ Failed"
            exit 1
        fi
ENDSSH

    if [ $? -eq 0 ]; then
        echo -e "   ${GREEN}✓ Installation successful on ${machine_name}${NC}"
    else
        echo -e "   ${RED}✗ Installation failed on ${machine_name}${NC}"
    fi
    echo ""
}

# Install on local machine
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}INSTALLING ON LOCAL MACHINE${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════${NC}"
echo ""
install_llamacpp_local

# Install on remote machines
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}INSTALLING ON REMOTE MACHINES${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════════${NC}"
echo ""

# Mac Studios (primary decode servers)
install_llamacpp_remote "Mac Studio 1" "$MAC_STUDIO_1"
install_llamacpp_remote "Mac Studio 2" "$MAC_STUDIO_2"

# DGX Sparks (optional - for hybrid mode)
echo -e "${YELLOW}Note: DGX Sparks use HuggingFace Transformers for prefill.${NC}"
echo -e "${YELLOW}Installing llama.cpp is optional.${NC}"
echo ""
read -p "Install llama.cpp on DGX Sparks? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    install_llamacpp_remote "DGX Spark 3" "$DGX_SPARK_3"
    install_llamacpp_remote "DGX Spark 4" "$DGX_SPARK_4"
fi

echo ""
echo "════════════════════════════════════════════════════════════════════"
echo -e "${BOLD}INSTALLATION COMPLETE${NC}"
echo "════════════════════════════════════════════════════════════════════"
echo ""
echo -e "${GREEN}✓ llama.cpp installed successfully!${NC}"
echo ""
echo "Next steps:"
echo "  1. Download GGUF models: ./download_gguf_models.sh"
echo "  2. Start decode servers: ./start_mac_servers_llamacpp.sh"
echo "  3. Verify status: python3 check_status.py"
echo ""
