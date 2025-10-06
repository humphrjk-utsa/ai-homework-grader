"""
Server Status Manager
Monitor and control Qwen and GPT-OSS servers for different grading modes
"""

import requests
from typing import Dict, Optional
from datetime import datetime


class ServerStatusManager:
    """Manage and monitor AI server status"""
    
    def __init__(self):
        self.servers = {
            'qwen': {
                'name': 'Qwen Coder 30B',
                'url': 'http://10.55.0.2:5002',
                'location': 'Mac Studio 2',
                'purpose': 'Code & Technical Analysis',
                'used_for': ['R/Python Notebooks', 'Tableau Calculations']
            },
            'gpt_oss': {
                'name': 'GPT-OSS 120B',
                'url': 'http://10.55.0.1:5001',
                'location': 'Mac Studio 1',
                'purpose': 'Feedback & Pedagogy',
                'used_for': ['R/Python Notebooks', 'Tableau Dashboards']
            }
        }
    
    def check_server_health(self, server_key: str) -> Dict:
        """Check if a server is responding"""
        server = self.servers.get(server_key)
        if not server:
            return {'status': 'unknown', 'error': 'Server not configured'}
        
        try:
            response = requests.get(
                f"{server['url']}/health",
                timeout=5
            )
            
            if response.status_code == 200:
                return {
                    'status': 'online',
                    'server': server['name'],
                    'location': server['location'],
                    'response_time_ms': response.elapsed.total_seconds() * 1000,
                    'checked_at': datetime.now().isoformat()
                }
            else:
                return {
                    'status': 'error',
                    'server': server['name'],
                    'error': f'HTTP {response.status_code}'
                }
                
        except requests.exceptions.Timeout:
            return {
                'status': 'timeout',
                'server': server['name'],
                'error': 'Server not responding'
            }
        except requests.exceptions.ConnectionError:
            return {
                'status': 'offline',
                'server': server['name'],
                'error': 'Cannot connect to server'
            }
        except Exception as e:
            return {
                'status': 'error',
                'server': server['name'],
                'error': str(e)
            }
    
    def check_all_servers(self) -> Dict:
        """Check status of all servers"""
        status = {}
        for key in self.servers.keys():
            status[key] = self.check_server_health(key)
        return status
    
    def get_servers_for_assignment_type(self, assignment_type: str) -> Dict:
        """Get required servers for an assignment type"""
        configs = {
            'r_notebook': {
                'required': ['qwen', 'gpt_oss'],
                'parallel': True,
                'description': 'R notebook grading requires both servers'
            },
            'python_notebook': {
                'required': ['qwen', 'gpt_oss'],
                'parallel': True,
                'description': 'Python notebook grading requires both servers'
            },
            'tableau': {
                'required': ['qwen', 'gpt_oss'],
                'parallel': True,
                'description': 'Tableau grading: Qwen for calculations, GPT-OSS for design'
            },
            'tableau_technical_only': {
                'required': ['qwen'],
                'parallel': False,
                'description': 'Tableau technical analysis only'
            },
            'tableau_design_only': {
                'required': ['gpt_oss'],
                'parallel': False,
                'description': 'Tableau design feedback only'
            }
        }
        
        return configs.get(assignment_type, {
            'required': [],
            'parallel': False,
            'description': 'Unknown assignment type'
        })
    
    def verify_servers_ready(self, assignment_type: str) -> Dict:
        """Verify all required servers are online for an assignment type"""
        config = self.get_servers_for_assignment_type(assignment_type)
        required_servers = config.get('required', [])
        
        if not required_servers:
            return {
                'ready': False,
                'error': f'Unknown assignment type: {assignment_type}'
            }
        
        status = {}
        all_ready = True
        
        for server_key in required_servers:
            health = self.check_server_health(server_key)
            status[server_key] = health
            if health['status'] != 'online':
                all_ready = False
        
        return {
            'ready': all_ready,
            'assignment_type': assignment_type,
            'required_servers': required_servers,
            'parallel_grading': config.get('parallel', False),
            'server_status': status,
            'description': config.get('description', '')
        }
    
    def get_server_info(self) -> Dict:
        """Get detailed information about all servers"""
        return self.servers
    
    def format_status_display(self, status: Dict) -> str:
        """Format server status for display"""
        lines = []
        lines.append("="*60)
        lines.append("🖥️  AI SERVER STATUS")
        lines.append("="*60)
        
        for key, health in status.items():
            server = self.servers[key]
            status_icon = {
                'online': '✅',
                'offline': '❌',
                'timeout': '⏱️',
                'error': '⚠️',
                'unknown': '❓'
            }.get(health['status'], '❓')
            
            lines.append(f"\n{status_icon} {server['name']}")
            lines.append(f"   Location: {server['location']}")
            lines.append(f"   Purpose: {server['purpose']}")
            lines.append(f"   Status: {health['status'].upper()}")
            
            if health['status'] == 'online':
                lines.append(f"   Response: {health['response_time_ms']:.0f}ms")
            elif 'error' in health:
                lines.append(f"   Error: {health['error']}")
        
        lines.append("\n" + "="*60)
        return "\n".join(lines)


def test_server_status():
    """Test server status checking"""
    manager = ServerStatusManager()
    
    # Check all servers
    print("\n🔍 Checking all servers...")
    status = manager.check_all_servers()
    print(manager.format_status_display(status))
    
    # Check for specific assignment types
    print("\n📋 Server requirements by assignment type:")
    for assignment_type in ['r_notebook', 'tableau', 'tableau_technical_only']:
        print(f"\n{assignment_type}:")
        verification = manager.verify_servers_ready(assignment_type)
        print(f"  Ready: {verification['ready']}")
        print(f"  Required: {', '.join(verification['required_servers'])}")
        print(f"  Parallel: {verification['parallel_grading']}")
        print(f"  {verification['description']}")


if __name__ == "__main__":
    test_server_status()
