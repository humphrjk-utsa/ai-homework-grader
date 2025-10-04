# Enable MIG on RTX Pro 6000
Write-Host "🚀 Enabling MIG on RTX Pro 6000..." -ForegroundColor Green
Write-Host ""

Write-Host "📋 Current GPU Status:" -ForegroundColor Yellow
nvidia-smi --query-gpu=name,mig.mode.current --format=csv
Write-Host ""

Write-Host "🔧 Enabling MIG mode..." -ForegroundColor Yellow
$result = nvidia-smi -i 0 -mig 1

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ MIG enable command succeeded!" -ForegroundColor Green
} else {
    Write-Host "❌ MIG enable failed!" -ForegroundColor Red
    Write-Host "Error: $result" -ForegroundColor Red
}

Write-Host ""
Write-Host "📋 New MIG Status:" -ForegroundColor Yellow
nvidia-smi --query-gpu=name,mig.mode.current,mig.mode.pending --format=csv

Write-Host ""
Write-Host "⚠️ IMPORTANT: You need to REBOOT for MIG to take effect!" -ForegroundColor Red
Write-Host "After reboot, run: python setup_mig.py" -ForegroundColor Cyan
Write-Host ""

Read-Host "Press Enter to continue"