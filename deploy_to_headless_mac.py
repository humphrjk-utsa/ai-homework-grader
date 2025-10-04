#!/usr/bin/env python3
"""
Deploy script for headless Mac Studios
Creates a complete package ready for deployment
"""

import os
import shutil
import json
import subprocess
import sys

def create_deployment_package():
    """Create deployment package for headless Mac Studios"""
    
    print("📦 Creating Deployment Package for Headless Mac Studios")
    print("=" * 60)
    
    # Create deployment directories
    deploy_dir = "mac_studio_deployment"
    mac1_dir = os.path.join(deploy_dir, "mac_studio_1")
    mac2_dir = os.path.join(deploy_dir, "mac_studio_2")
    
    # Clean and create directories
    if os.path.exists(deploy_dir):
        shutil.rmtree(deploy_dir)
    
    os.makedirs(mac1_dir, exist_ok=True)
    os.makedirs(mac2_dir, exist_ok=True)
    
    print(f"✅ Created deployment directories")
    
    # Copy essential files to both machines
    essential_files = [
        "requirements.txt",
        "distributed_config.json"
    ]
    
    essential_dirs = [
        "models",
        "servers"
    ]
    
    for mac_dir in [mac1_dir, mac2_dir]:
        # Copy files
        for file in essential_files:
            if os.path.exists(file):
                shutil.copy2(file, mac_dir)
        
        # Copy directories
        for dir_name in essential_dirs:
            if os.path.exists(dir_name):
                shutil.copytree(dir_name, os.path.join(mac_dir, dir_name), dirs_exist_ok=True)
    
    # Create Mac Studio 1 specific files
    create_mac1_files(mac1_dir)
    
    # Create Mac Studio 2 specific files  
    create_mac2_files(mac2_dir)
    
    # Create deployment instructions
    create_deployment_instructions(deploy_dir)
    
    print(f"\n🎉 Deployment package created in: {deploy_dir}/")
    print("📋 See deployment_instructions.md for next steps")

def create_mac1_files(mac1_dir):
    """Create Mac Studio 1 specific files"""
    
    # Install script for Mac 1
    install_script = """#!/bin/bash
# Mac Studio 1 Installation Script
echo "🖥️ Setting up Mac Studio 1 (Qwen Coder Server)"
echo "================================================"

# Check if we're on Apple Silicon
if [[ $(uname -m) != "arm64" ]]; then
    echo "❌ This script requires Apple Silicon Mac"
    exit 1
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

# Download Qwen model if not present
echo "🔄 Checking for Qwen model..."
python3 -c "
from mlx_lm import load
try:
    print('Loading Qwen model...')
    model, tokenizer = load('mlx-community/Qwen3-Coder-30B-A3B-Instruct-bf16')
    print('✅ Qwen model ready!')
except Exception as e:
    print(f'❌ Model loading failed: {e}')
    print('💡 Model will be downloaded on first use')
"

echo "✅ Mac Studio 1 setup complete!"
echo "🚀 Run: ./start_server.sh to start the Qwen server"
"""
    
    with open(os.path.join(mac1_dir, "install.sh"), "w") as f:
        f.write(install_script)
    os.chmod(os.path.join(mac1_dir, "install.sh"), 0o755)
    
    # Start server script for Mac 1
    start_script = """#!/bin/bash
# Mac Studio 1 - Start Qwen Coder Server
echo "🚀 Starting Qwen Coder Server on Mac Studio 1..."
echo "📡 Server will be available at: http://10.55.0.1:5001"
echo "Press Ctrl+C to stop"

export PYTHONPATH="$PWD:$PYTHONPATH"
python3 servers/qwen_server.py
"""
    
    with open(os.path.join(mac1_dir, "start_server.sh"), "w") as f:
        f.write(start_script)
    os.chmod(os.path.join(mac1_dir, "start_server.sh"), 0o755)
    
    # Status check script
    status_script = """#!/bin/bash
# Check Mac Studio 1 Status
echo "🔍 Mac Studio 1 Status Check"
echo "============================"

# Check if server is running
if curl -s http://10.55.0.1:5001/health > /dev/null; then
    echo "✅ Qwen server is running"
    curl -s http://10.55.0.1:5001/status | python3 -m json.tool
else
    echo "❌ Qwen server is not running"
    echo "💡 Run: ./start_server.sh"
fi
"""
    
    with open(os.path.join(mac1_dir, "check_status.sh"), "w") as f:
        f.write(status_script)
    os.chmod(os.path.join(mac1_dir, "check_status.sh"), 0o755)
    
    print("✅ Mac Studio 1 files created")

