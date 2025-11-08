#!/bin/bash
# Deploy disaggregated inference files to all machines

echo "🚀 Deploying Disaggregated Inference System"
echo "==========================================="

# Check if we're in the right directory
if [ ! -f "disaggregated_inference/prefill_server_dgx.py" ]; then
    echo "❌ Error: Run this from the project root directory"
    exit 1
fi

# Create directories on remote machines
echo ""
echo "📁 Creating directories..."

ssh humphrjk@169.254.150.103 "mkdir -p ~/disaggregated_inference ~/logs"
ssh humphrjk@169.254.150.104 "mkdir -p ~/disaggregated_inference ~/logs"
ssh humphrjk@169.254.150.102 "mkdir -p ~/disaggregated_inference ~/logs"
mkdir -p ~/logs

echo "✅ Directories created"

# Deploy to DGX Spark 1
echo ""
echo "📡 Deploying to DGX Spark 1 (169.254.150.103)..."
scp disaggregated_inference/prefill_server_dgx.py humphrjk@169.254.150.103:~/disaggregated_inference/
echo "✅ DGX Spark 1 deployed"

# Deploy to DGX Spark 2
echo ""
echo "📡 Deploying to DGX Spark 2 (169.254.150.104)..."
scp disaggregated_inference/prefill_server_dgx.py humphrjk@169.254.150.104:~/disaggregated_inference/
echo "✅ DGX Spark 2 deployed"

# Deploy to Mac Studio 2
echo ""
echo "📡 Deploying to Mac Studio 2 (169.254.150.102)..."
scp disaggregated_inference/decode_server_mac.py humphrjk@169.254.150.102:~/disaggregated_inference/
echo "✅ Mac Studio 2 deployed"

# Mac Studio 1 is local, just ensure file is there
echo ""
echo "📡 Mac Studio 1 (local) - files already present"

# Check Python dependencies
echo ""
echo "🔍 Checking dependencies..."

echo ""
echo "DGX Spark 1:"
ssh humphrjk@169.254.150.103 "python3 -c 'import flask, torch, transformers' && echo '  ✅ Dependencies OK' || echo '  ❌ Missing dependencies - run: pip install flask torch transformers accelerate'"

echo ""
echo "DGX Spark 2:"
ssh humphrjk@169.254.150.104 "python3 -c 'import flask, torch, transformers' && echo '  ✅ Dependencies OK' || echo '  ❌ Missing dependencies - run: pip install flask torch transformers accelerate'"

echo ""
echo "Mac Studio 1 (local):"
python3 -c 'import flask, mlx.core, mlx_lm' && echo '  ✅ Dependencies OK' || echo '  ❌ Missing dependencies - run: pip install flask mlx mlx-lm'

echo ""
echo "Mac Studio 2:"
ssh humphrjk@169.254.150.102 "python3 -c 'import flask, mlx.core, mlx_lm' && echo '  ✅ Dependencies OK' || echo '  ❌ Missing dependencies - run: pip install flask mlx mlx-lm'"

# Verify models exist
echo ""
echo "🔍 Checking models..."

echo ""
echo "DGX Spark 1 (Qwen):"
ssh humphrjk@169.254.150.103 "ls ~/models/fp4/qwen3-coder-30b-fp4/config.json >/dev/null 2>&1 && echo '  ✅ Model found' || echo '  ❌ Model not found at ~/models/fp4/qwen3-coder-30b-fp4/'"

echo ""
echo "DGX Spark 2 (GPT-OSS):"
ssh humphrjk@169.254.150.104 "ls ~/models/fp4/gpt-oss-120b-fp4/config.json >/dev/null 2>&1 && echo '  ✅ Model found' || echo '  ❌ Model not found at ~/models/fp4/gpt-oss-120b-fp4/'"

echo ""
echo "Mac Studio 1 (Qwen):"
ls ~/models/fp4/qwen3-coder-30b-fp4/config.json >/dev/null 2>&1 && echo '  ✅ Model found' || echo '  ❌ Model not found at ~/models/fp4/qwen3-coder-30b-fp4/'

echo ""
echo "Mac Studio 2 (GPT-OSS):"
ssh humphrjk@169.254.150.102 "ls ~/models/fp4/gpt-oss-120b-fp4/config.json >/dev/null 2>&1 && echo '  ✅ Model found' || echo '  ❌ Model not found at ~/models/fp4/gpt-oss-120b-fp4/'"

# Summary
echo ""
echo "==========================================="
echo "✅ Deployment Complete!"
echo "==========================================="
echo ""
echo "📝 Next steps:"
echo "1. Start DGX servers:  ./disaggregated_inference/start_dgx_servers.sh"
echo "2. Start Mac servers:  ./disaggregated_inference/start_mac_servers.sh"
echo "3. Check status:       python3 disaggregated_inference/check_status.py"
echo "4. Run tests:          python3 disaggregated_inference/test_system.py"
echo ""
echo "📚 Documentation:"
echo "  Quick Start:  disaggregated_inference/QUICKSTART.md"
echo "  Deployment:   disaggregated_inference/DEPLOYMENT.md"
echo "  Architecture: disaggregated_inference/README.md"
