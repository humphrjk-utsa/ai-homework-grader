#!/usr/bin/env python3
"""
Performance Logger for Mac Studios
Captures metrics and saves to CSV for later analysis
"""

import subprocess
import time
import csv
import json
import requests
from datetime import datetime
from pathlib import Path

class PerformanceLogger:
    """Logs performance metrics from both Mac Studios"""
    
    def __init__(self, log_dir: str = "performance_logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Create timestamped log file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"performance_log_{timestamp}.csv"
        
        # Initialize CSV
        self.fieldnames = [
            'timestamp',
            'mac1_name', 'mac1_cpu_user', 'mac1_cpu_system', 'mac1_cpu_idle',
            'mac1_mem_used', 'mac1_mem_free', 'mac1_server_status',
            'mac1_tokens_per_sec', 'mac1_active_requests',
            'mac2_name', 'mac2_cpu_user', 'mac2_cpu_system', 'mac2_cpu_idle',
            'mac2_mem_used', 'mac2_mem_free', 'mac2_server_status',
            'mac2_tokens_per_sec', 'mac2_active_requests',
            'event', 'notes'
        ]
        
        with open(self.log_file, 'w', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames)
            writer.writeheader()
        
        print(f"📊 Logging to: {self.log_file}")
    
    def get_mac_stats(self, user: str, ip: str, name: str) -> dict:
        """Get stats from a Mac Studio"""
        try:
            # Get CPU and Memory
            cmd = f"""ssh {user}@{ip} "top -l 1 | head -20" """
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
            
            stats = {
                'name': name,
                'cpu_user': '0%',
                'cpu_system': '0%',
                'cpu_idle': '100%',
                'mem_used': '0G',
                'mem_free': '0G',
                'server_status': '❌',
                'tokens_per_sec': 0,
                'active_requests': 0
            }
            
            if result.returncode == 0:
                lines = result.stdout.split('\n')
                for line in lines:
                    if 'CPU usage' in line:
                        parts = line.split()
                        if len(parts) >= 7:
                            stats['cpu_user'] = parts[2]
                            stats['cpu_system'] = parts[4]
                            stats['cpu_idle'] = parts[6]
                    elif 'PhysMem' in line:
                        parts = line.split()
                        if len(parts) >= 6:
                            stats['mem_used'] = parts[1]
                            stats['mem_free'] = parts[5]
            
            # Check server health and get performance metrics
            port = '5001' if '0.1' in ip else '5002'
            try:
                response = requests.get(f"http://{ip}:{port}/health", timeout=3)
                if response.status_code == 200:
                    stats['server_status'] = '✅'
                    data = response.json()
                    stats['tokens_per_sec'] = data.get('tokens_per_second', 0)
                    stats['active_requests'] = data.get('active_requests', 0)
            except:
                pass
            
            return stats
            
        except Exception as e:
            print(f"⚠️ Error getting stats from {name}: {e}")
            return {
                'name': name,
                'cpu_user': 'ERROR',
                'cpu_system': 'ERROR',
                'cpu_idle': 'ERROR',
                'mem_used': 'ERROR',
                'mem_free': 'ERROR',
                'server_status': '❌',
                'tokens_per_sec': 0,
                'active_requests': 0
            }
    
    def log_snapshot(self, event: str = "", notes: str = ""):
        """Log a single snapshot of both Mac Studios"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Get stats from both Macs
        mac1_stats = self.get_mac_stats("humphrjk", "10.55.0.1", "Mac Studio 1 (GPT-OSS)")
        mac2_stats = self.get_mac_stats("jamiehumphries", "10.55.0.2", "Mac Studio 2 (Qwen)")
        
        # Create log entry
        entry = {
            'timestamp': timestamp,
            'mac1_name': mac1_stats['name'],
            'mac1_cpu_user': mac1_stats['cpu_user'],
            'mac1_cpu_system': mac1_stats['cpu_system'],
            'mac1_cpu_idle': mac1_stats['cpu_idle'],
            'mac1_mem_used': mac1_stats['mem_used'],
            'mac1_mem_free': mac1_stats['mem_free'],
            'mac1_server_status': mac1_stats['server_status'],
            'mac1_tokens_per_sec': mac1_stats['tokens_per_sec'],
            'mac1_active_requests': mac1_stats['active_requests'],
            'mac2_name': mac2_stats['name'],
            'mac2_cpu_user': mac2_stats['cpu_user'],
            'mac2_cpu_system': mac2_stats['cpu_system'],
            'mac2_cpu_idle': mac2_stats['cpu_idle'],
            'mac2_mem_used': mac2_stats['mem_used'],
            'mac2_mem_free': mac2_stats['mem_free'],
            'mac2_server_status': mac2_stats['server_status'],
            'mac2_tokens_per_sec': mac2_stats['tokens_per_sec'],
            'mac2_active_requests': mac2_stats['active_requests'],
            'event': event,
            'notes': notes
        }
        
        # Write to CSV
        with open(self.log_file, 'a', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=self.fieldnames)
            writer.writerow(entry)
        
        return entry
    
    def start_continuous_logging(self, interval: int = 5):
        """Start continuous logging at specified interval (seconds)"""
        print(f"🔄 Starting continuous logging every {interval} seconds")
        print(f"📊 Log file: {self.log_file}")
        print("Press Ctrl+C to stop\n")
        
        try:
            while True:
                entry = self.log_snapshot()
                
                # Print summary
                print(f"[{entry['timestamp']}]")
                print(f"  Mac 1: CPU {entry['mac1_cpu_user']} | Mem {entry['mac1_mem_used']} | {entry['mac1_server_status']} | {entry['mac1_tokens_per_sec']:.1f} tok/s")
                print(f"  Mac 2: CPU {entry['mac2_cpu_user']} | Mem {entry['mac2_mem_used']} | {entry['mac2_server_status']} | {entry['mac2_tokens_per_sec']:.1f} tok/s")
                print()
                
                time.sleep(interval)
                
        except KeyboardInterrupt:
            print("\n\n✅ Logging stopped")
            print(f"📊 Log saved to: {self.log_file}")


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Log Mac Studio performance metrics')
    parser.add_argument('--interval', type=int, default=5, help='Logging interval in seconds (default: 5)')
    parser.add_argument('--log-dir', type=str, default='performance_logs', help='Directory for log files')
    parser.add_argument('--single', action='store_true', help='Log single snapshot and exit')
    parser.add_argument('--event', type=str, default='', help='Event name for single snapshot')
    parser.add_argument('--notes', type=str, default='', help='Notes for single snapshot')
    
    args = parser.parse_args()
    
    logger = PerformanceLogger(log_dir=args.log_dir)
    
    if args.single:
        entry = logger.log_snapshot(event=args.event, notes=args.notes)
        print(f"✅ Logged snapshot at {entry['timestamp']}")
    else:
        logger.start_continuous_logging(interval=args.interval)


if __name__ == '__main__':
    main()
