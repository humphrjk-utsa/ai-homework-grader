#!/usr/bin/env python3
"""
Setup R kernel for notebook execution
"""

import subprocess
import sys
import os

def check_r_installation():
    """Check if R is installed and accessible"""
    try:
        result = subprocess.run(['R', '--version'], capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ R is installed and accessible")
            return True
        else:
            print("❌ R is not accessible")
            return False
    except Exception as e:
        print(f"❌ R check failed: {e}")
        return False

def check_r_kernel():
    """Check if R kernel is available for Jupyter"""
    try:
        result = subprocess.run(['jupyter', 'kernelspec', 'list'], capture_output=True, text=True)
        if 'ir' in result.stdout.lower():
            print("✅ R kernel (IRkernel) is available")
            return True
        else:
            print("❌ R kernel (IRkernel) not found")
            return False
    except Exception as e:
        print(f"❌ Kernel check failed: {e}")
        return False

def install_r_kernel():
    """Install R kernel for Jupyter"""
    print("Installing R kernel for Jupyter...")
    
    r_commands = [
        'install.packages("IRkernel", repos="https://cran.r-project.org")',
        'IRkernel::installspec(user = FALSE)'
    ]
    
    for cmd in r_commands:
        try:
            result = subprocess.run(['R', '-e', cmd], capture_output=True, text=True, timeout=300)
            if result.returncode == 0:
                print(f"✅ R command succeeded: {cmd}")
            else:
                print(f"⚠️ R command had issues: {cmd}")
                print(f"   Output: {result.stdout}")
                print(f"   Error: {result.stderr}")
        except Exception as e:
            print(f"❌ Failed to run R command: {cmd}")
            print(f"   Error: {e}")

def setup_r_environment():
    """Set up R environment for notebook execution"""
    print("🔧 Setting up R environment for notebook execution...")
    
    if not check_r_installation():
        print("\n❌ R is not installed. Please install R first:")
        print("   macOS: brew install r")
        print("   Ubuntu: sudo apt-get install r-base")
        print("   Windows: Download from https://cran.r-project.org/")
        return False
    
    if not check_r_kernel():
        print("\n🔧 Installing R kernel for Jupyter...")
        install_r_kernel()
        
        # Check again
        if check_r_kernel():
            print("✅ R kernel installation successful!")
        else:
            print("❌ R kernel installation failed")
            return False
    
    print("\n✅ R environment ready for notebook execution!")
    print("📝 The grader can now:")
    print("   - Execute student R code automatically")
    print("   - Capture real error messages")
    print("   - Provide specific code corrections")
    print("   - Detect execution issues vs code issues")
    
    return True

if __name__ == "__main__":
    setup_r_environment()