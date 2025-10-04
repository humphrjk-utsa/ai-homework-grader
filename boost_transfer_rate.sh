#!/bin/bash
# Aggressive network optimizations for maximum Thunderbolt speed

echo "🚀 Boosting Thunderbolt transfer rates to maximum..."

# 1. Massive TCP buffers (32MB)
sudo sysctl -w net.inet.tcp.sendspace=33554432
sudo sysctl -w net.inet.tcp.recvspace=33554432
sudo sysctl -w kern.ipc.maxsockbuf=67108864

# 2. Disable all latency optimizations for throughput
sudo sysctl -w net.inet.tcp.delayed_ack=0
sudo sysctl -w net.inet.tcp.nagle=0

# 3. Enable aggressive window scaling
sudo sysctl -w net.inet.tcp.rfc1323=1
sudo sysctl -w net.inet.tcp.rfc3390=1

# 4. Optimize for bulk transfers
sudo sysctl -w net.inet.tcp.slowstart_flightsize=10
sudo sysctl -w net.inet.tcp.local_slowstart_flightsize=10

# 5. Increase connection limits
sudo sysctl -w kern.ipc.somaxconn=1024

echo "✅ Applied aggressive TCP optimizations"
sysctl net.inet.tcp.sendspace net.inet.tcp.recvspace