#!/bin/bash
# Install huggingface-cli on Mac Studio 2

echo "📦 Installing huggingface-cli on Mac Studio 2..."
echo ""

ssh jamiehumphries@10.55.0.2 << 'EOF'
echo "Installing huggingface_hub package..."
pip3 install --upgrade huggingface_hub

echo ""
echo "Verifying installation..."
which huggingface-cli

if [ $? -eq 0 ]; then
    echo "✅ huggingface-cli installed successfully"
    huggingface-cli --version
else
    echo "⚠️  Command not in PATH, checking Python location..."
    python3 -m huggingface_hub.commands.huggingface_cli --version
    
    if [ $? -eq 0 ]; then
        echo "✅ Can use: python3 -m huggingface_hub.commands.huggingface_cli"
    else
        echo "❌ Installation failed"
    fi
fi
EOF

echo ""
echo "✅ Done!"
