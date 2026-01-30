#!/usr/bin/env python3
"""
System Health Check and Auto-Start for Disaggregated Inference
Checks all servers, models, and connections. Auto-starts missing services.
"""
import requests
import subprocess
import json
import time
import os
from typing import Dict, List, Tuple
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SystemHealthCheck:
    """Check and auto-start disaggregated inference system"""
    
    def __init__(self, config_path: str = "disaggregated_inference/config_current.json"):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.prefill_servers = self.config['prefill_servers']
        self.decode_servers = self.config['decode_servers']
        self.status = {
            'prefill': {},
            'decode': {},
            'overall': 'unknown'
        }
    
    def check_server_health(self, host: str, port: int, name: str) -> Dict:
        """Check if a server is healthy"""
        try:
            response = requests.get(f"http://{host}:{port}/health", timeout=3)
            if response.status_code == 200:
                data = response.json()
                return {
                    'status': 'healthy',
                    'model': data.get('model', 'unknown'),
                    'loaded': data.get('loaded', False),
                    'backend': data.get('backend', 'unknown'),
                    'reachable': True
                }
        except requests.exceptions.Timeout:
            return {'status': 'timeout', 'reachable': False, 'error': 'Connection timeout'}
        except requests.exceptions.ConnectionError:
            return {'status': 'unreachable', 'reachable': False, 'error': 'Cannot connect'}
        except Exception as e:
            return {'status': 'error', 'reachable': False, 'error': str(e)}
    
    def check_ollama_running(self, host: str) -> bool:
        """Check if Ollama is running on a host"""
        try:
            response = requests.get(f"http://{host}:11434/api/tags", timeout=2)
            return response.status_code == 200
        except:
            return False
    
    def start_ollama_local(self) -> bool:
        """Start Ollama on local machine"""
        try:
            logger.info("🚀 Starting Ollama locally...")
            
            # Check if already running
            if self.check_ollama_running('localhost'):
                logger.info("✅ Ollama already running locally")
                return True
            
            # Start Ollama in background
            cmd = 'nohup ollama serve > /tmp/ollama.log 2>&1 &'
            subprocess.run(cmd, shell=True, check=True)
            
            # Wait for Ollama to start
            time.sleep(3)
            
            if self.check_ollama_running('localhost'):
                logger.info("✅ Ollama started successfully")
                return True
            else:
                logger.warning("⚠️  Ollama started but not responding yet")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to start Ollama: {e}")
            return False
    
    def start_ollama_remote(self, host: str) -> bool:
        """Start Ollama on remote machine via SSH"""
        try:
            logger.info(f"🚀 Starting Ollama on {host}...")
            
            # Check if already running
            if self.check_ollama_running(host):
                logger.info(f"✅ Ollama already running on {host}")
                return True
            
            # Try to find Ollama executable
            find_cmd = ['ssh', host, 'which ollama || find /Applications -name "ollama" -type f 2>/dev/null | head -1']
            result = subprocess.run(find_cmd, capture_output=True, text=True, timeout=5)
            ollama_path = result.stdout.strip()
            
            if not ollama_path:
                # Try common locations
                ollama_path = '/usr/local/bin/ollama'
            
            # Start Ollama via SSH
            cmd = ['ssh', host, f'nohup {ollama_path} serve > /tmp/ollama.log 2>&1 &']
            subprocess.run(cmd, timeout=5, check=True)
            
            # Wait for Ollama to start
            time.sleep(3)
            
            if self.check_ollama_running(host):
                logger.info(f"✅ Ollama started on {host}")
                return True
            else:
                logger.warning(f"⚠️  Ollama started on {host} but not responding yet")
                return False
                
        except Exception as e:
            logger.error(f"❌ Failed to start Ollama on {host}: {e}")
            return False
    
    def start_macs_fan_control_local(self) -> bool:
        """Start Macs Fan Control app locally"""
        try:
            logger.info("🌀 Starting Macs Fan Control locally...")
            
            # Check if already running
            check_cmd = "ps aux | grep 'Macs Fan Control' | grep -v grep"
            result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True)
            
            if result.returncode == 0:
                logger.info("✅ Macs Fan Control already running locally")
                return True
            
            # Try to open the app
            cmd = 'open -a "Macs Fan Control"'
            subprocess.run(cmd, shell=True, check=True)
            
            time.sleep(2)
            logger.info("✅ Macs Fan Control started locally")
            return True
            
        except Exception as e:
            logger.warning(f"⚠️  Could not start Macs Fan Control locally: {e}")
            return False
    
    def start_macs_fan_control_remote(self, host: str) -> bool:
        """Start Macs Fan Control app on remote machine"""
        try:
            logger.info(f"🌀 Starting Macs Fan Control on {host}...")
            
            # Check if already running
            check_cmd = ['ssh', f'humphrjk@{host}', "ps aux | grep 'Macs Fan Control' | grep -v grep"]
            result = subprocess.run(check_cmd, capture_output=True, text=True, timeout=5)
            
            if result.returncode == 0:
                logger.info(f"✅ Macs Fan Control already running on {host}")
                return True
            
            # Try to open the app directly
            cmd = ['ssh', f'humphrjk@{host}', 'open -a "Macs Fan Control" 2>/dev/null || ~/start_macs_fan.sh 2>/dev/null']
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            
            time.sleep(2)
            
            # Check if it started
            check_result = subprocess.run(check_cmd, capture_output=True, text=True, timeout=5)
            if check_result.returncode == 0:
                logger.info(f"✅ Macs Fan Control started on {host}")
                return True
            else:
                logger.warning(f"⚠️  Macs Fan Control may not have started on {host}")
                return False
            
        except Exception as e:
            logger.warning(f"⚠️  Could not start Macs Fan Control on {host}: {e}")
            return False
    
    def start_decode_server_local(self, model: str, port: int) -> bool:
        """Start decode server on local machine"""
        try:
            logger.info(f"🚀 Starting local decode server for {model} on port {port}")
            
            # Get the directory where this script is located
            import os
            script_dir = os.path.dirname(os.path.abspath(__file__))
            decode_script = os.path.join(script_dir, 'disaggregated_inference', 'decode_server_ollama.py')
            
            # Find venv python
            venv_python = os.path.join(script_dir, '.venv', 'bin', 'python3')
            if not os.path.exists(venv_python):
                venv_python = 'python3'  # Fallback to system python
            
            # Start in background using nohup
            cmd = f'nohup {venv_python} {decode_script} --model {model} --port {port} --host 0.0.0.0 > /tmp/decode_{port}.log 2>&1 &'
            
            subprocess.run(cmd, shell=True, check=True)
            
            # Wait for server to start
            logger.info(f"⏳ Waiting for decode server to initialize...")
            time.sleep(5)
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start decode server: {e}")
            return False
    
    def start_decode_server_remote(self, host: str, model: str, port: int) -> bool:
        """Start decode server on remote machine via SSH"""
        try:
            logger.info(f"🚀 Starting remote decode server on {host} for {model}")
            
            # Find the correct path on remote machine
            find_cmd = [
                'ssh', f'humphrjk@{host}',
                'find ~ -name "decode_server_ollama.py" -path "*/disaggregated_inference/*" 2>/dev/null | head -1'
            ]
            
            result = subprocess.run(find_cmd, capture_output=True, text=True, timeout=10)
            remote_script = result.stdout.strip()
            
            if not remote_script:
                logger.error(f"❌ Could not find decode_server_ollama.py on {host}")
                return False
            
            remote_dir = os.path.dirname(remote_script)
            
            # SSH command to start server in background
            cmd = [
                'ssh', f'humphrjk@{host}',
                f'cd {os.path.dirname(remote_dir)} && '
                f'nohup python3 {remote_script} '
                f'--model {model} --port {port} --host 0.0.0.0 '
                f'> /tmp/decode_{port}.log 2>&1 &'
            ]
            
            subprocess.run(cmd, timeout=10, check=True)
            
            # Wait for server to start
            logger.info(f"⏳ Waiting for remote decode server to initialize...")
            time.sleep(5)
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start remote decode server: {e}")
            return False
    
    def check_all_servers(self) -> Dict:
        """Check health of all servers"""
        logger.info("🔍 Checking system health...")
        
        # Check prefill servers
        for server in self.prefill_servers:
            name = server['name']
            host = server['host']
            port = server['port']
            
            logger.info(f"  Checking {name} ({host}:{port})...")
            health = self.check_server_health(host, port, name)
            self.status['prefill'][name] = health
            
            if health['status'] == 'healthy':
                logger.info(f"    ✅ {name}: Healthy - Model: {health['model']}")
            else:
                logger.warning(f"    ❌ {name}: {health['status']} - {health.get('error', '')}")
        
        # Check decode servers
        for server in self.decode_servers:
            name = server['name']
            host = server['host']
            port = server['port']
            model = server.get('comment', '').split('Has ')[-1] if 'Has' in server.get('comment', '') else server['model']
            
            logger.info(f"  Checking {name} ({host}:{port})...")
            health = self.check_server_health(host, port, name)
            self.status['decode'][name] = health
            self.status['decode'][name]['expected_model'] = model
            self.status['decode'][name]['host'] = host
            self.status['decode'][name]['port'] = port
            
            if health['status'] == 'healthy':
                logger.info(f"    ✅ {name}: Healthy - Model: {health['model']}")
            else:
                logger.warning(f"    ❌ {name}: {health['status']} - {health.get('error', '')}")
        
        return self.status
    
    def start_prefill_server_remote(self, host: str, model: str, port: int) -> bool:
        """Start prefill server on remote DGX machine via SSH"""
        try:
            logger.info(f"🚀 Starting remote prefill server on {host} for {model}")
            
            # Find the correct path on remote machine
            find_cmd = [
                'ssh', f'humphrjk@{host}',
                'find ~ -name "prefill_server_ollama.py" 2>/dev/null | head -1'
            ]
            
            result = subprocess.run(find_cmd, capture_output=True, text=True, timeout=10)
            remote_script = result.stdout.strip()
            
            if not remote_script:
                logger.error(f"❌ Could not find prefill_server_ollama.py on {host}")
                return False
            
            remote_dir = os.path.dirname(remote_script)
            
            # SSH command to start server in background
            cmd = [
                'ssh', f'humphrjk@{host}',
                f'cd {remote_dir} && '
                f'nohup python3 {remote_script} '
                f'--model {model} --port {port} --host 0.0.0.0 '
                f'> ~/prefill_{port}.log 2>&1 &'
            ]
            
            subprocess.run(cmd, timeout=10, check=True)
            
            # Wait for server to start
            logger.info(f"⏳ Waiting for remote prefill server to initialize...")
            time.sleep(5)
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to start remote prefill server: {e}")
            return False
    
    def auto_start_missing_services(self) -> bool:
        """Auto-start any missing prefill servers, decode servers, Ollama, and Macs Fan Control"""
        logger.info("🔧 Auto-starting missing services...")
        
        started_any = False
        
        # First, start prefill servers on DGX Sparks
        logger.info("🖥️  Checking prefill servers...")
        for server in self.prefill_servers:
            name = server['name']
            host = server['host']
            port = server['port']
            model_key = server['model']
            
            # Get expected model name
            if 'qwen' in model_key.lower():
                model = 'hopephoto/qwen3-coder-30b-a3b-instruct_q8:latest'
            else:
                model = 'gpt-oss:120b'
            
            health = self.status['prefill'].get(name, {})
            
            if health.get('status') != 'healthy':
                logger.info(f"  Starting {name} prefill server...")
                success = self.start_prefill_server_remote(host, model, port)
                
                if success:
                    logger.info(f"    ✅ Started {name}")
                    started_any = True
                else:
                    logger.error(f"    ❌ Failed to start {name}")
        
        # Second, start Macs Fan Control on all Mac machines
        logger.info("🌀 Starting Macs Fan Control on all Macs...")
        
        # Start locally
        if self.start_macs_fan_control_local():
            started_any = True
        
        # Start on remote Macs
        unique_hosts = set()
        for server in self.decode_servers:
            host = server['host']
            if host not in ['localhost', '127.0.0.1', '169.254.150.101']:
                unique_hosts.add(host)
        
        for host in unique_hosts:
            if self.start_macs_fan_control_remote(host):
                started_any = True
        
        # Second, ensure Ollama is running on all machines
        logger.info("📡 Checking Ollama status on all machines...")
        
        # Check local Ollama
        if not self.check_ollama_running('localhost'):
            logger.info("  Starting Ollama locally...")
            if self.start_ollama_local():
                started_any = True
        
        # Check Ollama on all unique hosts
        for host in unique_hosts:
            if not self.check_ollama_running(host):
                logger.info(f"  Starting Ollama on {host}...")
                if self.start_ollama_remote(host):
                    started_any = True
        
        # Now start decode servers
        logger.info("🖥️  Checking decode servers...")
        for server in self.decode_servers:
            name = server['name']
            host = server['host']
            port = server['port']
            model_key = server['model']
            
            # Get expected model name
            if 'qwen' in model_key.lower():
                model = 'qwen3-coder:30b'
            else:
                model = 'gpt-oss:120b'
            
            health = self.status['decode'].get(name, {})
            
            if health.get('status') != 'healthy':
                logger.info(f"  Starting {name} decode server...")
                
                # Check if this is localhost
                if host in ['localhost', '127.0.0.1', '169.254.150.101']:
                    success = self.start_decode_server_local(model, port)
                else:
                    success = self.start_decode_server_remote(host, model, port)
                
                if success:
                    logger.info(f"    ✅ Started {name}")
                    started_any = True
                else:
                    logger.error(f"    ❌ Failed to start {name}")
        
        return started_any
    
    def get_status_summary(self) -> Dict:
        """Get summary of system status"""
        prefill_healthy = sum(1 for s in self.status['prefill'].values() if s.get('status') == 'healthy')
        prefill_total = len(self.status['prefill'])
        
        decode_healthy = sum(1 for s in self.status['decode'].values() if s.get('status') == 'healthy')
        decode_total = len(self.status['decode'])
        
        all_healthy = (prefill_healthy == prefill_total) and (decode_healthy == decode_total)
        
        return {
            'overall_status': 'healthy' if all_healthy else 'degraded',
            'prefill': {
                'healthy': prefill_healthy,
                'total': prefill_total,
                'percentage': (prefill_healthy / prefill_total * 100) if prefill_total > 0 else 0
            },
            'decode': {
                'healthy': decode_healthy,
                'total': decode_total,
                'percentage': (decode_healthy / decode_total * 100) if decode_total > 0 else 0
            },
            'ready_for_grading': all_healthy
        }
    
    def run_full_check(self, auto_start: bool = True) -> Dict:
        """Run full system check and optionally auto-start services"""
        logger.info("=" * 60)
        logger.info("🏥 SYSTEM HEALTH CHECK")
        logger.info("=" * 60)
        
        # Check all servers
        self.check_all_servers()
        
        # Auto-start if requested
        if auto_start:
            started = self.auto_start_missing_services()
            
            if started:
                logger.info("⏳ Waiting for services to initialize...")
                time.sleep(5)
                
                # Re-check after starting
                logger.info("🔄 Re-checking system health...")
                self.check_all_servers()
        
        # Get summary
        summary = self.get_status_summary()
        
        logger.info("=" * 60)
        logger.info("📊 SYSTEM STATUS SUMMARY")
        logger.info("=" * 60)
        logger.info(f"Overall Status: {summary['overall_status'].upper()}")
        logger.info(f"Prefill Servers: {summary['prefill']['healthy']}/{summary['prefill']['total']} healthy ({summary['prefill']['percentage']:.0f}%)")
        logger.info(f"Decode Servers: {summary['decode']['healthy']}/{summary['decode']['total']} healthy ({summary['decode']['percentage']:.0f}%)")
        logger.info(f"Ready for Grading: {'✅ YES' if summary['ready_for_grading'] else '❌ NO'}")
        logger.info("=" * 60)
        
        return {
            'status': self.status,
            'summary': summary
        }


def main():
    """Run health check from command line"""
    checker = SystemHealthCheck()
    result = checker.run_full_check(auto_start=True)
    
    if result['summary']['ready_for_grading']:
        print("\n✅ System is ready for homework grading!")
        return 0
    else:
        print("\n⚠️  System is not fully operational. Check logs above.")
        return 1


if __name__ == '__main__':
    exit(main())
