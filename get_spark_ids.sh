#!/bin/bash
# Get Spark ID information from connected DGX systems

echo "🔍 Getting Spark ID Information..."
echo ""

echo "=== DGX Spark 3 (169.254.150.105) ==="
ssh jamiehumphries@169.254.150.105 "hostname && echo 'Machine ID:' && cat /etc/machine-id && echo 'GPU UUID:' && nvidia-smi -L"
echo ""

echo "=== DGX Spark 4 (169.254.150.106) ==="
ssh jamiehumphries@169.254.150.106 "hostname && echo 'Machine ID:' && cat /etc/machine-id && echo 'GPU UUID:' && nvidia-smi -L"
echo ""
