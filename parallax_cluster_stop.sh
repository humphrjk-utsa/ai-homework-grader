#!/bin/bash
# Parallax Cluster Shutdown Script
# Cleanly stops all nodes in the cluster
# NOTE: Kills both parallax processes AND orphaned multiprocessing children
#       that retain libp2p/mDNS state and cause ghost node issues.

echo "=============================================="
echo "Stopping Parallax Cluster"
echo "=============================================="

# Stop Mac 1 (Scheduler) - localhost
echo ""
echo "[1/4] Stopping Mac 1 (Scheduler - localhost)..."
pkill -f "parallax" 2>/dev/null && echo "  ✓ Parallax processes stopped" || echo "  - No parallax processes"
# Kill orphaned multiprocessing children (spawned by parallax workers)
pkill -f "multiprocessing.spawn" 2>/dev/null && echo "  ✓ Orphaned multiprocessing children killed" || echo "  - No orphaned children"

# Stop Mac 2 (Worker)
echo ""
echo "[2/4] Stopping Mac 2 (Worker - 169.254.150.102)..."
ssh humphrjk@169.254.150.102 "pkill -f 'parallax' 2>/dev/null; pkill -f 'multiprocessing.spawn' 2>/dev/null; pkill -f 'multiprocessing.resource_tracker' 2>/dev/null" && echo "  ✓ All parallax processes stopped" || echo "  - No processes running"

# Stop spark-2935 Docker container
echo ""
echo "[3/4] Stopping spark-2935 (169.254.150.106)..."
ssh humphrjk@169.254.150.106 "sudo docker stop \$(sudo docker ps -q) 2>/dev/null; sudo docker rm \$(sudo docker ps -aq) 2>/dev/null" && echo "  ✓ Docker containers stopped" || echo "  - No containers running"

# Stop RR191562IP01 Docker container
echo ""
echo "[4/4] Stopping RR191562IP01 (169.254.150.105)..."
ssh humphrjk@169.254.150.105 "sudo docker stop \$(sudo docker ps -q) 2>/dev/null; sudo docker rm \$(sudo docker ps -aq) 2>/dev/null" && echo "  ✓ Docker containers stopped" || echo "  - No containers running"

# Brief wait for libp2p/mDNS records to expire
sleep 3

echo ""
echo "=============================================="
echo "Parallax Cluster Stopped"
echo "=============================================="
