#!/usr/bin/env python3
"""
MIG-aware llama.cpp client for RTX Pro 6000
Enables parallel model execution using GPU partitioning
"""

import os
import time
import streamlit as st
from typing import Optional, Dict, Any, List
from pathlib import Path

from pc_llamacpp_client import PCLlamaCppClient
from mig_manager import MIGManager

class MIGLlamaCppClient(PCLlamaCppClient):
    """MIG-aware llama.cpp client for parallel execution"""
    
    def __init__(self, model_path: str = None, model_name: str = None, 
                 model_id: str = None, mig_manager: MIGManager = None):
        """Initialize MIG-aware client
        
        Args:
            model_path: Direct path to GGUF model file
            model_name: Model name for automatic selection
            model_id: Unique identifier for this model instance
            mig_manager: Shared MIG manager instance
        """
        
        # Initialize parent class
        super().__init__(model_path, model_name)
        
        self.model_id = model_id or f"model_{int(time.time())}"
        self.mig_manager = mig_manager or MIGManager()
        self.assigned_instance = None
        self.cuda_device = None
        
        # Estimate memory requirement
        self.memory_requirement_gb = self._estimate_memory_requirement()
        
        print(f"🎯 MIG Client initialized: {self.model_id}")
        print(f"📊 Estimated memory requirement: {self.memory_requirement_gb}GB")
    
    def _estimate_memory_requirement(self) -> int:
        """Estimate memory requirement based on model size"""
        if not self.model_path or not os.path.exists(self.model_path):
            return 24  # Default assumption
        
        try:
            file_size_gb = os.path.getsize(self.model_path) / (1024**3)
            
            # Add overhead for context, KV cache, etc.
            # Rule of thumb: model file size + 50% overhead + 4GB for context
            memory_needed = int(file_size_gb * 1.5 + 4)
            
            # Round up to nearest 6GB (common MIG slice sizes)
            return ((memory_needed + 5) // 6) * 6
            
        except Exception as e:
            print(f"⚠️ Could not estimate memory for {self.model_path}: {e}")
            return 24  # Conservative default
    
    def _request_mig_instance(self) -> bool:
        """Request a MIG instance for this model"""
        if self.assigned_instance:
            return True  # Already assigned
        
        instance_id = self.mig_manager.assign_model_to_instance(
            self.model_id, self.memory_requirement_gb
        )
        
        if instance_id:
            self.assigned_instance = instance_id
            self.cuda_device = self.mig_manager.get_cuda_device_for_model(self.model_id)
            
            print(f"✅ {self.model_id} assigned to MIG instance {instance_id}")
            print(f"🎮 CUDA device: {self.cuda_device}")
            return True
        else:
            print(f"❌ No MIG instance available for {self.model_id}")
            return False
    
    def _release_mig_instance(self):
        """Release the assigned MIG instance"""
        if self.assigned_instance:
            self.mig_manager.release_model_assignment(self.model_id)
            self.assigned_instance = None
            self.cuda_device = None
    
    def _load_model(self):
        """Load the llama.cpp model with MIG support"""
        if self.model_loaded_in_memory:
            return  # Already loaded
        
        if not self.model_path or not os.path.exists(self.model_path):
            print(f"❌ Model file not found: {self.model_path}")
            return
        
        # Request MIG instance
        if not self._request_mig_instance():
            print("⚠️ No MIG instance available, falling back to shared GPU")
        
        try:
            from llama_cpp import Llama
            
            # Show loading message
            if hasattr(st, 'info'):
                st.info(f"🔄 Loading {self.model_name} on MIG instance {self.assigned_instance}...")
            else:
                print(f"🔄 Loading {self.model_name} on MIG instance {self.assigned_instance}...")
            
            # Get optimal settings
            n_gpu_layers, n_threads = self._get_mig_optimal_settings()
            
            # Set CUDA device if using MIG
            if self.cuda_device and self.cuda_device.startswith('cuda:'):
                os.environ['CUDA_VISIBLE_DEVICES'] = self.cuda_device.split(':')[1]
            elif self.cuda_device and 'MIG' in self.cuda_device:
                # For MIG UUIDs, we need to use nvidia-ml-py or set appropriate env vars
                os.environ['CUDA_MIG_VISIBLE_DEVICES'] = self.cuda_device
            
            # Load model with MIG-optimized settings
            self.model = Llama(
                model_path=self.model_path,
                n_ctx=4096,  # Context window
                n_threads=n_threads,
                n_gpu_layers=n_gpu_layers,
                verbose=False,
                use_mmap=True,
                use_mlock=False,
                n_batch=512,
                f16_kv=True,
                # MIG-specific optimizations
                tensor_split=None,  # Let llama.cpp handle MIG automatically
                main_gpu=0,  # Use the assigned MIG instance
            )
            
            self.model_loaded_in_memory = True
            
            if hasattr(st, 'success'):
                st.success(f"✅ {self.model_name} loaded on MIG instance {self.assigned_instance}!")
            else:
                print(f"✅ {self.model_name} loaded on MIG instance {self.assigned_instance}!")
            
        except ImportError:
            error_msg = "llama-cpp-python not installed. Install with: pip install llama-cpp-python"
            if hasattr(st, 'error'):
                st.error(f"❌ {error_msg}")
            else:
                print(f"❌ {error_msg}")
            self.model_loaded_in_memory = False
            
        except Exception as e:
            self.model_loaded_in_memory = False
            error_msg = str(e)
            
            if hasattr(st, 'error'):
                st.error(f"❌ Failed to load model on MIG: {error_msg}")
            else:
                print(f"❌ Failed to load model on MIG: {error_msg}")
            
            # Release MIG instance on failure
            self._release_mig_instance()
    
    def _get_mig_optimal_settings(self) -> tuple[int, int]:
        """Get optimal settings for MIG instance"""
        
        # For MIG instances, we can be more aggressive with GPU layers
        # since we have dedicated memory
        if self.assigned_instance:
            # Use all GPU layers for MIG instances
            n_gpu_layers = -1
            
            # Reduce CPU threads since we're using GPU
            n_threads = 4
        else:
            # Fallback to regular GPU detection
            n_gpu_layers = self._get_optimal_gpu_layers()
            n_threads = self._get_optimal_threads()
        
        return n_gpu_layers, n_threads
    
    def __del__(self):
        """Cleanup: release MIG instance when client is destroyed"""
        self._release_mig_instance()
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information including MIG details"""
        base_info = super().get_model_info()
        
        base_info.update({
            "model_id": self.model_id,
            "mig_instance": self.assigned_instance,
            "cuda_device": self.cuda_device,
            "memory_requirement_gb": self.memory_requirement_gb,
            "backend": "llama.cpp (MIG-enabled)"
        })
        
        return base_info

class MIGModelPool:
    """Pool of MIG-enabled models for parallel processing"""
    
    def __init__(self):
        self.mig_manager = MIGManager()
        self.clients: Dict[str, MIGLlamaCppClient] = {}
        self.initialized = False
    
    def initialize(self) -> bool:
        """Initialize MIG and discover instances"""
        if self.initialized:
            return True
        
        print("🚀 Initializing MIG Model Pool...")
        
        # Discover MIG instances
        instances = self.mig_manager.discover_mig_instances()
        
        if len(instances) < 2:
            print(f"⚠️ Only {len(instances)} MIG instances found")
            print("💡 Consider running: sudo python mig_manager.py --setup")
            return False
        
        print(f"✅ Found {len(instances)} MIG instances")
        self.initialized = True
        return True
    
    def create_client(self, model_path: str, model_id: str) -> Optional[MIGLlamaCppClient]:
        """Create a new MIG-aware client"""
        if not self.initialize():
            return None
        
        if model_id in self.clients:
            print(f"⚠️ Client {model_id} already exists")
            return self.clients[model_id]
        
        client = MIGLlamaCppClient(
            model_path=model_path,
            model_id=model_id,
            mig_manager=self.mig_manager
        )
        
        self.clients[model_id] = client
        return client
    
    def get_client(self, model_id: str) -> Optional[MIGLlamaCppClient]:
        """Get existing client by ID"""
        return self.clients.get(model_id)
    
    def remove_client(self, model_id: str):
        """Remove and cleanup client"""
        if model_id in self.clients:
            client = self.clients[model_id]
            client._release_mig_instance()
            del self.clients[model_id]
    
    def get_pool_status(self) -> Dict[str, Any]:
        """Get status of the model pool"""
        return {
            "initialized": self.initialized,
            "total_instances": len(self.mig_manager.instances),
            "active_clients": len(self.clients),
            "available_instances": sum(1 for i in self.mig_manager.instances if i.available),
            "clients": {cid: client.get_model_info() for cid, client in self.clients.items()}
        }
    
    def print_status(self):
        """Print pool status"""
        status = self.get_pool_status()
        
        print("\n🏊 MIG Model Pool Status")
        print("=" * 40)
        print(f"Initialized: {status['initialized']}")
        print(f"Total MIG Instances: {status['total_instances']}")
        print(f"Active Clients: {status['active_clients']}")
        print(f"Available Instances: {status['available_instances']}")
        
        if status['clients']:
            print("\nActive Clients:")
            for client_id, info in status['clients'].items():
                print(f"  {client_id}: {info['name']} on {info['mig_instance']}")

# Global model pool instance
_global_mig_pool = None

def get_mig_pool() -> MIGModelPool:
    """Get global MIG model pool"""
    global _global_mig_pool
    if _global_mig_pool is None:
        _global_mig_pool = MIGModelPool()
    return _global_mig_pool

def create_mig_client(model_path: str, model_id: str) -> Optional[MIGLlamaCppClient]:
    """Convenience function to create MIG client"""
    pool = get_mig_pool()
    return pool.create_client(model_path, model_id)