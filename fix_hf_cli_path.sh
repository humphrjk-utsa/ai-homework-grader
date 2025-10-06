#!/bin/bash
# Find huggingface-cli and add to PATH on Mac Studio 2

echo "🔍 Finding huggingface-cli on Mac Studio 2..."
echo ""

ssh jamiehumphries@10.55.0.2 << 'EOF'
# Find where it's installed
echo "Searching for huggingface-cli..."
HF_CLI=$(find ~/Library/Python -name huggingface-cli 2>/dev/null | head -1)

if [ -z "$HF_CLI" ]; then
    HF_CLI=$(find /usr/local -name huggingface-cli 2>/dev/null | head -1)
fi

if [ -z "$HF_CLI" ]; then
    HF_CLI=$(python3 -c "import site; print(site.USER_BASE + '/bin/huggingface-cli')" 2>/dev/null)
fi

if [ -f "$HF_CLI" ]; then
    echo "✅ Found at: $HF_CLI"
    HF_DIR=$(dirname "$HF_CLI")
    
    # Add to .zshrc
    if ! grep -q "$HF_DIR" ~/.zshrc 2>/dev/null; then
        echo "" >> ~/.zshrc
        echo "# Huggingface CLI" >> ~/.zshrc
        echo "export PATH=\"$HF_DIR:\$PATH\"" >> ~/.zshrc
        echo "✅ Added to ~/.zshrc"
    else
        echo "✅ Already in ~/.zshrc"
    fi
    
    # Test it
    echo ""
    echo "Testing with full path:"
    $HF_CLI --version
    
else
    echo "❌ Not found. Installing with pip3..."
    pip3 install --user huggingface_hub[cli]
    
    # Try again
    HF_CLI=$(python3 -c "import site; print(site.USER_BASE + '/bin/huggingface-cli')")
    if [ -f "$HF_CLI" ]; then
        echo "✅ Installed at: $HF_CLI"
        HF_DIR=$(dirname "$HF_CLI")
        echo "export PATH=\"$HF_DIR:\$PATH\"" >> ~/.zshrc
    fi
fi
EOF

echo ""
echo "✅ Done! Now logout and login, or run: source ~/.zshrc"
