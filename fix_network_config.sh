#!/bin/bash
# Fix Mac Studio 1 Ethernet to use static IP for 10Gb switch

echo "🔧 Configuring Mac Studio 1 Ethernet for 10Gb switch"
echo "=================================================="
echo ""
echo "Current Ethernet config:"
networksetup -getinfo "Ethernet"
echo ""
echo "Setting static IP: 169.254.150.101"
echo "Subnet mask: 255.255.255.0"
echo ""

# Set static IP on Ethernet interface
sudo networksetup -setmanual "Ethernet" 169.254.150.101 255.255.255.0

echo ""
echo "✅ Network configured!"
echo ""
echo "New Ethernet config:"
networksetup -getinfo "Ethernet"
echo ""
echo "Testing connectivity to DGX Sparks..."
echo ""

# Test connectivity
echo -n "DGX Spark 1 (169.254.150.103): "
if ping -c 1 -W 2 169.254.150.103 > /dev/null 2>&1; then
    echo "✅ Reachable"
else
    echo "❌ Not reachable"
fi

echo -n "DGX Spark 2 (169.254.150.104): "
if ping -c 1 -W 2 169.254.150.104 > /dev/null 2>&1; then
    echo "✅ Reachable"
else
    echo "❌ Not reachable"
fi

echo -n "Mac Studio 2 (169.254.150.102): "
if ping -c 1 -W 2 169.254.150.102 > /dev/null 2>&1; then
    echo "✅ Reachable"
else
    echo "❌ Not reachable"
fi

echo ""
echo "If DGX Sparks are still not reachable, check:"
echo "1. DGX Sparks have static IPs configured (169.254.150.103, 169.254.150.104)"
echo "2. All machines are connected to the same 10Gb switch"
echo "3. Ethernet cables are properly connected"
