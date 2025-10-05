#!/usr/bin/env python3
"""
Distributed Server Manager
Manages, monitors, and auto-restarts MLX servers on Mac Studios
"""

import json
import subprocess
import time
import requests
import logging
from typing import Dict, Tuple

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ServerManager:
    """Manages distributed MLX servers"""
    
    def __init__(self, config_path: str = "server_config.json"):
        with open(config_path, 'r') as f:
            self.config = json.load(f)
        
        self.servers = {
            'mac_studio_1': self.config['mac_studio_1'],
            'mac_studio_2': self.config['mac_studio_2']
        }
        self.auto_restart_config = self.config['auto_restart']
    
    def check_server_health(self, server_name: str) -> Tuple[bool, str]:
        """Check if a server is healthy"""
        server = self.servers[server_name]
        url = f"http://{server['ip']}:{server['port']}/health"
        
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data.get('status') == 'healthy' and data.get('loaded'):
                    return True, "Server is healthy"
                else:
                    return False, f"Server unhealthy: {data}"
            else:
                return False, f"HTTP {response.status_code}"
        except requests.exceptions.RequestException as e:
            return False, f"Connection failed: {str(e)}"
    
    def restart_server(self, server_name: str) -> Tuple[bool, str]:
        """Restart a server"""
        server = self.servers[server_name]
        
        logger.info(f"🔄 Restarting {server['name']}...")
        
        # Step 1: Kill existing process
        kill_cmd = f"ssh {server['username']}@{server['ip']} 'pkill -f {server['server_path'].split('/')[-1]}'"
        try:
            subprocess.run(kill_cmd, shell=True, timeout=10)
            logger.info(f"✅ Killed existing process on {server_name}")
            time.sleep(2)
        except Exception as e:
            logger.warning(f"⚠️ Could not kill process: {e}")
        
        # Step 2: Start new process
        server_dir = '/'.join(server['server_path'].split('/')[:-1])
        server_file = server['server_path'].split('/')[-1]
        
        start_cmd = f"ssh {server['username']}@{server['ip']} 'cd {server_dir} && nohup python3 {server_file} > server.log 2>&1 &'"
        
        try:
            subprocess.run(start_cmd, shell=True, timeout=10)
            logger.info(f"🚀 Started server on {server_name}")
            
            # Wait for server to start
            time.sleep(5)
            
            # Verify it's running
            is_healthy, message = self.check_server_health(server_name)
            if is_healthy:
                logger.info(f"✅ {server['name']} restarted successfully!")
                return True, "Server restarted and healthy"
            else:
                logger.error(f"❌ Server started but not healthy: {message}")
                return False, f"Server unhealthy after restart: {message}"
                
        except Exception as e:
            logger.error(f"❌ Failed to restart: {e}")
            return False, f"Restart failed: {str(e)}"
    
    def restart_with_retry(self, server_name: str) -> bool:
        """Restart server with retries"""
        max_retries = self.auto_restart_config['max_retries']
        retry_delay = self.auto_restart_config['retry_delay_seconds']
        
        for attempt in range(1, max_retries + 1):
            logger.info(f"🔄 Restart attempt {attempt}/{max_retries} for {server_name}")
            
            success, message = self.restart_server(server_name)
            if success:
                return True
            
            if attempt < max_retries:
                logger.warning(f"⚠️ Attempt {attempt} failed: {message}. Retrying in {retry_delay}s...")
                time.sleep(retry_delay)
        
        logger.error(f"❌ Failed to restart {server_name} after {max_retries} attempts")
        return False
    
    def check_all_servers(self) -> Dict[str, bool]:
        """Check health of all servers"""
        results = {}
        
        for server_name, server in self.servers.items():
            is_healthy, message = self.check_server_health(server_name)
            results[server_name] = is_healthy
            
            status_emoji = "✅" if is_healthy else "❌"
            logger.info(f"{status_emoji} {server['name']}: {message}")
        
        return results
    
    def auto_restart_if_needed(self, server_name: str) -> bool:
        """Check server and auto-restart if down"""
        if not self.auto_restart_config['enabled']:
            logger.info("Auto-restart is disabled")
            return False
        
        is_healthy, message = self.check_server_health(server_name)
        
        if is_healthy:
            logger.info(f"✅ {server_name} is healthy")
            return True
        
        logger.warning(f"⚠️ {server_name} is down: {message}")
        logger.info(f"🔄 Auto-restarting {server_name}...")
        
        return self.restart_with_retry(server_name)
    
    def ensure_all_servers_running(self) -> Dict[str, bool]:
        """Ensure all servers are running, restart if needed"""
        results = {}
        
        for server_name in self.servers.keys():
            results[server_name] = self.auto_restart_if_needed(server_name)
        
        return results
    
    def get_server_status(self) -> Dict:
        """Get detailed status of all servers"""
        status = {}
        
        for server_name, server in self.servers.items():
            is_healthy, message = self.check_server_health(server_name)
            
            status[server_name] = {
                'name': server['name'],
                'ip': server['ip'],
                'port': server['port'],
                'model': server['model'],
                'healthy': is_healthy,
                'message': message,
                'url': f"http://{server['ip']}:{server['port']}"
            }
        
        return status


def main():
    """CLI for server management"""
    import sys
    
    manager = ServerManager()
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python server_manager.py check          - Check all servers")
        print("  python server_manager.py restart <name> - Restart specific server")
        print("  python server_manager.py restart-all    - Restart all servers")
        print("  python server_manager.py ensure         - Ensure all running (auto-restart if down)")
        print("  python server_manager.py status         - Get detailed status")
        return
    
    command = sys.argv[1]
    
    if command == "check":
        print("\n🔍 Checking all servers...")
        results = manager.check_all_servers()
        print(f"\n📊 Results: {sum(results.values())}/{len(results)} servers healthy")
    
    elif command == "restart":
        if len(sys.argv) < 3:
            print("❌ Please specify server name: mac_studio_1 or mac_studio_2")
            return
        
        server_name = sys.argv[2]
        if server_name not in manager.servers:
            print(f"❌ Unknown server: {server_name}")
            return
        
        print(f"\n🔄 Restarting {server_name}...")
        success = manager.restart_with_retry(server_name)
        if success:
            print(f"✅ {server_name} restarted successfully!")
        else:
            print(f"❌ Failed to restart {server_name}")
    
    elif command == "restart-all":
        print("\n🔄 Restarting all servers...")
        for server_name in manager.servers.keys():
            manager.restart_with_retry(server_name)
    
    elif command == "ensure":
        print("\n🔍 Ensuring all servers are running...")
        results = manager.ensure_all_servers_running()
        healthy_count = sum(results.values())
        print(f"\n📊 Results: {healthy_count}/{len(results)} servers running")
    
    elif command == "status":
        print("\n📊 Server Status:")
        status = manager.get_server_status()
        for server_name, info in status.items():
            print(f"\n{info['name']}:")
            print(f"  URL: {info['url']}")
            print(f"  Model: {info['model']}")
            print(f"  Status: {'✅ Healthy' if info['healthy'] else '❌ Down'}")
            print(f"  Message: {info['message']}")
    
    else:
        print(f"❌ Unknown command: {command}")


if __name__ == "__main__":
    main()
