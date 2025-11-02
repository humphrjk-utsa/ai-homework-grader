#!/usr/bin/env python3
"""
Real-Time Performance Monitor App
Live dashboard showing Mac Studio metrics with historical charts
"""

import streamlit as st
import pandas as pd
import subprocess
import requests
import time
from datetime import datetime, timedelta
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from pathlib import Path

# Page config
st.set_page_config(
    page_title="Mac Studio Monitor",
    page_icon="🖥️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for history
if 'history' not in st.session_state:
    st.session_state.history = []
if 'max_history' not in st.session_state:
    st.session_state.max_history = 60  # Keep last 60 data points

def get_mac_stats(user: str, ip: str, name: str) -> dict:
    """Get stats from a Mac Studio"""
    print(f"🔍 Getting stats from {name} ({ip})...")
    try:
        # Get CPU and Memory
        cmd = f"""ssh {user}@{ip} "top -l 1 | head -20" """
        print(f"  Running: {cmd[:80]}...")
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        print(f"  Result: returncode={result.returncode}, stdout length={len(result.stdout)}")
        
        stats = {
            'name': name,
            'ip': ip,
            'timestamp': datetime.now(),
            'cpu_user': 0.0,
            'cpu_system': 0.0,
            'cpu_idle': 100.0,
            'mem_used_gb': 0.0,
            'mem_free_gb': 0.0,
            'mem_total_gb': 0.0,
            'mem_percent': 0.0,
            'gpu_active_percent': 0.0,
            'power_watts': 0.0,
            'thermal_pressure': 'Unknown',
            'active_users': 0,
            'server_status': '❌',
            'tokens_per_sec': 0.0,
            'active_requests': 0
        }
        
        if result.returncode == 0:
            lines = result.stdout.split('\n')
            for line in lines:
                if 'CPU usage' in line:
                    parts = line.split()
                    if len(parts) >= 7:
                        stats['cpu_user'] = float(parts[2].rstrip('%'))
                        stats['cpu_system'] = float(parts[4].rstrip('%'))
                        stats['cpu_idle'] = float(parts[6].rstrip('%'))
                elif 'PhysMem' in line:
                    parts = line.split()
                    if len(parts) >= 6:
                        # Parse memory (e.g., "123G" -> 123.0, "3376K" -> 0.003376)
                        mem_used_str = parts[1]
                        mem_free_str = parts[5]
                        
                        # Convert to GB
                        def parse_memory(mem_str):
                            if mem_str.endswith('G'):
                                return float(mem_str.rstrip('G'))
                            elif mem_str.endswith('M'):
                                return float(mem_str.rstrip('M')) / 1024.0
                            elif mem_str.endswith('K'):
                                return float(mem_str.rstrip('K')) / (1024.0 * 1024.0)
                            else:
                                return 0.0
                        
                        stats['mem_used_gb'] = parse_memory(mem_used_str)
                        stats['mem_free_gb'] = parse_memory(mem_free_str)
                        stats['mem_total_gb'] = stats['mem_used_gb'] + stats['mem_free_gb']
                        if stats['mem_total_gb'] > 0:
                            stats['mem_percent'] = (stats['mem_used_gb'] / stats['mem_total_gb']) * 100
        
        # Get GPU and Power stats using powermetrics (single call for efficiency)
        # Skip for now if causing timeouts - can be enabled later
        try:
            power_cmd = f"""ssh {user}@{ip} "sudo powermetrics -i 200 -n 1 --samplers gpu_power,cpu_power,thermal 2>/dev/null | grep -E 'GPU Power|CPU Power|Combined Power|GPU HW active frequency|GPU HW active residency|GPU idle residency|pressure level'" """
            power_result = subprocess.run(power_cmd, shell=True, capture_output=True, text=True, timeout=10)
            
            if power_result.returncode == 0 and power_result.stdout:
                print(f"🔍 DEBUG {name} powermetrics output:")
                print(power_result.stdout)
                print("---")
                
                for line in power_result.stdout.split('\n'):
                    # Parse GPU HW active residency (the actual field name)
                    if 'GPU HW active residency' in line:
                        parts = line.split(':')
                        if len(parts) > 1:
                            try:
                                # Extract just the percentage (first value after colon)
                                gpu_val = parts[1].strip().split('%')[0].strip()
                                stats['gpu_active_percent'] = float(gpu_val)
                                print(f"✅ Parsed GPU: {gpu_val}% -> {stats['gpu_active_percent']}")
                            except Exception as e:
                                print(f"❌ Failed to parse GPU from: {line} - {e}")
                                pass
                    
                    # Also try GPU idle residency as fallback (100 - idle = active)
                    elif 'GPU idle residency' in line and stats['gpu_active_percent'] == 0.0:
                        parts = line.split(':')
                        if len(parts) > 1:
                            try:
                                idle_val = float(parts[1].strip().rstrip('%'))
                                stats['gpu_active_percent'] = 100.0 - idle_val
                                print(f"✅ Calculated GPU from idle: {idle_val}% idle -> {stats['gpu_active_percent']}% active")
                            except Exception as e:
                                print(f"❌ Failed to parse GPU idle from: {line} - {e}")
                                pass
                    
                    # Parse thermal pressure level
                    elif 'pressure level' in line.lower():
                        parts = line.split(':')
                        if len(parts) > 1:
                            pressure = parts[1].strip()
                            stats['thermal_pressure'] = pressure
                            print(f"✅ Thermal pressure: {pressure}")
                    
                    # Parse CPU Power (in mW)
                    elif 'CPU Power:' in line and 'mW' in line:
                        parts = line.split(':')
                        if len(parts) > 1:
                            try:
                                mw_str = parts[1].strip().split()[0]
                                stats['power_watts'] = float(mw_str) / 1000.0
                            except:
                                pass
                    
                    # Parse Combined Power (total system power)
                    elif 'Combined Power' in line and 'mW' in line:
                        parts = line.split(':')
                        if len(parts) > 1:
                            try:
                                mw_str = parts[1].strip().split()[0]
                                # Store combined power separately if you want
                                combined_watts = float(mw_str) / 1000.0
                                # Use combined power as the main power metric
                                stats['power_watts'] = combined_watts
                            except:
                                pass
            else:
                print(f"⚠️ Powermetrics returned no output for {name} (returncode: {power_result.returncode})")
                if power_result.stderr:
                    print(f"   stderr: {power_result.stderr}")
        except Exception as e:
            # Powermetrics can be slow, don't let it break the whole function
            print(f"⚠️ Powermetrics failed for {name}: {e}")
            import traceback
            traceback.print_exc()
            pass
        
        # Get active users count
        try:
            users_cmd = f"""ssh {user}@{ip} "who | wc -l" """
            users_result = subprocess.run(users_cmd, shell=True, capture_output=True, text=True, timeout=5)
            if users_result.returncode == 0:
                stats['active_users'] = int(users_result.stdout.strip())
        except:
            pass
        
        # Check server health
        port = '5001' if '0.1' in ip else '5002'
        try:
            response = requests.get(f"http://{ip}:{port}/health", timeout=3)
            if response.status_code == 200:
                stats['server_status'] = '✅'
                try:
                    data = response.json()
                    stats['tokens_per_sec'] = data.get('tokens_per_second', data.get('throughput', 0))
                    stats['active_requests'] = data.get('active_requests', data.get('requests', 0))
                    print(f"✅ {name} health: {data}")
                except:
                    # Health endpoint returned 200 but not JSON
                    pass
        except Exception as e:
            print(f"⚠️ Health check failed for {name}: {e}")
            pass
        
        return stats
        
    except Exception as e:
        print(f"⚠️ Error getting stats from {name}: {e}")
        import traceback
        traceback.print_exc()
        return {
            'name': name,
            'ip': ip,
            'timestamp': datetime.now(),
            'cpu_user': 0.0,
            'cpu_system': 0.0,
            'cpu_idle': 0.0,
            'mem_used_gb': 0.0,
            'mem_free_gb': 0.0,
            'mem_total_gb': 0.0,
            'mem_percent': 0.0,
            'gpu_active_percent': 0.0,
            'power_watts': 0.0,
            'active_users': 0,
            'server_status': '❌',
            'tokens_per_sec': 0.0,
            'active_requests': 0,
            'error': str(e)
        }

def create_cpu_chart(history_df, mac_name):
    """Create CPU usage chart"""
    fig = go.Figure()
    
    mac_data = history_df[history_df['name'] == mac_name]
    
    fig.add_trace(go.Scatter(
        x=mac_data['timestamp'],
        y=mac_data['cpu_user'],
        name='User',
        mode='lines',
        line=dict(color='#FF6B6B', width=2),
        fill='tozeroy'
    ))
    
    fig.add_trace(go.Scatter(
        x=mac_data['timestamp'],
        y=mac_data['cpu_system'],
        name='System',
        mode='lines',
        line=dict(color='#4ECDC4', width=2)
    ))
    
    fig.update_layout(
        title=f"{mac_name} - CPU Usage",
        xaxis_title="Time",
        yaxis_title="CPU %",
        height=250,
        margin=dict(l=0, r=0, t=30, b=0),
        showlegend=True,
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
    )
    
    return fig

def create_tokens_chart(history_df, mac_name):
    """Create tokens/sec chart"""
    fig = go.Figure()
    
    mac_data = history_df[history_df['name'] == mac_name]
    
    fig.add_trace(go.Scatter(
        x=mac_data['timestamp'],
        y=mac_data['tokens_per_sec'],
        name='Tokens/sec',
        mode='lines+markers',
        line=dict(color='#95E1D3', width=2),
        marker=dict(size=6)
    ))
    
    fig.update_layout(
        title=f"{mac_name} - Throughput",
        xaxis_title="Time",
        yaxis_title="Tokens/sec",
        height=250,
        margin=dict(l=0, r=0, t=30, b=0)
    )
    
    return fig

def create_memory_chart(history_df, mac_name):
    """Create memory usage chart"""
    fig = go.Figure()
    
    mac_data = history_df[history_df['name'] == mac_name]
    
    fig.add_trace(go.Scatter(
        x=mac_data['timestamp'],
        y=mac_data['mem_percent'],
        name='Memory %',
        mode='lines',
        line=dict(color='#F38181', width=2),
        fill='tozeroy'
    ))
    
    fig.update_layout(
        title=f"{mac_name} - Memory Usage",
        xaxis_title="Time",
        yaxis_title="Memory %",
        height=250,
        margin=dict(l=0, r=0, t=30, b=0),
        yaxis=dict(range=[0, 100])
    )
    
    return fig

def create_gpu_chart(history_df, mac_name):
    """Create GPU usage chart"""
    fig = go.Figure()
    
    mac_data = history_df[history_df['name'] == mac_name]
    
    fig.add_trace(go.Scatter(
        x=mac_data['timestamp'],
        y=mac_data['gpu_active_percent'],
        name='GPU Active %',
        mode='lines',
        line=dict(color='#AA96DA', width=2),
        fill='tozeroy'
    ))
    
    fig.update_layout(
        title=f"{mac_name} - GPU Activity",
        xaxis_title="Time",
        yaxis_title="GPU %",
        height=250,
        margin=dict(l=0, r=0, t=30, b=0),
        yaxis=dict(range=[0, 100])
    )
    
    return fig

def create_power_chart(history_df, mac_name):
    """Create power consumption chart"""
    fig = go.Figure()
    
    mac_data = history_df[history_df['name'] == mac_name]
    
    fig.add_trace(go.Scatter(
        x=mac_data['timestamp'],
        y=mac_data['power_watts'],
        name='Power (W)',
        mode='lines',
        line=dict(color='#FCBAD3', width=2),
        fill='tozeroy'
    ))
    
    fig.update_layout(
        title=f"{mac_name} - Power Consumption",
        xaxis_title="Time",
        yaxis_title="Watts",
        height=250,
        margin=dict(l=0, r=0, t=30, b=0)
    )
    
    return fig

def main():
    st.title("🖥️ Mac Studio Performance Monitor")
    st.caption("Real-time monitoring of distributed AI grading system")
    
    # Sidebar controls
    with st.sidebar:
        st.header("⚙️ Settings")
        
        refresh_rate = st.slider("Refresh Rate (seconds)", 1, 10, 3)
        
        # Disable auto-refresh option
        auto_refresh = st.checkbox("Auto-refresh", value=True)
        
        st.markdown("---")
        
        if st.button("🔄 Manual Refresh"):
            st.rerun()
        
        if st.button("🗑️ Clear History"):
            st.session_state.history = []
            st.rerun()
        
        st.markdown("---")
        st.subheader("📊 History")
        st.metric("Data Points", len(st.session_state.history))
        
        if st.session_state.history:
            oldest = st.session_state.history[0]['timestamp']
            duration = datetime.now() - oldest
            st.metric("Duration", f"{duration.seconds}s")
    
    # Get current stats
    mac1_stats = get_mac_stats("humphrjk", "10.55.0.1", "Mac Studio 1 (GPT-OSS)")
    mac2_stats = get_mac_stats("jamiehumphries", "10.55.0.2", "Mac Studio 2 (Qwen)")
    
    # Fix memory percentage based on actual total RAM
    # Mac 1: 512GB, Mac 2: 128GB
    mac1_stats['mem_total_gb'] = 512.0
    mac1_stats['mem_percent'] = (mac1_stats['mem_used_gb'] / 512.0) * 100
    
    mac2_stats['mem_total_gb'] = 128.0
    mac2_stats['mem_percent'] = (mac2_stats['mem_used_gb'] / 128.0) * 100
    
    # Add to history
    st.session_state.history.append(mac1_stats)
    st.session_state.history.append(mac2_stats)
    
    # Trim history
    if len(st.session_state.history) > st.session_state.max_history * 2:
        st.session_state.history = st.session_state.history[-st.session_state.max_history * 2:]
    
    # Convert to DataFrame
    history_df = pd.DataFrame(st.session_state.history)
    
    # Current Status Cards
    st.subheader("📡 Current Status")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"### {mac1_stats['server_status']} Mac Studio 1 (GPT-OSS)")
        st.caption(f"IP: {mac1_stats['ip']} | Active Users: {mac1_stats['active_users']}")
        
        metric_col1, metric_col2, metric_col3, metric_col4, metric_col5 = st.columns(5)
        with metric_col1:
            st.metric("CPU User", f"{mac1_stats['cpu_user']:.1f}%")
        with metric_col2:
            st.metric("Memory", f"{mac1_stats['mem_used_gb']:.0f}G / 512G", f"{mac1_stats['mem_percent']:.1f}%")
        with metric_col3:
            st.metric("GPU", f"{mac1_stats['gpu_active_percent']:.1f}%")
        with metric_col4:
            st.metric("Power", f"{mac1_stats['power_watts']:.1f}W")
        with metric_col5:
            # Thermal pressure with emoji indicator
            thermal_emoji = "🟢" if mac1_stats['thermal_pressure'] == "Nominal" else "🟡" if mac1_stats['thermal_pressure'] == "Moderate" else "🔴"
            st.metric("Thermal", f"{thermal_emoji} {mac1_stats['thermal_pressure']}")
        
        # Charts in tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["CPU", "Memory", "GPU", "Power", "Throughput"])
        
        if len(history_df[history_df['name'] == mac1_stats['name']]) > 1:
            with tab1:
                st.plotly_chart(create_cpu_chart(history_df, mac1_stats['name']), use_container_width=True)
            with tab2:
                st.plotly_chart(create_memory_chart(history_df, mac1_stats['name']), use_container_width=True)
            with tab3:
                st.plotly_chart(create_gpu_chart(history_df, mac1_stats['name']), use_container_width=True)
            with tab4:
                st.plotly_chart(create_power_chart(history_df, mac1_stats['name']), use_container_width=True)
            with tab5:
                st.plotly_chart(create_tokens_chart(history_df, mac1_stats['name']), use_container_width=True)
    
    with col2:
        st.markdown(f"### {mac2_stats['server_status']} Mac Studio 2 (Qwen)")
        st.caption(f"IP: {mac2_stats['ip']} | Active Users: {mac2_stats['active_users']}")
        
        metric_col1, metric_col2, metric_col3, metric_col4, metric_col5 = st.columns(5)
        with metric_col1:
            st.metric("CPU User", f"{mac2_stats['cpu_user']:.1f}%")
        with metric_col2:
            st.metric("Memory", f"{mac2_stats['mem_used_gb']:.0f}G / 128G", f"{mac2_stats['mem_percent']:.1f}%")
        with metric_col3:
            st.metric("GPU", f"{mac2_stats['gpu_active_percent']:.1f}%")
        with metric_col4:
            st.metric("Power", f"{mac2_stats['power_watts']:.1f}W")
        with metric_col5:
            # Thermal pressure with emoji indicator
            thermal_emoji = "🟢" if mac2_stats['thermal_pressure'] == "Nominal" else "🟡" if mac2_stats['thermal_pressure'] == "Moderate" else "🔴"
            st.metric("Thermal", f"{thermal_emoji} {mac2_stats['thermal_pressure']}")
        
        # Charts in tabs
        tab1, tab2, tab3, tab4, tab5 = st.tabs(["CPU", "Memory", "GPU", "Power", "Throughput"])
        
        if len(history_df[history_df['name'] == mac2_stats['name']]) > 1:
            with tab1:
                st.plotly_chart(create_cpu_chart(history_df, mac2_stats['name']), use_container_width=True)
            with tab2:
                st.plotly_chart(create_memory_chart(history_df, mac2_stats['name']), use_container_width=True)
            with tab3:
                st.plotly_chart(create_gpu_chart(history_df, mac2_stats['name']), use_container_width=True)
            with tab4:
                st.plotly_chart(create_power_chart(history_df, mac2_stats['name']), use_container_width=True)
            with tab5:
                st.plotly_chart(create_tokens_chart(history_df, mac2_stats['name']), use_container_width=True)
    
    # System Health
    st.markdown("---")
    st.subheader("🏥 System Health")
    
    health_col1, health_col2, health_col3, health_col4 = st.columns(4)
    
    with health_col1:
        both_online = mac1_stats['server_status'] == '✅' and mac2_stats['server_status'] == '✅'
        st.metric(
            "System Status",
            "🟢 Online" if both_online else "🔴 Degraded",
            delta="Both servers" if both_online else "Check servers"
        )
    
    with health_col2:
        total_throughput = mac1_stats['tokens_per_sec'] + mac2_stats['tokens_per_sec']
        st.metric("Combined Throughput", f"{total_throughput:.1f} tok/s")
    
    with health_col3:
        avg_cpu = (mac1_stats['cpu_user'] + mac2_stats['cpu_user']) / 2
        st.metric("Avg CPU Usage", f"{avg_cpu:.1f}%")
    
    with health_col4:
        total_requests = mac1_stats['active_requests'] + mac2_stats['active_requests']
        st.metric("Active Requests", total_requests)
    
    # Auto-refresh only if enabled
    if auto_refresh:
        time.sleep(refresh_rate)
        st.rerun()

if __name__ == '__main__':
    main()
