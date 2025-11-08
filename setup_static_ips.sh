#!/bin/bash
# Set static IPs on Mac Studios for DGX Spark connectivity

echo "="*80
echo "🌐 SETTING STATIC IPS FOR DGX SPARK NETWORK"
echo "="*80
echo ""
echo "Network Plan:"
echo "  Mac Studio 1 (en0): 169.254.150.101/16"
echo "  Mac Studio 2 (en0): 169.254.150.102/16"
echo "  DGX Spark 1: 169.254.150.1/16 (to be configured)"
echo "  DGX Spark 2: 169.254.150.2/16 (to be configured)"
echo ""

read -p "Continue? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Cancelled"
    exit 0
fi

echo ""
echo "📝 Configuring Mac Studio 1 (this machine)..."
echo ""

# Mac Studio 1 - Configure en0
INTERFACE="en0"
IP="169.254.150.101"
SUBNET="255.255.0.0"

echo "Setting $INTERFACE to $IP/$SUBNET..."

# Remove existing IP if any
sudo ifconfig $INTERFACE inet $IP netmask $SUBNET

if [ $? -eq 0 ]; then
    echo "✅ Mac Studio 1 configured: $IP"
else
    echo "❌ Failed to configure Mac Studio 1"
    exit 1
fi

# Verify
CURRENT_IP=$(ifconfig $INTERFACE | grep "inet " | awk '{print $2}')
echo "   Current IP: $CURRENT_IP"

echo ""
echo "📝 Configuring Mac Studio 2..."
echo ""

# Mac Studio 2 - Configure en0 remotely
MAC2_HOST="humphrjk@10.55.0.2"
MAC2_INTERFACE="en0"
MAC2_IP="169.254.150.102"

ssh $MAC2_HOST "sudo ifconfig $MAC2_INTERFACE inet $MAC2_IP netmask $SUBNET"

if [ $? -eq 0 ]; then
    echo "✅ Mac Studio 2 configured: $MAC2_IP"
else
    echo "❌ Failed to configure Mac Studio 2"
    exit 1
fi

# Verify
MAC2_CURRENT=$(ssh $MAC2_HOST "ifconfig $MAC2_INTERFACE | grep 'inet ' | awk '{print \$2}'")
echo "   Current IP: $MAC2_CURRENT"

echo ""
echo "="*80
echo "✅ STATIC IPS CONFIGURED"
echo "="*80
echo ""
echo "📊 Network Status:"
echo "  Mac Studio 1: $CURRENT_IP"
echo "  Mac Studio 2: $MAC2_CURRENT"
echo ""
echo "🔍 Testing connectivity..."
ping -c 2 $MAC2_IP

if [ $? -eq 0 ]; then
    echo "✅ Mac Studios can communicate!"
else
    echo "⚠️  Warning: Cannot ping Mac Studio 2"
fi

echo ""
echo "📝 Next steps:"
echo "1. Configure DGX Spark 1: 169.254.150.1/16"
echo "2. Configure DGX Spark 2: 169.254.150.2/16"
echo "3. Test connectivity: ping 169.254.150.1"
echo "4. Distribute models: ./distribute_fp4_models.sh"
echo ""
echo "⚠️  Note: These IPs are temporary and will reset on reboot"
echo "   To make permanent, configure in System Settings > Network"
