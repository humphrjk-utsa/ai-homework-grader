# Swap Models Between Mac Studios

## New Configuration

**Mac Studio 1** (10.55.0.1:5001):
- Model: `mlx-community/gemma-3-27b-it-bf16`
- Purpose: Feedback Generation
- Max Tokens: 3800 (for verbose feedback)
- Temperature: 0.3

**Mac Studio 2** (10.55.0.2:5002):
- Model: `mlx-community/Qwen3-Coder-30B-A3B-Instruct-bf16`
- Purpose: Code Analysis
- Max Tokens: 2400
- Temperature: 0.1

## Steps to Apply Changes

### 1. Stop Current Servers

**On Mac Studio 1:**
```bash
ssh user@10.55.0.1
pkill -f "gemma_server.py\|qwen_server.py"
```

**On Mac Studio 2:**
```bash
ssh user@10.55.0.2
pkill -f "gemma_server.py\|qwen_server.py"
```

### 2. Update Configuration Files

The configuration files have been updated. Copy them to each Mac:

**Copy to Mac Studio 1:**
```bash
scp mac_studio_deployment/mac_studio_1/distributed_config.json user@10.55.0.1:~/homework-grader/
```

**Copy to Mac Studio 2:**
```bash
scp mac_studio_deployment/mac_studio_2/distributed_config.json user@10.55.0.2:~/homework-grader/
```

### 3. Start Servers with New Models

**On Mac Studio 1 (start Gemma server):**
```bash
ssh user@10.55.0.1
cd ~/homework-grader/mac_studio_deployment/mac_studio_1/servers
python gemma_server.py
```

**On Mac Studio 2 (start Qwen server):**
```bash
ssh user@10.55.0.2
cd ~/homework-grader/mac_studio_deployment/mac_studio_2/servers
python qwen_server.py
```

### 4. Verify Servers are Running

**Check Mac Studio 1 (Gemma):**
```bash
curl http://10.55.0.1:5001/health
```

**Check Mac Studio 2 (Qwen):**
```bash
curl http://10.55.0.2:5002/health
```

### 5. Restart Streamlit App

```bash
# Stop current app
pkill -f streamlit

# Start with new config
streamlit run app.py
```

## Verify in App

The sidebar should now show:

```
🖥️ Distributed MLX System
✅ Mac Studio 1: gemma-3-27b-it-bf16
   Purpose: Feedback Generation
   
✅ Mac Studio 2: Qwen3-Coder-30B-A3B-Instruct-bf16
   Purpose: Code Analysis
   
⚡ True Parallel Processing
🌉 Thunderbolt Bridge Active

Server Details:
Feedback Gen: http://10.55.0.1:5001
   Model: Gemma-3-27B
Code Analysis: http://10.55.0.2:5002
   Model: Qwen3-Coder-30B
```

## Quick One-Liner Script

Create this script to automate the swap:

```bash
#!/bin/bash
# swap_models.sh

echo "🔄 Swapping models between Mac Studios..."

# Stop servers
echo "⏹️ Stopping servers..."
ssh user@10.55.0.1 "pkill -f 'gemma_server.py|qwen_server.py'"
ssh user@10.55.0.2 "pkill -f 'gemma_server.py|qwen_server.py'"

sleep 2

# Copy configs
echo "📋 Updating configurations..."
scp mac_studio_deployment/mac_studio_1/distributed_config.json user@10.55.0.1:~/homework-grader/
scp mac_studio_deployment/mac_studio_2/distributed_config.json user@10.55.0.2:~/homework-grader/

# Start servers with new models
echo "🚀 Starting Mac Studio 1 with Gemma..."
ssh user@10.55.0.1 "cd ~/homework-grader/mac_studio_deployment/mac_studio_1/servers && nohup python gemma_server.py > gemma.log 2>&1 &"

echo "🚀 Starting Mac Studio 2 with Qwen..."
ssh user@10.55.0.2 "cd ~/homework-grader/mac_studio_deployment/mac_studio_2/servers && nohup python qwen_server.py > qwen.log 2>&1 &"

sleep 5

# Verify
echo "✅ Verifying servers..."
curl -s http://10.55.0.1:5001/health && echo "✅ Mac Studio 1 (Gemma) is up"
curl -s http://10.55.0.2:5002/health && echo "✅ Mac Studio 2 (Qwen) is up"

echo "🎉 Model swap complete!"
echo "📱 Restart Streamlit app to see changes"
```

Make it executable:
```bash
chmod +x swap_models.sh
./swap_models.sh
```

## Why This Configuration?

**Gemma on Mac Studio 1 (M3 Ultra 512GB):**
- ✅ More RAM for verbose feedback (3800 tokens)
- ✅ Cleaner output, less internal thinking
- ✅ Better at following instructions
- ✅ Generates personalized feedback

**Qwen on Mac Studio 2 (M4 Max 128GB):**
- ✅ Specialized for code analysis
- ✅ Faster inference on M4
- ✅ Needs less RAM (2400 tokens)
- ✅ Better at technical evaluation

## Troubleshooting

### Servers won't start
Check if models are downloaded:
```bash
# On Mac Studio 1
ssh user@10.55.0.1
ls ~/.cache/huggingface/hub/ | grep gemma-3-27b

# On Mac Studio 2
ssh user@10.55.0.2
ls ~/.cache/huggingface/hub/ | grep Qwen3-Coder
```

### App still shows old configuration
1. Clear browser cache
2. Restart Streamlit: `pkill -f streamlit && streamlit run app.py`
3. Check config file is updated: `cat distributed_config.json`

### Models are slow
- Gemma (27B) should be faster than GPT-OSS (120B)
- First request loads model into memory (~30-60s)
- Subsequent requests should be fast (~15-30s)

## Rollback

To go back to the old configuration, swap the models back in `distributed_config.json` and restart servers.
