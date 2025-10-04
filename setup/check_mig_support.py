#!/usr/bin/env python3
"""
Comprehensive MIG Support Checker
Based on NVIDIA MIG User Guide
"""

import subprocess
import sys
import re
from typing import Dict, List, Any, Optional

def run_nvidia_command(cmd: List[str]) -> tuple[bool, str, str]:
    """Run nvidia command and return success, stdout, stderr"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def check_nvidia_driver():
    """Check NVIDIA driver version and basic info"""
    print("🔍 Checking NVIDIA Driver...")
    
    success, stdout, stderr = run_nvidia_command(['nvidia-smi'])
    
    if not success:
        print("❌ nvidia-smi not found or failed")
        return False
    
    print("✅ NVIDIA driver detected")
    
    # Extract driver version
    driver_match = re.search(r'Driver Version: ([\d.]+)', stdout)
    if driver_match:
        driver_version = driver_match.group(1)
        print(f"📋 Driver Version: {driver_version}")
        
        # Check if driver version supports MIG (470+)
        try:
            major_version = int(driver_version.split('.')[0])
            if major_version >= 470:
                print("✅ Driver version supports MIG (470+)")
                return True
            else:
                print(f"⚠️ Driver version {driver_version} may not support MIG (need 470+)")
                return False
        except:
            print("⚠️ Could not parse driver version")
            return False
    else:
        print("⚠️ Could not extract driver version")
        return False

def check_gpu_mig_capability():
    """Check if GPU supports MIG"""
    print("\n🔍 Checking GPU MIG Capability...")
    
    # Method 1: Try nvidia-smi mig command
    success, stdout, stderr = run_nvidia_command(['nvidia-smi', 'mig', '-lgip'])
    
    if success:
        print("✅ nvidia-smi mig command works")
        if "No MIG-supported devices found" in stdout:
            print("❌ No MIG-supported devices found")
            return False
        else:
            print("✅ MIG-supported devices detected")
            return True
    else:
        print(f"⚠️ nvidia-smi mig command failed: {stderr}")
    
    # Method 2: Check GPU properties
    success, stdout, stderr = run_nvidia_command([
        'nvidia-smi', '--query-gpu=name,mig.mode.current,mig.mode.pending', '--format=csv,noheader'
    ])
    
    if success:
        lines = stdout.strip().split('\n')
        for i, line in enumerate(lines):
            parts = [p.strip() for p in line.split(',')]
            if len(parts) >= 3:
                gpu_name = parts[0]
                mig_current = parts[1]
                mig_pending = parts[2]
                
                print(f"📋 GPU {i}: {gpu_name}")
                print(f"   MIG Current: {mig_current}")
                print(f"   MIG Pending: {mig_pending}")
                
                # If we can query MIG mode, the GPU likely supports it
                if mig_current != "N/A" or mig_pending != "N/A":
                    print("✅ GPU appears to support MIG")
                    return True
                else:
                    print("❌ GPU does not support MIG (N/A values)")
    
    # Method 3: Try to query MIG mode directly
    success, stdout, stderr = run_nvidia_command([
        'nvidia-smi', '-i', '0', '--query-gpu=mig.mode.current', '--format=csv,noheader'
    ])
    
    if success and "N/A" not in stdout:
        print("✅ GPU supports MIG mode queries")
        return True
    
    return False

def check_mig_mode_status():
    """Check current MIG mode status"""
    print("\n🔍 Checking MIG Mode Status...")
    
    success, stdout, stderr = run_nvidia_command([
        'nvidia-smi', '--query-gpu=name,mig.mode.current,mig.mode.pending', '--format=csv'
    ])
    
    if success:
        lines = stdout.strip().split('\n')[1:]  # Skip header
        for i, line in enumerate(lines):
            parts = [p.strip() for p in line.split(',')]
            if len(parts) >= 3:
                gpu_name = parts[0]
                mig_current = parts[1]
                mig_pending = parts[2]
                
                print(f"🎮 GPU {i}: {gpu_name}")
                print(f"   Current MIG Mode: {mig_current}")
                print(f"   Pending MIG Mode: {mig_pending}")
                
                if mig_current == "Enabled":
                    print("✅ MIG is currently enabled")
                    return True
                elif mig_current == "Disabled":
                    print("⚠️ MIG is currently disabled")
                    return False
                else:
                    print(f"❓ Unknown MIG status: {mig_current}")
    
    return False

def check_mig_instances():
    """Check existing MIG instances"""
    print("\n🔍 Checking MIG Instances...")
    
    # Check GPU instances
    success, stdout, stderr = run_nvidia_command(['nvidia-smi', 'mig', '-lgip'])
    
    if success:
        print("📋 GPU Instances:")
        print(stdout)
        
        # Count instances
        gi_lines = [line for line in stdout.split('\n') if 'GPU instance' in line]
        print(f"Found {len(gi_lines)} GPU instances")
    else:
        print(f"❌ Could not list GPU instances: {stderr}")
    
    # Check Compute instances
    success, stdout, stderr = run_nvidia_command(['nvidia-smi', 'mig', '-lcip'])
    
    if success:
        print("📋 Compute Instances:")
        print(stdout)
        
        # Count instances
        ci_lines = [line for line in stdout.split('\n') if 'Compute instance' in line]
        print(f"Found {len(ci_lines)} Compute instances")
    else:
        print(f"❌ Could not list Compute instances: {stderr}")

def get_mig_profiles():
    """Get available MIG profiles"""
    print("\n🔍 Checking Available MIG Profiles...")
    
    success, stdout, stderr = run_nvidia_command(['nvidia-smi', 'mig', '-lgipp'])
    
    if success:
        print("📋 Available MIG Profiles:")
        print(stdout)
    else:
        print(f"❌ Could not get MIG profiles: {stderr}")

def check_rtx_pro_6000_specific():
    """Check RTX Pro 6000 specific MIG support"""
    print("\n🔍 RTX Pro 6000 Specific Checks...")
    
    success, stdout, stderr = run_nvidia_command([
        'nvidia-smi', '--query-gpu=name,memory.total,compute_cap', '--format=csv'
    ])
    
    if success:
        lines = stdout.strip().split('\n')[1:]  # Skip header
        for line in lines:
            parts = [p.strip() for p in line.split(',')]
            if len(parts) >= 3:
                gpu_name = parts[0]
                memory_mb = parts[1].replace(' MiB', '')
                compute_cap = parts[2]
                
                print(f"🎮 GPU: {gpu_name}")
                print(f"📊 Memory: {memory_mb} MiB ({int(memory_mb)/1024:.1f} GB)")
                print(f"🔢 Compute Capability: {compute_cap}")
                
                # RTX Pro 6000 should have high compute capability
                if "RTX" in gpu_name and "6000" in gpu_name:
                    print("✅ RTX Pro 6000 detected")
                    
                    # Check compute capability (MIG typically requires 7.0+)
                    try:
                        cc_major = float(compute_cap.split('.')[0])
                        if cc_major >= 7.0:
                            print(f"✅ Compute capability {compute_cap} supports MIG")
                            return True
                        else:
                            print(f"❌ Compute capability {compute_cap} may not support MIG")
                            return False
                    except:
                        print("⚠️ Could not parse compute capability")
                        return False
    
    return False

def test_mig_enable():
    """Test if we can enable MIG (requires root)"""
    print("\n🔍 Testing MIG Enable (requires root)...")
    
    # Check if running as admin/root
    try:
        import os
        if os.name == 'nt':  # Windows
            import ctypes
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        else:  # Linux/Unix
            is_admin = os.geteuid() == 0
        
        if not is_admin:
            print("⚠️ Not running as administrator/root")
            print("💡 Run as admin to test MIG enable: sudo python check_mig_support.py")
            return False
        
        print("✅ Running with administrator privileges")
        
        # Try to enable MIG mode (dry run)
        success, stdout, stderr = run_nvidia_command([
            'nvidia-smi', '-i', '0', '-mig', '1'
        ])
        
        if success:
            print("✅ MIG enable command succeeded")
            print("⚠️ You may need to reboot for changes to take effect")
            return True
        else:
            print(f"❌ MIG enable failed: {stderr}")
            return False
            
    except Exception as e:
        print(f"❌ Error testing MIG enable: {e}")
        return False

def main():
    """Main MIG support check"""
    print("🖥️ Comprehensive MIG Support Check")
    print("=" * 50)
    print("Based on NVIDIA MIG User Guide")
    print()
    
    results = {}
    
    # Check driver
    results['driver_ok'] = check_nvidia_driver()
    
    # Check GPU MIG capability
    results['gpu_supports_mig'] = check_gpu_mig_capability()
    
    # Check MIG mode status
    results['mig_enabled'] = check_mig_mode_status()
    
    # Check instances (if MIG enabled)
    if results['mig_enabled']:
        check_mig_instances()
        get_mig_profiles()
    
    # RTX Pro 6000 specific checks
    results['rtx_pro_6000_compatible'] = check_rtx_pro_6000_specific()
    
    # Test MIG enable (if admin)
    results['can_enable_mig'] = test_mig_enable()
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 MIG Support Summary:")
    print("=" * 50)
    
    for check, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {check.replace('_', ' ').title()}")
    
    # Overall assessment
    if results['gpu_supports_mig'] and results['driver_ok']:
        if results['mig_enabled']:
            print("\n🎉 MIG is supported and enabled!")
            print("💡 You can use MIG for parallel model execution")
        else:
            print("\n⚡ MIG is supported but not enabled")
            print("💡 Run as admin: sudo nvidia-smi -i 0 -mig 1")
            print("💡 Then reboot and run: sudo python setup_mig.py")
    else:
        print("\n❌ MIG is not supported on this system")
        print("💡 Use regular Ollama parallel processing instead")
    
    return results

if __name__ == "__main__":
    try:
        results = main()
        
        # Exit code based on MIG support
        if results.get('gpu_supports_mig', False):
            sys.exit(0)  # MIG supported
        else:
            sys.exit(1)  # MIG not supported
            
    except KeyboardInterrupt:
        print("\n👋 Check interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)