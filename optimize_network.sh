#!/bin/bash
# Optimize network settings for high-speed Thunderbolt connections
echo "🚀 Optimizing TCP/IP for high-speed local connections..."

# Increase TCP buffer sizes for high-speed transfers
sudo sysctl -w net.inet.tcp.sendspace=2097152    # 2MB send buffer
sudo sysctl -w net.inet.tcp.recvspace=2097152    # 2MB receive buffer
sudo sysctl -w net.inet.tcp.win_scale_factor=8   # Enable window scaling
sudo sysctl -w net.inet.tcp.rfc1323=1            # Enable window scaling and timestamps

# Optimize for low latency local connections
sudo sysctl -w net.inet.tcp.delayed_ack=0        # Disable delayed ACK for low latency
sudo sysctl -w net.inet.tcp.nagle=0              # Disable Nagle algorithm for low latency

echo "✅ TCP optimizations applied"
echo "📊 Current settings:"
sysctl net.inet.tcp.sendspace net.inet.tcp.recvspace

# Create unencrypted transfer function
echo "🔧 Setting up unencrypted high-speed transfers..."