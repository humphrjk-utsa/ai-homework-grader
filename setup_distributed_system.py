#!/usr/bin/env python3
"""
Setup script for distributed MLX system across two Mac Studios
"""

import os
import subprocess
import sys
import json

def create_config():
    """Create configuration file for distributed system"""
    
    print("🔧 Configuring Distributed MLX System")
    print("=" * 50)
    
    # Get network configuration
    print("\n1. Network Configuration:")
    mac1_ip = input("Enter Mac Studio 1 IP (Qwen Coder): ").strip()
    mac2_ip = input("Enter Mac Studio 2 IP (Gemma): ").strip()
    
    if not mac1_ip:
        mac1_ip = "192.168.1.100"  # Default Thunderbolt bridge IP
    if not mac2_ip:
        mac2_ip = "192.168.1.101"  # Default Thunderbolt bridge IP
    
    config = {
        "distributed_mode": True,
        "mac_studio_1": {
            "ip": mac1_ip,
            "port": 5001,
            "model": "mlx-community/Qwen3-Coder-30B-A3B-Instruct-bf16",
            "purpose": "code_analysis",
            "max_tokens": 2400,
            "temperature": 0.1
        },
        "mac_studio_2": {
            "ip": mac2_ip,
            "port": 5002,
            "model": "mlx-community/gemma-3-27b-it-bf16",
            "purpose": "feedback_generation",
            "max_tokens": 3800,
            "temperature": 0.3
        },
        "urls": {
            "qwen_server": f"http://{mac1_ip}:5001",
            "gemma_server": f"http://{mac2_ip}:5002"
        }
    }
    
    # Save configuration
    with open('distributed_config.json', 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"\n✅ Configuration saved to distributed_config.json")
    print(f"📡 Qwen Server: {config['urls']['qwen_server']}")
    print(f"📡 Gemma Server: {config['urls']['gemma_server']}")
    
    return config

def install_dependencies():
    """Install required dependencies"""
    
    print("\n2. Installing Dependencies:")
    print("-" * 30)
    
    dependencies = [
        "mlx-lm",
        "flask", 
        "aiohttp",
        "requests"
    ]
    
    for dep in dependencies:
        print(f"Installing {dep}...")
        subprocess.run([sys.executable, "-m", "pip", "install", dep], 
                      capture_output=True)
    
    print("✅ Dependencies installed")

def create_startup_scripts(config):
    """Create startup scripts for each Mac Studio"""
    
    print("\n3. Creating Startup Scripts:")
    print("-" * 30)
    
    # Mac Studio 1 startup script
    mac1_script = f"""#!/bin/bash
# Mac Studio 1 - Qwen Coder Server Startup
echo "🖥️ Starting Qwen Coder Server on Mac Studio 1..."
echo "📡 Server will be available at: {config['urls']['qwen_server']}"

cd "$(dirname "$0")"
export PYTHONPATH="$PWD:$PYTHONPATH"

python servers/qwen_server.py
"""
    
    with open('start_mac1_server.sh', 'w') as f:
        f.write(mac1_script)
    os.chmod('start_mac1_server.sh', 0o755)
    
    # Mac Studio 2 startup script
    mac2_script = f"""#!/bin/bash
# Mac Studio 2 - Gemma Server Startup
echo "🖥️ Starting Gemma Server on Mac Studio 2..."
echo "📡 Server will be available at: {config['urls']['gemma_server']}"

cd "$(dirname "$0")"
export PYTHONPATH="$PWD:$PYTHONPATH"

python servers/gemma_server.py
"""
    
    with open('start_mac2_server.sh', 'w') as f:
        f.write(mac2_script)
    os.chmod('start_mac2_server.sh', 0o755)
    
    print("✅ Startup scripts created:")
    print("   - start_mac1_server.sh (for Mac Studio 1)")
    print("   - start_mac2_server.sh (for Mac Studio 2)")

def create_test_script(config):
    """Create test script to verify distributed setup"""
    
    test_script = f"""#!/usr/bin/env python3
import requests
import time
import json

def test_distributed_system():
    print("🧪 Testing Distributed MLX System")
    print("=" * 40)
    
    qwen_url = "{config['urls']['qwen_server']}"
    gemma_url = "{config['urls']['gemma_server']}"
    
    # Test Qwen server
    print("\\n1. Testing Qwen Coder Server...")
    try:
        response = requests.get(f"{{qwen_url}}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Qwen server is healthy")
            data = response.json()
            print(f"   Model: {{data.get('model', 'Unknown')}}")
            print(f"   Status: {{data.get('status', 'Unknown')}}")
        else:
            print("❌ Qwen server health check failed")
    except Exception as e:
        print(f"❌ Cannot connect to Qwen server: {{e}}")
    
    # Test Gemma server
    print("\\n2. Testing Gemma Server...")
    try:
        response = requests.get(f"{{gemma_url}}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Gemma server is healthy")
            data = response.json()
            print(f"   Model: {{data.get('model', 'Unknown')}}")
            print(f"   Status: {{data.get('status', 'Unknown')}}")
        else:
            print("❌ Gemma server health check failed")
    except Exception as e:
        print(f"❌ Cannot connect to Gemma server: {{e}}")
    
    # Test parallel generation
    print("\\n3. Testing Parallel Generation...")
    try:
        from models.distributed_mlx_client import DistributedMLXClient
        
        client = DistributedMLXClient(qwen_url, gemma_url)
        
        code_prompt = "Analyze this R code: x <- c(1,2,3); mean(x)"
        feedback_prompt = "Provide feedback on data analysis approach"
        
        start_time = time.time()
        result = client.generate_parallel_sync(code_prompt, feedback_prompt)
        total_time = time.time() - start_time
        
        if result.get('code_analysis') and result.get('feedback'):
            print("✅ Parallel generation successful!")
            print(f"   Total time: {{total_time:.2f}}s")
            print(f"   Parallel efficiency: {{result.get('parallel_efficiency', 0):.2f}}x")
        else:
            print("❌ Parallel generation failed")
            print(f"   Error: {{result.get('error', 'Unknown')}}")
            
    except Exception as e:
        print(f"❌ Parallel test failed: {{e}}")

if __name__ == "__main__":
    test_distributed_system()
"""
    
    with open('test_distributed_system.py', 'w') as f:
        f.write(test_script)
    os.chmod('test_distributed_system.py', 0o755)
    
    print("✅ Test script created: test_distributed_system.py")

def main():
    """Main setup function"""
    
    print("🚀 Distributed MLX System Setup")
    print("Setting up homework grader across two Mac Studios")
    print("=" * 60)
    
    # Create configuration
    config = create_config()
    
    # Install dependencies
    install_dependencies()
    
    # Create startup scripts
    create_startup_scripts(config)
    
    # Create test script
    create_test_script(config)
    
    print("\n" + "=" * 60)
    print("🎉 Setup Complete!")
    print("\nNext Steps:")
    print("1. Copy this project to both Mac Studios")
    print("2. On Mac Studio 1: ./start_mac1_server.sh")
    print("3. On Mac Studio 2: ./start_mac2_server.sh") 
    print("4. Run: python test_distributed_system.py")
    print("5. Start the main app: streamlit run app.py")
    print("\n💡 The app will automatically detect and use the distributed system!")

if __name__ == "__main__":
    main()