def create_mac2_files(mac2_dir):
    """Create Mac Studio 2 specific files"""
    
    # Install script for Mac 2
    install_script = """#!/bin/bash
# Mac Studio 2 Installation Script
echo "🖥️ Setting up Mac Studio 2 (Gemma Server)"
echo "==========================================="

# Check if we're on Apple Silicon
if [[ $(uname -m) != "arm64" ]]; then
    echo "❌ This script requires Apple Silicon Mac"
    exit 1
fi

# Install Python dependencies
echo "📦 Installing Python dependencies..."
pip3 install -r requirements.txt

# Download Gemma model if not present
echo "🔄 Checking for Gemma model..."
python3 -c "
from mlx_lm import load
try:
    print('Loading Gemma model...')
    model, tokenizer = load('mlx-community/gemma-3-27b-it-bf16')
    print('✅ Gemma model ready!')
except Exception as e:
    print(f'❌ Model loading failed: {e}')
    print('💡 Model will be downloaded on first use')
"

echo "✅ Mac Studio 2 setup complete!"
echo "🚀 Run: ./start_server.sh to start the Gemma server"
"""
    
    with open(os.path.join(mac2_dir, "install.sh"), "w") as f:
        f.write(install_script)
    os.chmod(os.path.join(mac2_dir, "install.sh"), 0o755)
    
    # Start server script for Mac 2
    start_script = """#!/bin/bash
# Mac Studio 2 - Start Gemma Server
echo "🚀 Starting Gemma Server on Mac Studio 2..."
echo "📡 Server will be available at: http://10.55.0.2:5002"
echo "Press Ctrl+C to stop"

export PYTHONPATH="$PWD:$PYTHONPATH"
python3 servers/gemma_server.py
"""
    
    with open(os.path.join(mac2_dir, "start_server.sh"), "w") as f:
        f.write(start_script)
    os.chmod(os.path.join(mac2_dir, "start_server.sh"), 0o755)
    
    # Status check script
    status_script = """#!/bin/bash
# Check Mac Studio 2 Status
echo "🔍 Mac Studio 2 Status Check"
echo "============================"

# Check if server is running
if curl -s http://10.55.0.2:5002/health > /dev/null; then
    echo "✅ Gemma server is running"
    curl -s http://10.55.0.2:5002/status | python3 -m json.tool
else
    echo "❌ Gemma server is not running"
    echo "💡 Run: ./start_server.sh"
fi
"""
    
    with open(os.path.join(mac2_dir, "check_status.sh"), "w") as f:
        f.write(status_script)
    os.chmod(os.path.join(mac2_dir, "check_status.sh"), 0o755)
    
    print("✅ Mac Studio 2 files created")

