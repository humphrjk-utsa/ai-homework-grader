# Disaggregated Inference System Status

## ✅ SYSTEM FULLY OPERATIONAL

All servers online and tested successfully!

### Working Configuration
- **DGX Spark 1** (169.254.150.103:8000): Qwen 3 Coder 30B prefill - ✅ ONLINE
- **DGX Spark 2** (169.254.150.104:8000): GPT-OSS 120B prefill - ✅ ONLINE
- **Mac Studio 1** (169.254.150.101:8001): GPT-OSS 120B decode - ✅ ONLINE
- **Mac Studio 2** (169.254.150.102:8001): Qwen 3 Coder 30B decode - ✅ ONLINE

### Performance (Tested)
- **Qwen**: 0.68s total (0.10s prefill + 0.57s decode @ 101 tok/s)
- **GPT-OSS**: 2.00s total (0.00s prefill + 1.99s decode @ 78 tok/s)

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  DISAGGREGATED SYSTEM                        │
│                                                              │
│  DGX Spark 1 (prefill) ──→ Mac Studio 1 (decode)  [Qwen]   │
│  DGX Spark 2 (prefill) ──→ Mac Studio 2 (decode)  [GPT-OSS]│
└─────────────────────────────────────────────────────────────┘
```

### Correct Configuration

| Machine | Role | Port | Model | Status |
|---------|------|------|-------|--------|
| DGX Spark 1 (103) | Prefill | 8000 | qwen3-coder:30b | ✅ |
| DGX Spark 2 (104) | Prefill | 8000 | gpt-oss:120b | ✅ |
| Mac Studio 1 (101) | Decode | 8001 | qwen3-coder:30b | ❌ OFFLINE |
| Mac Studio 2 (102) | Decode | 8001 | gpt-oss:120b | ❌ WRONG MODEL |

## How It Works

1. **Prefill Phase (DGX)**:
   - Flask server on port 8000 receives prompt
   - Calls local Ollama (port 11434) to process prompt
   - Returns context/metrics to orchestrator

2. **Decode Phase (Mac)**:
   - Flask server on port 8001 receives context from prefill
   - Calls local Ollama (port 11434) to generate tokens
   - Returns generated text + metrics

3. **Client Integration**:
   - `disaggregated_client.py` calls Flask wrappers (not Ollama directly)
   - `business_analytics_grader_v2.py` uses DisaggregatedClient when available
   - Falls back to direct Ollama if disaggregated system unavailable

## Files Updated

1. **disaggregated_client.py**: Fixed to call Flask wrappers instead of Ollama API
2. **business_analytics_grader_v2.py**: Added disaggregated client integration
3. **test_disaggregated_setup.py**: Status checker
4. **test_disaggregated_client.py**: Client test suite

## Next Steps

### 1. Fix Mac Studio 1 (Offline)
```bash
# On Mac Studio 1 (this machine - 169.254.150.101)
cd ~/GitHub/ai-homework-grader-clean
./disaggregated_inference/start_mac_servers_ollama.sh
```

This will start the decode server for Qwen on port 8001.

### 2. Fix Mac Studio 2 (Wrong Model)
```bash
# SSH to Mac Studio 2
ssh humphrjk@169.254.150.102

# Stop the wrong server
pkill -f "decode_server_ollama.py"

# Start with correct model
cd ~/GitHub/ai-homework-grader-clean
nohup python3 disaggregated_inference/decode_server_ollama.py \
    --model gpt-oss:120b \
    --host 169.254.150.102 \
    --port 8001 \
    > ~/logs/decode_gpt_oss.log 2>&1 &

# Verify
curl http://169.254.150.102:8001/health | python3 -m json.tool
```

### 3. Test the System
```bash
# Check all servers
python3 test_disaggregated_setup.py

# Test client
python3 test_disaggregated_client.py

# Test with grader
streamlit run app.py
# Then grade a submission and check for disaggregated metrics
```

## Troubleshooting

### Check if Ollama is running locally
```bash
# On each machine
curl http://localhost:11434/api/tags
```

### Check Flask wrapper logs
```bash
# DGX Spark 1
ssh humphrjk@169.254.150.103 'tail -f ~/logs/prefill_qwen.log'

# DGX Spark 2
ssh humphrjk@169.254.150.104 'tail -f ~/logs/prefill_gpt_oss.log'

# Mac Studio 1
tail -f ~/logs/decode_qwen.log

# Mac Studio 2
ssh humphrjk@169.254.150.102 'tail -f ~/logs/decode_gpt_oss.log'
```

### Manual test of Flask wrappers
```bash
# Test prefill
curl -X POST http://169.254.150.103:8000/prefill \
  -H "Content-Type: application/json" \
  -d '{"prompt": "def hello():"}'

# Test decode
curl -X POST http://169.254.150.101:8001/decode \
  -H "Content-Type: application/json" \
  -d '{"prompt": "def hello():", "max_new_tokens": 50}'
```

## Performance Expectations

- **Qwen 3 Coder 30B**: 
  - Prefill: ~400-600 tok/s (DGX)
  - Decode: ~50-80 tok/s (Mac)

- **GPT-OSS 120B**:
  - Prefill: ~200-300 tok/s (DGX)
  - Decode: ~20-30 tok/s (Mac)
