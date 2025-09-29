#!/usr/bin/env python3
"""
MIG Setup Script for RTX Pro 6000
Configures Multi-Instance GPU for parallel homework grading
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def check_root_privileges():
    """Check if running with root privileges"""
    if os.geteuid() != 0:
        print("❌ This script requires root privileges for MIG configuration")
        print("💡 Run with: sudo python setup_mig.py")
        return False
    return True

def check_nvidia_driver():
    """Check NVIDIA driver version and MIG support"""
    try:
        result = subprocess.run(['nvidia-smi'], capture_output=True, text=True, timeout=10)
        if result.returncode != 0:
            print("❌ nvidia-smi not found or not working")
            return False
        
        print("✅ NVIDIA driver detected")
        
        # Check MIG support
        mig_result = subprocess.run(['nvidia-smi', 'mig', '-lgip'], 
                                  capture_output=True, text=True, timeout=10)
        
        if mig_result.returncode == 0:
            print("✅ MIG support confirmed")
            return True
        else:
            print("❌ MIG not supported or not enabled")
            print("💡 Ensure you have a compatible GPU and driver version")
            return False
            
    except Exception as e:
        print(f"❌ Error checking NVIDIA driver: {e}")
        return False

def get_gpu_info():
    """Get detailed GPU information"""
    try:
        result = subprocess.run([
            'nvidia-smi', '--query-gpu=name,memory.total,compute_mode,mig.mode.current',
            '--format=csv,noheader,nounits'
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            lines = result.stdout.strip().split('\n')
            gpus = []
            
            for i, line in enumerate(lines):
                parts = [p.strip() for p in line.split(',')]
                if len(parts) >= 4:
                    gpus.append({
                        "id": i,
                        "name": parts[0],
                        "memory_mb": int(parts[1]),
                        "compute_mode": parts[2],
                        "mig_mode": parts[3]
                    })
            
            return gpus
        
    except Exception as e:
        print(f"❌ Error getting GPU info: {e}")
    
    return []

def enable_mig_mode(gpu_id=0):
    """Enable MIG mode on GPU"""
    print(f"🔧 Enabling MIG mode on GPU {gpu_id}...")
    
    try:
        # Enable MIG mode
        result = subprocess.run([
            'nvidia-smi', '-i', str(gpu_id), '-mig', '1'
        ], capture_output=True, text=True, timeout=30)
        
        if result.returncode == 0:
            print("✅ MIG mode enabled")
            return True
        else:
            print(f"❌ Failed to enable MIG mode: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error enabling MIG mode: {e}")
        return False

def reset_mig_configuration(gpu_id=0):
    """Reset MIG configuration to clean state"""
    print(f"🧹 Resetting MIG configuration on GPU {gpu_id}...")
    
    try:
        # Destroy all compute instances
        subprocess.run(['nvidia-smi', 'mig', '-dci', '-i', str(gpu_id)], 
                      capture_output=True, timeout=30)
        
        # Destroy all GPU instances  
        subprocess.run(['nvidia-smi', 'mig', '-dgi', '-i', str(gpu_id)], 
                      capture_output=True, timeout=30)
        
        print("✅ MIG configuration reset")
        return True
        
    except Exception as e:
        print(f"⚠️ Error resetting MIG: {e}")
        return False

def create_homework_grader_mig_config(gpu_id=0):
    """Create optimal MIG configuration for homework grading"""
    print(f"🏗️ Creating homework grader MIG configuration on GPU {gpu_id}...")
    
    # Configuration: 2x 24GB instances for parallel model execution
    # This allows running two large models (e.g., Qwen2.5-Coder 32B + Gemma 2 27B) simultaneously
    
    try:
        # Create 2 GPU instances with 24GB each (2g.24gb profile)
        print("📊 Creating 2x 24GB GPU instances...")
        
        for i in range(2):
            result = subprocess.run([
                'nvidia-smi', 'mig', '-cgi', '2g.24gb', '-i', str(gpu_id)
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode != 0:
                print(f"❌ Failed to create GPU instance {i}: {result.stderr}")
                return False
            
            print(f"✅ Created GPU instance {i}")
        
        # Get created GPU instances
        gi_result = subprocess.run([
            'nvidia-smi', 'mig', '-lgip', '-i', str(gpu_id)
        ], capture_output=True, text=True, timeout=10)
        
        if gi_result.returncode != 0:
            print("❌ Failed to list GPU instances")
            return False
        
        # Parse GPU instances and create compute instances
        lines = gi_result.stdout.strip().split('\n')
        gpu_instances = []
        
        for line in lines:
            if 'GPU instance' in line and ':' in line:
                # Extract GPU instance ID
                parts = line.split()
                for part in parts:
                    if part.endswith(':'):
                        gi_id = part.rstrip(':')
                        gpu_instances.append(gi_id)
                        break
        
        print(f"📋 Found {len(gpu_instances)} GPU instances: {gpu_instances}")
        
        # Create compute instances for each GPU instance
        for gi_id in gpu_instances:
            print(f"🖥️ Creating compute instance for GPU instance {gi_id}...")
            
            ci_result = subprocess.run([
                'nvidia-smi', 'mig', '-cci', '-gi', gi_id, '-i', str(gpu_id)
            ], capture_output=True, text=True, timeout=30)
            
            if ci_result.returncode != 0:
                print(f"❌ Failed to create compute instance for GI {gi_id}: {ci_result.stderr}")
                return False
            
            print(f"✅ Created compute instance for GPU instance {gi_id}")
        
        print("🎉 MIG configuration created successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Error creating MIG configuration: {e}")
        return False

def verify_mig_configuration(gpu_id=0):
    """Verify MIG configuration"""
    print(f"🔍 Verifying MIG configuration on GPU {gpu_id}...")
    
    try:
        # List GPU instances
        gi_result = subprocess.run([
            'nvidia-smi', 'mig', '-lgip', '-i', str(gpu_id)
        ], capture_output=True, text=True, timeout=10)
        
        # List compute instances
        ci_result = subprocess.run([
            'nvidia-smi', 'mig', '-lcip', '-i', str(gpu_id)
        ], capture_output=True, text=True, timeout=10)
        
        if gi_result.returncode == 0 and ci_result.returncode == 0:
            print("📊 GPU Instances:")
            print(gi_result.stdout)
            print("🖥️ Compute Instances:")
            print(ci_result.stdout)
            
            # Count instances
            gi_lines = [line for line in gi_result.stdout.split('\n') if 'GPU instance' in line]
            ci_lines = [line for line in ci_result.stdout.split('\n') if 'Compute instance' in line]
            
            print(f"✅ Found {len(gi_lines)} GPU instances and {len(ci_lines)} compute instances")
            
            if len(gi_lines) >= 2 and len(ci_lines) >= 2:
                print("🎯 MIG configuration is optimal for homework grading!")
                return True
            else:
                print("⚠️ MIG configuration may not be optimal")
                return False
        else:
            print("❌ Failed to verify MIG configuration")
            return False
            
    except Exception as e:
        print(f"❌ Error verifying MIG configuration: {e}")
        return False

def test_mig_with_homework_grader():
    """Test MIG configuration with homework grader"""
    print("🧪 Testing MIG configuration with homework grader...")
    
    try:
        # Test MIG manager
        result = subprocess.run([
            sys.executable, '-c', 
            'from mig_manager import MIGManager; m = MIGManager(); m.print_mig_status()'
        ], capture_output=True, text=True, timeout=30, cwd=Path(__file__).parent)
        
        if result.returncode == 0:
            print("✅ MIG manager test passed")
            print(result.stdout)
            return True
        else:
            print(f"❌ MIG manager test failed: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing MIG with homework grader: {e}")
        return False

def main():
    """Main setup function"""
    print("🖥️ RTX Pro 6000 MIG Setup for Homework Grader")
    print("=" * 60)
    
    # Check prerequisites
    if not check_root_privileges():
        return False
    
    if not check_nvidia_driver():
        return False
    
    # Get GPU information
    gpus = get_gpu_info()
    
    if not gpus:
        print("❌ No GPUs detected")
        return False
    
    print(f"\n📊 Detected GPUs:")
    for gpu in gpus:
        print(f"  GPU {gpu['id']}: {gpu['name']} ({gpu['memory_mb']}MB)")
        print(f"    MIG Mode: {gpu['mig_mode']}")
    
    # Find RTX Pro 6000
    rtx_pro_6000 = None
    for gpu in gpus:
        if "rtx" in gpu["name"].lower() and "6000" in gpu["name"]:
            rtx_pro_6000 = gpu
            break
    
    if not rtx_pro_6000:
        print("⚠️ RTX Pro 6000 not detected")
        print("💡 This setup is optimized for RTX Pro 6000, but will attempt configuration anyway")
        rtx_pro_6000 = gpus[0]  # Use first GPU
    
    gpu_id = rtx_pro_6000["id"]
    print(f"\n🎯 Configuring MIG on GPU {gpu_id}: {rtx_pro_6000['name']}")
    
    # Check if MIG is already enabled
    if rtx_pro_6000["mig_mode"] == "Disabled":
        print("\n🔧 MIG mode is disabled. Enabling...")
        
        if not enable_mig_mode(gpu_id):
            return False
        
        print("\n⚠️ MIG mode enabled. Please reboot or reset GPU driver:")
        print("   sudo nvidia-smi --gpu-reset")
        print("   Then run this script again to complete setup")
        return True
    
    elif rtx_pro_6000["mig_mode"] == "Enabled":
        print("✅ MIG mode is already enabled")
        
        # Ask user if they want to reset configuration
        response = input("\n🤔 Reset existing MIG configuration? (y/N): ").strip().lower()
        
        if response in ['y', 'yes']:
            reset_mig_configuration(gpu_id)
        
        # Create homework grader configuration
        if not create_homework_grader_mig_config(gpu_id):
            return False
        
        # Verify configuration
        if not verify_mig_configuration(gpu_id):
            return False
        
        # Test with homework grader
        print("\n🧪 Testing MIG configuration...")
        if test_mig_with_homework_grader():
            print("\n🎉 MIG setup complete and verified!")
            print("\n💡 Next steps:")
            print("   1. Download models: python quick_download_commands.py")
            print("   2. Test setup: python test_pc_setup.py")
            print("   3. Start grading: streamlit run pc_start.py")
            return True
        else:
            print("\n⚠️ MIG setup complete but testing failed")
            print("💡 Try running: python test_pc_setup.py")
            return False
    
    else:
        print(f"❌ Unknown MIG mode: {rtx_pro_6000['mig_mode']}")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n👋 Setup interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)