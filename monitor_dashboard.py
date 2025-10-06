#!/usr/bin/env python3
"""
Real-time monitoring dashboard for Mac Studios
Updates every 2 seconds with live stats
"""

import subprocess
import time
import sys
from datetime import datetime

def clear_screen():
    """Clear the terminal screen"""
    print("\033[2J\033[H", end="")

def get_mac_stats(user, ip, name):
    """Get stats from a Mac Studio"""
    try:
        # Get CPU and Memory
        cmd = f"""ssh {user}@{ip} "top -l 1 | head -20" """
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=5)
        
        stats = {
            'name': name,
            'ip': ip,
            'cpu_user': '?',
            'cpu_system': '?',
            'cpu_idle': '?',
            'mem_used': '?',
            'mem_free': '?',
            'server_status': '❌'
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
        
        # Check server health
        port = '5001' if '0.1' in ip else '5002'
        health_cmd = f"curl -s http://{ip}:{port}/health"
        health_result = subprocess.run(health_cmd, shell=True, capture_output=True, timeout=2)
        if health_result.returncode == 0 and b'healthy' in health_result.stdout:
            stats['server_status'] = '✅'
        
        return stats
        
    except Exception as e:
        return {
            'name': name,
            'ip': ip,
            'cpu_user': 'ERROR',
            'cpu_system': 'ERROR',
            'cpu_idle': 'ERROR',
            'mem_used': 'ERROR',
            'mem_free': 'ERROR',
            'server_status': '❌'
        }

def display_dashboard(mac1_stats, mac2_stats):
    """Display the monitoring dashboard"""
    clear_screen()
    
    print("━" * 100)
    print("🖥️  MAC STUDIO REAL-TIME MONITORING DASHBOARD".center(100))
    print("━" * 100)
    print(f"⏱️  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}".center(100))
    print("━" * 100)
    print()
    
    # Mac Studio 1
    print("┌" + "─" * 98 + "┐")
    print(f"│ 🖥️  {mac1_stats['name']:<40} ({mac1_stats['ip']})".ljust(99) + "│")
    print("├" + "─" * 98 + "┤")
    print(f"│ 📊 CPU:  User: {mac1_stats['cpu_user']:<8} System: {mac1_stats['cpu_system']:<8} Idle: {mac1_stats['cpu_idle']:<8}".ljust(99) + "│")
    print(f"│ 💾 MEM:  Used: {mac1_stats['mem_used']:<12} Free: {mac1_stats['mem_free']:<12}".ljust(99) + "│")
    print(f"│ 🌐 Server: {mac1_stats['server_status']} GPT-OSS (Port 5001)".ljust(99) + "│")
    print("└" + "─" * 98 + "┘")
    print()
    
    # Mac Studio 2
    print("┌" + "─" * 98 + "┐")
    print(f"│ 🖥️  {mac2_stats['name']:<40} ({mac2_stats['ip']})".ljust(99) + "│")
    print("├" + "─" * 98 + "┤")
    print(f"│ 📊 CPU:  User: {mac2_stats['cpu_user']:<8} System: {mac2_stats['cpu_system']:<8} Idle: {mac2_stats['cpu_idle']:<8}".ljust(99) + "│")
    print(f"│ 💾 MEM:  Used: {mac2_stats['mem_used']:<12} Free: {mac2_stats['mem_free']:<12}".ljust(99) + "│")
    print(f"│ 🌐 Server: {mac2_stats['server_status']} Qwen (Port 5002)".ljust(99) + "│")
    print("└" + "─" * 98 + "┘")
    print()
    
    print("━" * 100)
    print("💡 Press Ctrl+C to exit".center(100))
    print("━" * 100)

def main():
    """Main monitoring loop"""
    print("Starting real-time monitoring...")
    print("Connecting to Mac Studios...")
    time.sleep(1)
    
    try:
        while True:
            # Get stats from both Macs (different usernames!)
            mac1_stats = get_mac_stats("humphrjk", "10.55.0.1", "Mac Studio 1 (GPT-OSS)")
            mac2_stats = get_mac_stats("jamiehumphries", "10.55.0.2", "Mac Studio 2 (Qwen)")
            
            # Display dashboard
            display_dashboard(mac1_stats, mac2_stats)
            
            # Wait 2 seconds before next update
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n\n✅ Monitoring stopped")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
