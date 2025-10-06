#!/usr/bin/env python3
"""
Analyze Performance Logs
Generate reports and visualizations from logged performance data
"""

import pandas as pd
import sys
from pathlib import Path
from datetime import datetime

def analyze_log(log_file: str):
    """Analyze a performance log file"""
    
    print(f"📊 Analyzing: {log_file}\n")
    
    # Read CSV
    df = pd.read_csv(log_file)
    
    if df.empty:
        print("❌ No data in log file")
        return
    
    # Parse timestamps
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Calculate duration
    duration = df['timestamp'].max() - df['timestamp'].min()
    
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Start Time: {df['timestamp'].min()}")
    print(f"End Time: {df['timestamp'].max()}")
    print(f"Duration: {duration}")
    print(f"Total Snapshots: {len(df)}")
    print()
    
    # Mac Studio 1 (GPT-OSS) Stats
    print("=" * 80)
    print("MAC STUDIO 1 (GPT-OSS) - FEEDBACK GENERATION")
    print("=" * 80)
    
    # Clean CPU percentages
    df['mac1_cpu_numeric'] = df['mac1_cpu_user'].str.rstrip('%').astype(float)
    
    print(f"CPU Usage (User):")
    print(f"  Average: {df['mac1_cpu_numeric'].mean():.1f}%")
    print(f"  Max: {df['mac1_cpu_numeric'].max():.1f}%")
    print(f"  Min: {df['mac1_cpu_numeric'].min():.1f}%")
    print()
    
    print(f"Tokens/Second:")
    print(f"  Average: {df['mac1_tokens_per_sec'].mean():.1f}")
    print(f"  Max: {df['mac1_tokens_per_sec'].max():.1f}")
    print(f"  Total Requests: {df['mac1_active_requests'].sum()}")
    print()
    
    uptime = (df['mac1_server_status'] == '✅').sum() / len(df) * 100
    print(f"Server Uptime: {uptime:.1f}%")
    print()
    
    # Mac Studio 2 (Qwen) Stats
    print("=" * 80)
    print("MAC STUDIO 2 (QWEN) - CODE ANALYSIS")
    print("=" * 80)
    
    # Clean CPU percentages
    df['mac2_cpu_numeric'] = df['mac2_cpu_user'].str.rstrip('%').astype(float)
    
    print(f"CPU Usage (User):")
    print(f"  Average: {df['mac2_cpu_numeric'].mean():.1f}%")
    print(f"  Max: {df['mac2_cpu_numeric'].max():.1f}%")
    print(f"  Min: {df['mac2_cpu_numeric'].min():.1f}%")
    print()
    
    print(f"Tokens/Second:")
    print(f"  Average: {df['mac2_tokens_per_sec'].mean():.1f}")
    print(f"  Max: {df['mac2_tokens_per_sec'].max():.1f}")
    print(f"  Total Requests: {df['mac2_active_requests'].sum()}")
    print()
    
    uptime = (df['mac2_server_status'] == '✅').sum() / len(df) * 100
    print(f"Server Uptime: {uptime:.1f}%")
    print()
    
    # Events
    if df['event'].notna().any():
        print("=" * 80)
        print("EVENTS")
        print("=" * 80)
        events = df[df['event'] != ''][['timestamp', 'event', 'notes']]
        for _, row in events.iterrows():
            print(f"[{row['timestamp']}] {row['event']}")
            if row['notes']:
                print(f"  Notes: {row['notes']}")
        print()
    
    # Performance Issues
    print("=" * 80)
    print("POTENTIAL ISSUES")
    print("=" * 80)
    
    # High CPU
    high_cpu_mac1 = df[df['mac1_cpu_numeric'] > 80]
    if not high_cpu_mac1.empty:
        print(f"⚠️ Mac 1 High CPU (>80%): {len(high_cpu_mac1)} snapshots")
    
    high_cpu_mac2 = df[df['mac2_cpu_numeric'] > 80]
    if not high_cpu_mac2.empty:
        print(f"⚠️ Mac 2 High CPU (>80%): {len(high_cpu_mac2)} snapshots")
    
    # Server downtime
    mac1_down = df[df['mac1_server_status'] == '❌']
    if not mac1_down.empty:
        print(f"❌ Mac 1 Server Down: {len(mac1_down)} snapshots")
        for _, row in mac1_down.iterrows():
            print(f"   {row['timestamp']}")
    
    mac2_down = df[df['mac2_server_status'] == '❌']
    if not mac2_down.empty:
        print(f"❌ Mac 2 Server Down: {len(mac2_down)} snapshots")
        for _, row in mac2_down.iterrows():
            print(f"   {row['timestamp']}")
    
    # Low performance
    low_perf_mac1 = df[(df['mac1_tokens_per_sec'] > 0) & (df['mac1_tokens_per_sec'] < 10)]
    if not low_perf_mac1.empty:
        print(f"🐌 Mac 1 Low Performance (<10 tok/s): {len(low_perf_mac1)} snapshots")
    
    low_perf_mac2 = df[(df['mac2_tokens_per_sec'] > 0) & (df['mac2_tokens_per_sec'] < 10)]
    if not low_perf_mac2.empty:
        print(f"🐌 Mac 2 Low Performance (<10 tok/s): {len(low_perf_mac2)} snapshots")
    
    if mac1_down.empty and mac2_down.empty and high_cpu_mac1.empty and high_cpu_mac2.empty:
        print("✅ No issues detected")
    
    print()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Analyze performance logs')
    parser.add_argument('log_file', nargs='?', help='Log file to analyze (default: latest)')
    parser.add_argument('--log-dir', type=str, default='performance_logs', help='Directory with log files')
    
    args = parser.parse_args()
    
    log_dir = Path(args.log_dir)
    
    if args.log_file:
        log_file = args.log_file
    else:
        # Find latest log file
        log_files = sorted(log_dir.glob('performance_log_*.csv'))
        if not log_files:
            print(f"❌ No log files found in {log_dir}")
            sys.exit(1)
        log_file = log_files[-1]
        print(f"📂 Using latest log: {log_file}\n")
    
    analyze_log(log_file)


if __name__ == '__main__':
    main()
