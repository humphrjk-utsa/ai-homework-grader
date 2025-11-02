#!/bin/bash
# Verify 8-bit Qwen model is configured and running

echo "🔍 Verifying 8-bit Qwen Setup..."
echo ""

# Check config files
echo "📋 Checking configuration files..."
if grep -q "Qwen3-Coder-30B-A3B-Instruct-8bit" models/two_model_config.py; then
    echo "  ✅ models/two_model_config.py - Updated to 8-bit"
else
    echo "  ❌ models/two_model_config.py - Still using bf16"
fi

if grep -q "Qwen3-Coder-30B-A3B-Instruct-8bit" model_status_display.py; then
    echo "  ✅ model_status_display.py - Updated to 8-bit"
else
    echo "  ❌ model_status_display.py - Still using bf16"
fi

echo ""
echo "🖥️  Checking Mac 2 server..."
if curl -s http://10.55.0.2:5002/health | grep -q "ok"; then
    echo "  ✅ Server is running on Mac 2"
    
    # Test actual generation
    echo ""
    echo "🧪 Testing model generation..."
    response=$(curl -s -X POST http://10.55.0.2:5002/v1/chat/completions \
      -H "Content-Type: application/json" \
      -d '{"messages": [{"role": "user", "content": "Say hello"}], "max_tokens": 10}')
    
    if echo "$response" | grep -q "choices"; then
        echo "  ✅ Model is generating responses"
    else
        echo "  ❌ Model generation failed"
    fi
else
    echo "  ❌ Server is not responding"
    echo "  💡 Run: ./start_qwen_8bit_mac2.sh"
fi

echo ""
echo "📊 Memory usage on Mac 2:"
ssh jamiehumphries@10.55.0.2 "top -l 1 | grep PhysMem"

echo ""
echo "✅ Verification complete!"
