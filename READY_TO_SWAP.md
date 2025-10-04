# ✅ Ready to Swap Models

## Current Status
All configuration files have been updated to swap the models:

**NEW Configuration:**
- 🖥️ **Mac Studio 1** (10.55.0.1): Gemma for **feedback generation** (3800 tokens)
- 🖥️ **Mac Studio 2** (10.55.0.2): Qwen for **code analysis** (2400 tokens)

## Quick Start

### Option 1: Automated Script (Recommended)
```bash
./swap_models.sh
```

This will:
1. Stop current servers
2. Update configurations
3. Start Gemma on Mac Studio 1
4. Start Qwen on Mac Studio 2
5. Verify servers are running

### Option 2: Manual Steps

See `SWAP_MODELS_INSTRUCTIONS.md` for detailed manual steps.

## After Swapping

1. **Restart Streamlit:**
   ```bash
   pkill -f streamlit
   streamlit run app.py
   ```

2. **Verify in sidebar:**
   Should show:
   ```
   ✅ Mac Studio 1: gemma-3-27b-it-bf16
      Purpose: Feedback Generation
   
   ✅ Mac Studio 2: Qwen3-Coder-30B-A3B-Instruct-bf16
      Purpose: Code Analysis
   ```

3. **Test with a submission:**
   - Grade 1-2 test submissions
   - Check feedback is verbose and clean
   - Verify no "We need to", "Let's" thinking text

## Benefits of This Configuration

✅ **Gemma on Mac Studio 1 (M3 Ultra 512GB):**
- More verbose feedback (3800 tokens vs 1200)
- Cleaner output (no internal thinking)
- Better instruction following
- Personalized per student

✅ **Qwen on Mac Studio 2 (M4 Max 128GB):**
- Specialized for code analysis
- Faster on M4 chip
- Technical evaluation expert

## Files Updated

- ✅ `distributed_config.json` (main config)
- ✅ `mac_studio_deployment/mac_studio_1/distributed_config.json`
- ✅ `mac_studio_deployment/mac_studio_2/distributed_config.json`
- ✅ `swap_models.sh` (automation script)
- ✅ All feedback improvement changes from earlier

## What This Fixes

1. ✅ **More verbose feedback** - 3800 tokens instead of 1200
2. ✅ **Cleaner output** - Gemma has less internal thinking than GPT-OSS
3. ✅ **Personalized feedback** - No generic fallbacks
4. ✅ **Better instructions** - Gemma follows prompts better

## Ready to Go!

Just run:
```bash
./swap_models.sh
```

Then restart the app and start grading! 🚀
