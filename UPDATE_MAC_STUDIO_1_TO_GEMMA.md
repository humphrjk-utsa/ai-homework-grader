# Update Mac Studio 1 to Use Gemma for Feedback

## Current Setup
- **Mac Studio 1** (10.55.0.1): Currently running gpt-oss-120b
- **Mac Studio 2** (10.55.0.2): Running Qwen3-Coder (keep as is)

## What Needs to Change
Mac Studio 1 needs to switch from `gpt-oss-120b` to `gemma-3-27b-it-bf16` for cleaner, more verbose feedback.

## Steps to Update

### Option 1: If Gemma is Already Downloaded on Mac Studio 1

1. **SSH into Mac Studio 1:**
   ```bash
   ssh user@10.55.0.1
   ```

2. **Check if Gemma is available:**
   ```bash
   ls ~/.cache/huggingface/hub/ | grep gemma-3-27b
   ```

3. **If Gemma exists, restart the server:**
   ```bash
   # Stop the current server
   pkill -f "mlx_server.py"
   
   # Start with Gemma
   cd ~/path/to/homework-grader/mac_studio_deployment/mac_studio_1
   python mlx_server.py
   ```

### Option 2: If Gemma Needs to be Downloaded

1. **SSH into Mac Studio 1:**
   ```bash
   ssh user@10.55.0.1
   ```

2. **Download Gemma:**
   ```bash
   # This will download ~54GB
   huggingface-cli download mlx-community/gemma-3-27b-it-bf16
   ```

3. **Restart the server:**
   ```bash
   # Stop the current server
   pkill -f "mlx_server.py"
   
   # Start with Gemma
   cd ~/path/to/homework-grader/mac_studio_deployment/mac_studio_1
   python mlx_server.py
   ```

### Option 3: Quick Test Without Restarting Server

If you want to test first without changing the server:

1. **Update the local config:**
   The `distributed_config.json` has been updated to use Gemma

2. **Test locally:**
   ```bash
   streamlit run app.py
   ```
   
   The app will try to use Gemma on Mac Studio 1. If it's not available, it will fall back to gpt-oss-120b.

## Verify the Change

After updating, check the Streamlit app sidebar. It should show:

```
✅ Mac Studio 1: gemma-3-27b-it-bf16
   Purpose: Feedback Generation
   
✅ Mac Studio 2: Qwen3-Coder-30B-A3B-Instruct-bf16
   Purpose: Code Analysis
```

## Benefits of Using Gemma

- ✅ **Cleaner output** - Less internal thinking/reasoning text
- ✅ **More verbose** - 3000 tokens vs 1200 (2.5x more feedback)
- ✅ **Better instructions** - Follows prompts more accurately
- ✅ **Personalized** - Better at referencing specific student work
- ✅ **Faster** - Smaller model (27B vs 120B) = faster responses

## Configuration Changes Made

Updated `distributed_config.json`:
```json
"mac_studio_1": {
  "model": "mlx-community/gemma-3-27b-it-bf16",  // Changed from gpt-oss-120b
  "max_tokens": 3000,  // Increased from 1200
}
```

## Rollback (if needed)

If you want to go back to gpt-oss-120b:

1. Edit `distributed_config.json`:
   ```json
   "mac_studio_1": {
     "model": "lmstudio-community/gpt-oss-120b-MLX-8bit",
     "max_tokens": 1200,
   }
   ```

2. Restart Mac Studio 1 server

## Next Steps

1. ✅ Update Mac Studio 1 to use Gemma (choose option above)
2. ✅ Restart the server on Mac Studio 1
3. ✅ Start the Streamlit app: `streamlit run app.py`
4. ✅ Grade 2-3 test submissions
5. ✅ Verify feedback is verbose and clean
6. ✅ Grade full assignment batch

## Troubleshooting

### Server won't start with Gemma
**Check:** Is Gemma downloaded?
```bash
ls ~/.cache/huggingface/hub/ | grep gemma-3-27b
```

**Fix:** Download it:
```bash
huggingface-cli download mlx-community/gemma-3-27b-it-bf16
```

### App still shows gpt-oss-120b
**Check:** Is the server running with the new config?
```bash
ssh user@10.55.0.1
ps aux | grep mlx_server
```

**Fix:** Restart the server with new config

### Feedback still has thinking text
**Check:** Verify Gemma is actually being used (check app sidebar)

**Fix:** Ensure Mac Studio 1 server restarted with Gemma model

## Performance Comparison

| Model | Size | Speed | Quality | Thinking Text | Tokens |
|-------|------|-------|---------|---------------|--------|
| gpt-oss-120b | 120B | Slow | Excellent | Heavy | 1200 |
| gemma-3-27b | 27B | Fast | Very Good | Minimal | 3000 |

**Recommendation:** Use Gemma for 2.5x more feedback with cleaner output and faster responses.
