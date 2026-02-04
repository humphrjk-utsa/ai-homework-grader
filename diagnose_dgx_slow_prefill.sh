#!/bin/bash
# Diagnostic script for slow DGX prefill performance
# Run this ON the DGX Spark 4 machine (169.254.150.106)

echo "======================================================================="
echo "  DGX Spark 4 - Prefill Performance Diagnostics"
echo "======================================================================="
echo ""

echo "1. GPU Status and Utilization"
echo "-----------------------------"
nvidia-smi
echo ""

echo "2. GPU Processes (what's using the GPU?)"
echo "----------------------------------------"
nvidia-smi pquery
echo ""

echo "3. Check for Ollama or competing services"
echo "-----------------------------------------"
ps aux | grep -E 'ollama|llama-server|python.*model' | grep -v grep
echo ""

echo "4. Check systemd services that might use GPU"
echo "--------------------------------------------"
systemctl list-units | grep -E 'ollama|llama|gpu'
echo ""

echo "5. GPU Memory Usage"
echo "------------------"
nvidia-smi --query-gpu=memory.used,memory.free,memory.total --format=csv
echo ""

echo "6. GPU Temperature and Power"
echo "---------------------------"
nvidia-smi --query-gpu=temperature.gpu,power.draw,power.limit --format=csv
echo ""

echo "7. Check which GPU the prefill server is using"
echo "----------------------------------------------"
echo "CUDA_VISIBLE_DEVICES from prefill server process:"
ps aux | grep -E 'llama-server.*prefill|python.*prefill' | grep -v grep
echo ""

echo "======================================================================="
echo "  Common Issues and Fixes:"
echo "======================================================================="
echo ""
echo "❌ If Ollama is running:"
echo "   → sudo systemctl stop ollama"
echo ""
echo "❌ If GPU memory is full:"
echo "   → Restart the prefill server to clear state"
echo ""
echo "❌ If temperature is >85°C:"
echo "   → GPU is thermal throttling - improve cooling or reduce load"
echo ""
echo "❌ If wrong GPU is being used:"
echo "   → Set CUDA_VISIBLE_DEVICES=0 (or appropriate GPU ID)"
echo ""
echo "✅ After fixing, restart prefill server and retest"
echo ""
