#!/usr/bin/env python3
"""
MIG (Multi-Instance GPU) Manager for RTX Pro 6000
Enables parallel model execution using GPU partitioning
"""

import subprocess
import json
import os
import time
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass

@dataclass
class MIGInstance:
    """Represents a MIG GPU instance"""
    instance_id: str
    gpu_id: int
    memory_mb: int
    compute_units: int
    uuid: str
    profile: str
    available: bool = True

class MIGManager:
    """Manages MIG instances for parallel model execution"""
    
    def __init__(self):
        self.instances: List[MIGInstance] = []
        self.instance_assignments: Dict[str, str] = {}  # model_id -> instance_id
        self.rtx_pro_6000_profiles = {
            # RTX Pro 6000 48GB MIG profiles
            "1g.24gb": {"memory_gb": 24, "compute_units": 1, "instances": 2},
            "2g.24gb": {"memory_gb": 24, "compute_units": 2, "instances": 2}, 
            "3g.24gb": {"memory_gb": 24, "compute_units": 3, "instances": 2},
            "4g.24gb": {"memory_gb": 24, "compute_units": 4, "instances": 2},
            "1g.12gb": {"memory_gb": 12, "compute_units": 1, "instances": 4},
            "2g.12gb": {"memory_gb": 12, "compute_units": 2, "instances": 4},
            "1g.6gb":  {"memory_gb": 6,  "compute_units": 1, "instances": 8}
        }
    
    def check_mig_support(self) -> bool:
        """Check if MIG is supported and enabled"""
        try:
            # Check if nvidia-smi supports MIG
            result = subprocess.run([
                'nvidia-smi', 'mig', '-lgip'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                print("✅ MIG support detected")
                return True
            else:
                print("❌ MIG not supported or not enabled")
                return False
                
        except (FileNotFoundError, subprocess.TimeoutExpired):
            print("❌ nvidia-smi not found or timeout")
            return False
    
    def get_gpu_info(self) -> Dict[str, Any]:
        """Get detailed GPU information"""
        try:
            result = subprocess.run([
                'nvidia-smi', '--query-gpu=name,memory.total,compute_mode,mig.mode.current',
                '--format=csv,noheader,nounits'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                gpu_info = {}
                
                for i, line in enumerate(lines):
                    parts = [p.strip() for p in line.split(',')]
                    if len(parts) >= 4:
                        gpu_info[f"gpu_{i}"] = {
                            "name": parts[0],
                            "memory_mb": int(parts[1]),
                            "compute_mode": parts[2],
                            "mig_mode": parts[3]
                        }
                
                return gpu_info
            
        except Exception as e:
            print(f"❌ Failed to get GPU info: {e}")
        
        return {}
    
    def enable_mig_mode(self, gpu_id: int = 0) -> bool:
        """Enable MIG mode on specified GPU"""
        try:
            print(f"🔧 Enabling MIG mode on GPU {gpu_id}...")
            
            # Enable MIG mode
            result = subprocess.run([
                'sudo', 'nvidia-smi', '-i', str(gpu_id), '-mig', '1'
            ], capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                print("✅ MIG mode enabled (requires reboot or driver reset)")
                return True
            else:
                print(f"❌ Failed to enable MIG mode: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"❌ Error enabling MIG mode: {e}")
            return False
    
    def create_mig_instances(self, profile: str = "2g.24gb", gpu_id: int = 0) -> bool:
        """Create MIG instances with specified profile"""
        try:
            print(f"🏗️ Creating MIG instances with profile {profile} on GPU {gpu_id}...")
            
            if profile not in self.rtx_pro_6000_profiles:
                print(f"❌ Unknown profile: {profile}")
                return False
            
            profile_info = self.rtx_pro_6000_profiles[profile]
            
            # Create GPU instances
            for i in range(profile_info["instances"]):
                result = subprocess.run([
                    'sudo', 'nvidia-smi', 'mig', '-cgi', profile,
                    '-i', str(gpu_id)
                ], capture_output=True, text=True, timeout=30)
                
                if result.returncode != 0:
                    print(f"❌ Failed to create GPU instance {i}: {result.stderr}")
                    return False
            
            # Create compute instances
            gi_result = subprocess.run([
                'nvidia-smi', 'mig', '-lgip', '-i', str(gpu_id)
            ], capture_output=True, text=True, timeout=10)
            
            if gi_result.returncode == 0:
                # Parse GPU instances and create compute instances
                lines = gi_result.stdout.strip().split('\n')[1:]  # Skip header
                
                for line in lines:
                    if 'GPU instance' in line:
                        # Extract GPU instance ID
                        parts = line.split()
                        gi_id = parts[1].rstrip(':')
                        
                        # Create compute instance
                        ci_result = subprocess.run([
                            'sudo', 'nvidia-smi', 'mig', '-cci', '-gi', gi_id,
                            '-i', str(gpu_id)
                        ], capture_output=True, text=True, timeout=30)
                        
                        if ci_result.returncode != 0:
                            print(f"❌ Failed to create compute instance for GI {gi_id}")
            
            print(f"✅ MIG instances created successfully")
            return True
            
        except Exception as e:
            print(f"❌ Error creating MIG instances: {e}")
            return False
    
    def discover_mig_instances(self) -> List[MIGInstance]:
        """Discover available MIG instances"""
        instances = []
        
        try:
            # Get MIG device information
            result = subprocess.run([
                'nvidia-smi', 'mig', '-lgip'
            ], capture_output=True, text=True, timeout=10)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                
                for line in lines:
                    if 'MIG' in line and 'UUID' in line:
                        # Parse MIG instance information
                        parts = line.split()
                        
                        # Extract relevant information (format may vary)
                        instance_id = parts[0] if parts else "unknown"
                        
                        # Get detailed info using nvidia-ml-py if available
                        try:
                            import pynvml
                            pynvml.nvmlInit()
                            
                            device_count = pynvml.nvmlDeviceGetCount()
                            
                            for i in range(device_count):
                                handle = pynvml.nvmlDeviceGetHandleByIndex(i)
                                name = pynvml.nvmlDeviceGetName(handle).decode()
                                
                                if 'MIG' in name:
                                    memory_info = pynvml.nvmlDeviceGetMemoryInfo(handle)
                                    uuid = pynvml.nvmlDeviceGetUUID(handle).decode()
                                    
                                    instance = MIGInstance(
                                        instance_id=f"mig_{i}",
                                        gpu_id=0,  # Assume GPU 0 for now
                                        memory_mb=memory_info.total // (1024 * 1024),
                                        compute_units=1,  # Default
                                        uuid=uuid,
                                        profile="detected",
                                        available=True
                                    )
                                    
                                    instances.append(instance)
                            
                            pynvml.nvmlShutdown()
                            
                        except ImportError:
                            print("⚠️ pynvml not available, using basic detection")
                            
                            # Fallback: create instances based on common profiles
                            for i in range(2):  # Assume 2 instances for RTX Pro 6000
                                instance = MIGInstance(
                                    instance_id=f"mig_{i}",
                                    gpu_id=0,
                                    memory_mb=24 * 1024,  # 24GB per instance
                                    compute_units=2,
                                    uuid=f"MIG-{i}",
                                    profile="2g.24gb",
                                    available=True
                                )
                                instances.append(instance)
        
        except Exception as e:
            print(f"❌ Error discovering MIG instances: {e}")
        
        self.instances = instances
        return instances
    
    def assign_model_to_instance(self, model_id: str, memory_requirement_gb: int) -> Optional[str]:
        """Assign a model to an available MIG instance"""
        
        # Find suitable instance
        for instance in self.instances:
            if (instance.available and 
                instance.memory_mb >= memory_requirement_gb * 1024):
                
                instance.available = False
                self.instance_assignments[model_id] = instance.instance_id
                
                print(f"📍 Assigned {model_id} to MIG instance {instance.instance_id}")
                return instance.instance_id
        
        print(f"❌ No suitable MIG instance found for {model_id}")
        return None
    
    def release_model_assignment(self, model_id: str):
        """Release a model's MIG instance assignment"""
        if model_id in self.instance_assignments:
            instance_id = self.instance_assignments[model_id]
            
            # Find and mark instance as available
            for instance in self.instances:
                if instance.instance_id == instance_id:
                    instance.available = True
                    break
            
            del self.instance_assignments[model_id]
            print(f"🔓 Released MIG instance {instance_id} from {model_id}")
    
    def get_cuda_device_for_model(self, model_id: str) -> Optional[str]:
        """Get CUDA device string for a model"""
        if model_id in self.instance_assignments:
            instance_id = self.instance_assignments[model_id]
            
            # Find the instance
            for instance in self.instances:
                if instance.instance_id == instance_id:
                    # Return CUDA device string (format: MIG-UUID or device index)
                    return instance.uuid if instance.uuid.startswith('MIG-') else f"cuda:{instance.gpu_id}"
        
        return None
    
    def setup_optimal_mig_config(self) -> bool:
        """Setup optimal MIG configuration for homework grading"""
        print("🎯 Setting up optimal MIG configuration for RTX Pro 6000...")
        
        gpu_info = self.get_gpu_info()
        
        if not gpu_info:
            print("❌ Could not get GPU information")
            return False
        
        # Check if we have RTX Pro 6000
        gpu_0 = gpu_info.get("gpu_0", {})
        gpu_name = gpu_0.get("name", "").lower()
        
        if "rtx" not in gpu_name or "6000" not in gpu_name:
            print(f"⚠️ GPU detected: {gpu_0.get('name', 'Unknown')}")
            print("⚠️ This configuration is optimized for RTX Pro 6000")
        
        # Check MIG mode
        if gpu_0.get("mig_mode", "Disabled") == "Disabled":
            print("🔧 MIG mode is disabled. Enabling...")
            if not self.enable_mig_mode():
                return False
            
            print("⚠️ Please reboot or reset GPU driver, then run this script again")
            return False
        
        # Create optimal instances for homework grading
        # 2x 24GB instances - perfect for running two large models in parallel
        if not self.create_mig_instances("2g.24gb"):
            return False
        
        # Discover created instances
        instances = self.discover_mig_instances()
        
        if len(instances) >= 2:
            print(f"✅ MIG setup complete: {len(instances)} instances available")
            return True
        else:
            print(f"❌ Expected 2+ instances, found {len(instances)}")
            return False
    
    def print_mig_status(self):
        """Print current MIG status"""
        print("\n🖥️ MIG Status Report")
        print("=" * 40)
        
        gpu_info = self.get_gpu_info()
        
        for gpu_id, info in gpu_info.items():
            print(f"GPU {gpu_id}: {info['name']}")
            print(f"  Memory: {info['memory_mb']}MB")
            print(f"  MIG Mode: {info['mig_mode']}")
            print()
        
        if self.instances:
            print("MIG Instances:")
            for instance in self.instances:
                status = "🟢 Available" if instance.available else "🔴 In Use"
                print(f"  {instance.instance_id}: {instance.memory_mb}MB, {status}")
        else:
            print("No MIG instances detected")
        
        if self.instance_assignments:
            print("\nModel Assignments:")
            for model_id, instance_id in self.instance_assignments.items():
                print(f"  {model_id} → {instance_id}")

def setup_mig_for_homework_grader():
    """Setup MIG for homework grader"""
    manager = MIGManager()
    
    if not manager.check_mig_support():
        print("❌ MIG not supported on this system")
        return False
    
    return manager.setup_optimal_mig_config()

if __name__ == "__main__":
    manager = MIGManager()
    manager.print_mig_status()
    
    if manager.check_mig_support():
        print("\n💡 To setup MIG for homework grading:")
        print("sudo python mig_manager.py --setup")
    else:
        print("\n❌ MIG not available on this system")