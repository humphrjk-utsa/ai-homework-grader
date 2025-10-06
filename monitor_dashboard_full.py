#!/usr/bin/env python3
"""
Real-time monitoring dashboard for Mac Studios with temperature & fans
Requires sudo access on remote Macs
"""

import subprocess
import time
import sys
from datetime import datetime

def clear_screen():
    """Clear the terminal screen"""
    print("\033[2J\033[H", end="")

def get_mac_stats(user, ip, name):
    """Get comprehensive stats from a Mac Studio"""
    try:
        # Get CPU, Memory, GPU, and Thermal info for Apple Silicon
        cmd = f"""ssh {user}@{ip} "top -l 1 | head -20; echo '---POWER---'; sudo powermetrics -i 200 -n 1 --samplers gpu_power,cpu_power,thermal 2>/dev/null | grep -E 'GPU Power|CPU Power|Combined Power|GPU HW active frequency|pressure level' | head -10" """
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        
        stats = {
            'name': name,
            'ip': ip,
            'cpu_user': '?',
            'cpu_system': '?',
            'cpu_idle': '?',
            'mem_used': '?',
            'mem_free': '?',
            'gpu_power': '?',
            'cpu_power': '?',
            'combined_power': '?',
            'gpu_freq': '?',
            'thermal': '?',
            'server_status': '❌',
            'python_cpu': '?'
        }
        
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            power_section = False
            
            for line in lines:
                if '---POWER---' in line:
                    power_section = True
                    continue
                
                if not power_section:
                    # Parse top output
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
                    elif 'python' in line.lower() and 'CPU' in line:
                        parts = line.split()
                        if len(parts) >= 3:
                            stats['python_cpu'] = parts[2]
                else:
                    # Parse power and thermal output
                    if 'GPU Power:' in line:
                        power = line.split(':')[-1].strip()
                        stats['gpu_power'] = power
                    elif 'CPU Power:' in line:
                        power = line.split(':')[-1].strip()
                        stats['cpu_power'] = power
                    elif 'Combined Power' in line:
                        power = line.split(':')[-1].strip()
                        stats['combined_power'] = power
                    elif 'GPU HW active frequency:' in line:
                        freq = line.split(':')[-1].strip()
                        stats['gpu_freq'] = freq
                    elif 'pressure level:' in line:
                        thermal = line.split(':')[-1].strip()
                        stats['thermal'] = thermal
        
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
            'gpu_power': 'ERROR',
            'cpu_power': 'ERROR',
            'combined_power': 'ERROR',
            'gpu_freq': 'ERROR',
            'thermal': 'ERROR',
            'server_status': '❌',
            'python_cpu': 'ERROR'
        }

def get_thermal_color(thermal_str):
    """Get color code based on thermal pressure"""
    thermal_lower = thermal_str.lower()
    if 'trap' in thermal_lower or 'heavy' in thermal_lower:
        return '\033[91m'  # Red - critical
    elif 'moderate' in thermal_lower:
        return '\033[93m'  # Yellow - warning
    else:
        return '\033[92m'  # Green - nominal

def display_dashboard(mac1_stats, mac2_stats):
    """Display the monitoring dashboard"""
    clear_screen()
    
    reset = '\033[0m'
    
    print("━" * 110)
    print("🖥️  MAC STUDIO REAL-TIME MONITORING DASHBOARD (Apple Silicon)".center(110))
    print("━" * 110)
    print(f"⏱️  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}".center(110))
    print("━" * 110)
    print()
    
    # Mac Studio 1
    thermal_color1 = get_thermal_color(mac1_stats['thermal'])
    
    print("┌" + "─" * 108 + "┐")
    print(f"│ 🖥️  {mac1_stats['name']:<40} ({mac1_stats['ip']})".ljust(109) + "│")
    print("├" + "─" * 108 + "┤")
    print(f"│ 📊 CPU:  User: {mac1_stats['cpu_user']:<8} System: {mac1_stats['cpu_system']:<8} Idle: {mac1_stats['cpu_idle']:<8}".ljust(109) + "│")
    print(f"│ 💾 MEM:  Used: {mac1_stats['mem_used']:<12} Free: {mac1_stats['mem_free']:<12}".ljust(109) + "│")
    print(f"│ ⚡ POWER: CPU: {mac1_stats['cpu_power']:<10} GPU: {mac1_stats['gpu_power']:<10} Combined: {mac1_stats['combined_power']:<10}".ljust(109) + "│")
    print(f"│ 🌡️  THERMAL: {thermal_color1}{mac1_stats['thermal']:<15}{reset} GPU Freq: {mac1_stats['gpu_freq']:<15}".ljust(130) + "│")
    print(f"│ 🐍 Python CPU: {mac1_stats['python_cpu']:<8}".ljust(109) + "│")
    print(f"│ 🌐 Server: {mac1_stats['server_status']} GPT-OSS (Port 5001)".ljust(109) + "│")
    print("└" + "─" * 108 + "┘")
    print()
    
    # Mac Studio 2
    thermal_color2 = get_thermal_color(mac2_stats['thermal'])
    
    print("┌" + "─" * 108 + "┐")
    print(f"│ 🖥️  {mac2_stats['name']:<40} ({mac2_stats['ip']})".ljust(109) + "│")
    print("├" + "─" * 108 + "┤")
    print(f"│ 📊 CPU:  User: {mac2_stats['cpu_user']:<8} System: {mac2_stats['cpu_system']:<8} Idle: {mac2_stats['cpu_idle']:<8}".ljust(109) + "│")
    print(f"│ 💾 MEM:  Used: {mac2_stats['mem_used']:<12} Free: {mac2_stats['mem_free']:<12}".ljust(109) + "│")
    print(f"│ ⚡ POWER: CPU: {mac2_stats['cpu_power']:<10} GPU: {mac2_stats['gpu_power']:<10} Combined: {mac2_stats['combined_power']:<10}".ljust(109) + "│")
    print(f"│ 🌡️  THERMAL: {thermal_color2}{mac2_stats['thermal']:<15}{reset} GPU Freq: {mac2_stats['gpu_freq']:<15}".ljust(130) + "│")
    print(f"│ 🐍 Python CPU: {mac2_stats['python_cpu']:<8}".ljust(109) + "│")
    print(f"│ 🌐 Server: {mac2_stats['server_status']} Qwen (Port 5002)".ljust(109) + "│")
    print("└" + "─" * 108 + "┘")
    print()
    
    print("━" * 110)
    print("💡 Press Ctrl+C to exit | 🌡️  Thermal: \033[92mNominal\033[0m | \033[93mModerate\033[0m | \033[91mHeavy/Trapping\033[0m".center(130))
    print("━" * 110)

def main():
    """Main monitoring loop"""
    print("Starting real-time monitoring for Apple Silicon Mac Studios...")
    print("Note: Requires sudo access on remote Macs for power metrics")
    print("Connecting to Mac Studios...")
    time.sleep(1)
    
    try:
        while True:
            # Get stats from both Macs (different usernames!)
            mac1_stats = get_mac_stats("humphrjk", "10.55.0.1", "Mac Studio 1 (GPT-OSS)")
            mac2_stats = get_mac_stats("jamiehumphries", "10.55.0.2", "Mac Studio 2 (Qwen)")
            
            # Display dashboard
            display_dashboard(mac1_stats, mac2_stats)
            
            # Wait 3 seconds before next update (longer due to sudo)
            time.sleep(3)
            
    except KeyboardInterrupt:
        print("\n\n✅ Monitoring stopped")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
