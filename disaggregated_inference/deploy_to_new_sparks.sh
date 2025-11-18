#!/bin/bash
# Automated deployment to new DGX Sparks

set -e  # Exit on error

echo "=========================================="
echo "Automated Deployment to New DGX Sparks"
echo "=========================================="
echo ""

# Configuration
SPARK3_IP="169.254.150.105"
SPARK4_IP="169.254.150.106"

# Get usernames
echo "Enter username for Spark 3 ($SPARK3_IP):"
read -p "Username: " SPARK3_USER

echo "Enter username for Spark 4 ($SPARK4_IP):"
read -p "Username: " SPARK4_USER

SPARK3_HOST="${SPARK3_USER}@${SPARK3_IP}"
SPARK4_HOST="${SPARK4_USER}@${SPARK4_IP}"

# Function to deploy to a Spark
deploy_to_spark() {
    local host=$1
    local name=$2
    local model=$3
    local model_name=$4
    
    echo ""
    echo "=========================================="
    echo "Deploying to $name"
    echo "=========================================="
    
    # Test connection
    echo "1. Testing SSH connection..."
    if ! ssh -o BatchMode=yes -o ConnectTimeout=5 $host "echo 'Connected'" > /dev/null 2>&1; then
        echo "❌ Cannot connect to $host"
        echo "   Run ./setup_ssh_keys.sh first"
        return 1
    fi
    echo "   ✅ Connected"
    
    # Check if Ollama is installed
    echo "2. Checking Ollama installation..."
    if ssh $host "which ollama" > /dev/null 2>&1; then
        echo "   ✅ Ollama already installed"
    else
        echo "   Installing Ollama..."
        ssh $host "curl -fsSL https://ollama.com/install.sh | sh"
        echo "   ✅ Ollama installed"
    fi
    
    # Start Ollama service
    echo "3. Starting Ollama service..."
    ssh $host "sudo systemctl start ollama 2>/dev/null || true"
    ssh $host "sudo systemctl enable ollama 2>/dev/null || true"
    sleep 2
    echo "   ✅ Ollama service started"
    
    # Pull model
    echo "4. Pulling model: $model_name"
    echo "   (This may take several minutes...)"
    ssh $host "ollama pull $model"
    echo "   ✅ Model pulled"
    
    # Copy prefill server
    echo "5. Copying prefill server..."
    scp -q prefill_server_ollama.py $host:~/
    echo "   ✅ Server copied"
    
    # Create systemd service
    echo "6. Creating systemd service..."
    ssh $host "cat > /tmp/prefill-server.service << 'EOF'
[Unit]
Description=Disaggregated Inference Prefill Server
After=network.target ollama.service

[Service]
Type=simple
User=$USER
WorkingDirectory=/home/$USER
ExecStart=/usr/bin/python3 /home/$USER/prefill_server_ollama.py --model $model --port 8000 --host 0.0.0.0
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF"
    
    ssh $host "sudo mv /tmp/prefill-server.service /etc/systemd/system/"
    ssh $host "sudo systemctl daemon-reload"
    ssh $host "sudo systemctl enable prefill-server"
    ssh $host "sudo systemctl start prefill-server"
    echo "   ✅ Service created and started"
    
    # Wait for server to start
    echo "7. Waiting for server to start..."
    sleep 5
    
    # Test server
    echo "8. Testing prefill server..."
    if curl -s http://${host#*@}:8000/health > /dev/null 2>&1; then
        echo "   ✅ Server responding"
    else
        echo "   ⚠️ Server not responding yet (may need more time)"
    fi
    
    echo ""
    echo "✅ $name deployment complete!"
}

# Deploy to both Sparks
echo ""
echo "This will:"
echo "  1. Install Ollama on both Sparks"
echo "  2. Pull required models"
echo "  3. Deploy and start prefill servers"
echo "  4. Create systemd services for auto-start"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Deployment cancelled"
    exit 0
fi

# Deploy Spark 3 (Qwen)
deploy_to_spark "$SPARK3_HOST" "Spark 3" \
    "hopephoto/qwen3-coder-30b-a3b-instruct_q8:latest" \
    "Qwen Coder 30B"

# Deploy Spark 4 (GPT-OSS)
deploy_to_spark "$SPARK4_HOST" "Spark 4" \
    "gemma3:27b-it-q8_0" \
    "Gemma3 27B (GPT-OSS)"

echo ""
echo "=========================================="
echo "Deployment Complete!"
echo "=========================================="
echo ""
echo "Testing all servers..."
echo ""

# Test all 4 Sparks
for ip in "169.254.150.103" "169.254.150.104" "169.254.150.105" "169.254.150.106"; do
    echo -n "  Spark at $ip: "
    if curl -s http://$ip:8000/health > /dev/null 2>&1; then
        echo "✅ Running"
    else
        echo "❌ Not responding"
    fi
done

echo ""
echo "Next step: Update config_current.json to include new Sparks"
echo ""
echo "Run: nano disaggregated_inference/config_current.json"
echo ""
echo "Add these entries to prefill_servers:"
echo '  {'
echo '    "host": "169.254.150.105",'
echo '    "port": 8000,'
echo '    "model": "qwen",'
echo '    "name": "DGX Spark 3"'
echo '  },'
echo '  {'
echo '    "host": "169.254.150.106",'
echo '    "port": 8000,'
echo '    "model": "gpt-oss",'
echo '    "name": "DGX Spark 4"'
echo '  }'
echo ""
