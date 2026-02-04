#!/bin/bash
# Script to shut down all Ollama servers on all machines

echo "🛑 Shutting down all Ollama servers..."
echo ""

# DGX Spark 3 (169.254.150.105)
echo "📡 DGX Spark 3 (169.254.150.105)"
ssh jamiehumphries@169.254.150.105 "pkill -f ollama && pkill -f prefill_server" 2>/dev/null
echo "   ✅ Stopped"

# DGX Spark 4 (169.254.150.106)
echo "📡 DGX Spark 4 (169.254.150.106)"
ssh jamiehumphries@169.254.150.106 "pkill -f ollama && pkill -f prefill_server" 2>/dev/null
echo "   ✅ Stopped"

# Mac Studio 2 (169.254.150.102)
echo "📡 Mac Studio 2 (169.254.150.102)"
ssh jamiehumphries@169.254.150.102 "pkill -f ollama && pkill -f decode_server" 2>/dev/null
echo "   ✅ Stopped"

# Local Mac Studio 1 (169.254.150.101 / localhost)
echo "📡 Mac Studio 1 (Local)"
pkill -f ollama 2>/dev/null
pkill -f decode_server 2>/dev/null
echo "   ✅ Stopped"

echo ""
echo "✅ All Ollama servers shut down"
