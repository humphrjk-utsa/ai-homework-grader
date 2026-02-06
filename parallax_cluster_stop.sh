#!/bin/bash
# Parallax Cluster Shutdown Script
# Cleanly stops all nodes in the cluster

echo "=============================================="
echo "Stopping Parallax Cluster"
echo "=============================================="

# Stop Mac 1 (Scheduler) - localhost
echo ""
echo "[1/4] Stopping Mac 1 (Scheduler - localhost)..."
pkill -f "parallax" 2>/dev/null && echo "  ✓ Parallax processes stopped" || echo "  - No processes running"

# Stop Mac 2 (Worker)
echo ""
echo "[2/4] Stopping Mac 2 (Worker - 169.254.150.102)..."
ssh humphrjk@169.254.150.102 "pkill -f 'parallax'" 2>/dev/null && echo "  ✓ Parallax processes stopped" || echo "  - No processes running"

# Stop spark-2935 Docker container
echo ""
echo "[3/4] Stopping spark-2935 (169.254.150.106)..."
ssh humphrjk@169.254.150.106 "sudo docker stop \$(sudo docker ps -q --filter ancestor=gradientservice/parallax:latest-spark) 2>/dev/null" && echo "  ✓ Docker container stopped" || echo "  - No container running"

# Stop RR191562IP01 Docker container
echo ""
echo "[4/4] Stopping RR191562IP01 (169.254.150.105)..."
ssh humphrjk@169.254.150.105 "sudo docker stop \$(sudo docker ps -q --filter ancestor=gradientservice/parallax:latest-spark) 2>/dev/null" && echo "  ✓ Docker container stopped" || echo "  - No container running"

echo ""
echo "=============================================="
echo "Parallax Cluster Stopped"
echo "=============================================="
