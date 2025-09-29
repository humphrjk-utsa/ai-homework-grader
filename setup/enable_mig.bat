@echo off
echo 🚀 Enabling MIG on RTX Pro 6000...
echo.

echo 📋 Current GPU Status:
nvidia-smi --query-gpu=name,mig.mode.current --format=csv
echo.

echo 🔧 Enabling MIG mode...
nvidia-smi -i 0 -mig 1

echo.
echo 📋 New MIG Status:
nvidia-smi --query-gpu=name,mig.mode.current,mig.mode.pending --format=csv

echo.
echo ⚠️ IMPORTANT: You need to REBOOT for MIG to take effect!
echo After reboot, run: python setup_mig.py
echo.
pause