def create_deployment_instructions(deploy_dir):
    """Create deployment instructions"""
    
    instructions = """# Headless Mac Studio Deployment Instructions

## Overview
This package contains everything needed to run the distributed MLX homework grader across two headless Mac Studios connected via Thunderbolt bridge.

## Network Configuration
- Mac Studio 1: 10.55.0.1:5001 (Qwen Coder)
- Mac Studio 2: 10.55.0.2:5002 (Gemma)

## Deployment Steps

### 1. Copy Files to Mac Studios

**Mac Studio 1:**
```bash
# Copy the mac_studio_1 folder to Mac Studio 1
scp -r mac_studio_1/ user@10.55.0.1:~/homework_grader/
```

**Mac Studio 2:**
```bash
# Copy the mac_studio_2 folder to Mac Studio 2  
scp -r mac_studio_2/ user@10.55.0.2:~/homework_grader/
```

### 2. Setup Mac Studio 1 (SSH)

```bash
# SSH into Mac Studio 1
ssh user@10.55.0.1

# Navigate to project directory
cd ~/homework_grader

# Run installation
./install.sh

# Start the Qwen server
./start_server.sh
```

### 3. Setup Mac Studio 2 (SSH)

```bash
# SSH into Mac Studio 2
ssh user@10.55.0.2

# Navigate to project directory
cd ~/homework_grader

# Run installation
./install.sh

# Start the Gemma server
./start_server.sh
```

### 4. Verify Setup

**Check Mac Studio 1:**
```bash
ssh user@10.55.0.1
cd ~/homework_grader
./check_status.sh
```

**Check Mac Studio 2:**
```bash
ssh user@10.55.0.2
cd ~/homework_grader
./check_status.sh
```

**Test from main machine:**
```bash
# Test Qwen server
curl http://10.55.0.1:5001/health

# Test Gemma server
curl http://10.55.0.2:5002/health
```

### 5. Run Main Application

On your main machine (where you run Streamlit):
```bash
streamlit run app.py
```

The app will automatically detect the distributed system and show "🖥️ Distributed MLX System" in the sidebar.

## Troubleshooting

### Models Not Loading
- Models will download automatically on first use
- Qwen model: ~60GB download
- Gemma model: ~54GB download
- Ensure sufficient disk space and internet connection

### Network Issues
- Verify Thunderbolt bridge is active: `ifconfig bridge100`
- Test connectivity: `ping 10.55.0.1` and `ping 10.55.0.2`
- Check firewall settings on both machines

### Server Issues
- Check logs: Server output will show any errors
- Restart servers: `./start_server.sh`
- Verify Python/MLX installation: `python3 -c "import mlx_lm; print('OK')"`

## Performance Expectations

- **Model Loading**: 30-60 seconds on first startup
- **Generation Speed**: 
  - Qwen (code analysis): ~30-60 seconds
  - Gemma (feedback): ~45-90 seconds
  - Parallel processing: ~60-90 seconds total (vs 120+ sequential)

## Monitoring

Each Mac Studio has a `check_status.sh` script to monitor:
- Server health
- Model loading status
- Response times
- Memory usage

Run these periodically to ensure optimal performance.
"""
    
    with open(os.path.join(deploy_dir, "deployment_instructions.md"), "w") as f:
        f.write(instructions)
    
    # Create a quick deployment script
    quick_deploy = """#!/bin/bash
# Quick Deployment Script
echo "🚀 Quick Deployment to Headless Mac Studios"
echo "============================================"

# Check if we have the deployment package
if [ ! -d "mac_studio_deployment" ]; then
    echo "❌ Run python3 deploy_to_headless_mac.py first"
    exit 1
fi

echo "📋 This script will help you deploy to both Mac Studios"
echo ""

# Get SSH details
read -p "Enter username for Mac Studios: " username
read -p "Enter Mac Studio 1 IP (default: 10.55.0.1): " mac1_ip
read -p "Enter Mac Studio 2 IP (default: 10.55.0.2): " mac2_ip

mac1_ip=${mac1_ip:-10.55.0.1}
mac2_ip=${mac2_ip:-10.55.0.2}

echo ""
echo "🔄 Deploying to Mac Studios..."

# Deploy to Mac Studio 1
echo "📤 Deploying to Mac Studio 1 ($mac1_ip)..."
scp -r mac_studio_deployment/mac_studio_1/ $username@$mac1_ip:~/homework_grader/
if [ $? -eq 0 ]; then
    echo "✅ Mac Studio 1 deployment successful"
else
    echo "❌ Mac Studio 1 deployment failed"
fi

# Deploy to Mac Studio 2
echo "📤 Deploying to Mac Studio 2 ($mac2_ip)..."
scp -r mac_studio_deployment/mac_studio_2/ $username@$mac2_ip:~/homework_grader/
if [ $? -eq 0 ]; then
    echo "✅ Mac Studio 2 deployment successful"
else
    echo "❌ Mac Studio 2 deployment failed"
fi

echo ""
echo "🎉 Deployment complete!"
echo ""
echo "Next steps:"
echo "1. SSH to Mac Studio 1: ssh $username@$mac1_ip"
echo "2. Run: cd ~/homework_grader && ./install.sh && ./start_server.sh"
echo "3. SSH to Mac Studio 2: ssh $username@$mac2_ip"
echo "4. Run: cd ~/homework_grader && ./install.sh && ./start_server.sh"
echo "5. Test: python3 test_distributed_system.py"
"""
    
    with open(os.path.join(deploy_dir, "quick_deploy.sh"), "w") as f:
        f.write(quick_deploy)
    os.chmod(os.path.join(deploy_dir, "quick_deploy.sh"), 0o755)
    
    print("✅ Deployment instructions created")

if __name__ == "__main__":
    create_deployment_package()