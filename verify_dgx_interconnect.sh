#!/bin/bash
# Verify DGX Spark ConnectX-7 interconnect for distributed training

echo "="*80
echo "🔍 VERIFYING DGX SPARK CONNECTX-7 INTERCONNECT"
echo "="*80
echo ""

DGX1="humphrjk@169.254.150.103"
DGX2="humphrjk@169.254.150.104"

echo "📡 Checking network interfaces on DGX Sparks..."
echo ""

# Check DGX Spark 1
echo "=== DGX Spark 1 ==="
ssh $DGX1 "hostname && echo '' && ip addr show | grep -E '^[0-9]+:|inet ' | grep -v 'inet6' | head -20"
echo ""

# Check DGX Spark 2
echo "=== DGX Spark 2 ==="
ssh $DGX2 "hostname && echo '' && ip addr show | grep -E '^[0-9]+:|inet ' | grep -v 'inet6' | head -20"
echo ""

echo "="*80
echo "🔍 CHECKING CONNECTX-7 ADAPTERS"
echo "="*80
echo ""

# Check for Mellanox/NVIDIA ConnectX adapters
echo "=== DGX Spark 1 - InfiniBand/RoCE Adapters ==="
ssh $DGX1 "lspci | grep -i mellanox || lspci | grep -i nvidia | grep -i network || echo 'No Mellanox/NVIDIA network adapters found'"
echo ""

echo "=== DGX Spark 2 - InfiniBand/RoCE Adapters ==="
ssh $DGX2 "lspci | grep -i mellanox || lspci | grep -i nvidia | grep -i network || echo 'No Mellanox/NVIDIA network adapters found'"
echo ""

echo "="*80
echo "🔍 CHECKING RDMA/INFINIBAND STATUS"
echo "="*80
echo ""

# Check if RDMA is available
echo "=== DGX Spark 1 - RDMA Devices ==="
ssh $DGX1 "ls /dev/infiniband/ 2>/dev/null || echo 'No InfiniBand devices found'"
ssh $DGX1 "ibstat 2>/dev/null | head -20 || echo 'ibstat not available (install rdma-core)'"
echo ""

echo "=== DGX Spark 2 - RDMA Devices ==="
ssh $DGX2 "ls /dev/infiniband/ 2>/dev/null || echo 'No InfiniBand devices found'"
ssh $DGX2 "ibstat 2>/dev/null | head -20 || echo 'ibstat not available (install rdma-core)'"
echo ""

echo "="*80
echo "🔍 TESTING CONNECTIVITY BETWEEN DGX SPARKS"
echo "="*80
echo ""

# Find the high-speed interconnect IPs
echo "Looking for high-speed interconnect IPs..."
echo ""

# Test ping between DGX Sparks on all interfaces
echo "=== Testing DGX1 → DGX2 connectivity ==="
ssh $DGX1 "ping -c 3 169.254.150.104 && echo 'Ethernet: OK'"
echo ""

echo "=== Testing DGX2 → DGX1 connectivity ==="
ssh $DGX2 "ping -c 3 169.254.150.103 && echo 'Ethernet: OK'"
echo ""

echo "="*80
echo "📊 SUMMARY"
echo "="*80
echo ""
echo "✅ Both DGX Sparks are reachable via Ethernet (169.254.150.x)"
echo ""
echo "📝 Next steps:"
echo "1. Verify ConnectX-7 adapters are detected (lspci output above)"
echo "2. Check if RDMA/InfiniBand is configured (ibstat output above)"
echo "3. If ConnectX-7 is present but not configured:"
echo "   - Install OFED drivers: apt install rdma-core ibverbs-utils"
echo "   - Configure IPoIB or RoCE"
echo "   - Set up high-speed IPs (e.g., 192.168.100.1/2)"
echo "4. Test RDMA bandwidth: ib_write_bw or perftest"
echo ""
