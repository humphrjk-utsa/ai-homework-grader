# Performance Optimization Plan

## Issues Identified

### 1. **File Size Limit (500KB+ files skipped)**
**Current Behavior:**
- Files > 400KB are automatically skipped and marked for manual review
- Files > 300KB get warnings
- Files > 200KB skip output comparison

**Location:** `business_analytics_grader.py` lines 192-233

**Solutions:**

#### Option A: Increase Limits (Quick Fix)
```python
# Change in business_analytics_grader.py
if notebook_size_kb > 600:  # Increase from 400KB to 600KB
    # Skip and mark for manual review
```

#### Option B: Smart Truncation (Better)
- Keep full code cells
- Truncate only output cells
- Preserve markdown for context
- This allows grading without timeout risk

#### Option C: Streaming Processing
- Process notebook in chunks
- Grade sections independently
- Combine results at the end

**Recommended:** Option B - Smart truncation of outputs only

---

### 2. **Performance Issues - Low Throughput**

**Current Metrics:**
- Combined throughput < 50 tok/s
- Parallel efficiency < 1.5x
- Large timing variance (thermal throttling suspected)

**Root Causes:**

#### A. Model Quantization Mismatch
**Mac Studio 2 (Qwen):**
- Config says: `mlx-community/Qwen3-Coder-30B-A3B-Instruct-bf16`
- Actually running: `mlx-community/Qwen3-Coder-30B-A3B-Instruct-8bit`
- bf16 is MUCH slower than 8-bit on M4 Max with 128GB RAM

**Solution:**
```bash
# On Mac Studio 2, switch to 4-bit quantized model for 3x speed boost
ssh jamiehumphries@10.55.0.2
cd ~
# Stop current server
pkill -f qwen_8bit_server

# Update to 4-bit model
# Edit qwen_8bit_server.py to use:
# MODEL_NAME = "mlx-community/Qwen3-Coder-30B-A3B-Instruct-4bit"
```

#### B. Timeout Settings Too Conservative
**Current:** 300 seconds (5 minutes) per request
**Issue:** Allows slow responses to block the queue

**Solution:**
```python
# In distributed_mlx_client.py
# Reduce timeouts for faster failure/retry:
timeout=120  # 2 minutes for code analysis
timeout=150  # 2.5 minutes for feedback
```

#### C. Token Limits Too High
**Current:**
- Qwen: 1800 tokens max
- GPT-OSS: 1200 tokens max

**Issue:** Longer responses = slower throughput

**Solution:**
```json
// In distributed_config.json
"mac_studio_2": {
  "max_tokens": 1200,  // Reduce from 1800
  "temperature": 0.1
},
"mac_studio_1": {
  "max_tokens": 800,   // Reduce from 1200
  "temperature": 0.3
}
```

---

### 3. **Thermal Throttling**

**Symptoms:**
- Large timing variance
- Performance degrades over time
- Fan noise increases

**Current Status:**
- ✅ Macs Fan Control running on Mac Studio 2
- ❓ Need to verify on Mac Studio 1

**Solutions:**

#### Check Mac Studio 1 Fans
```bash
# On Mac Studio 1 (current machine)
ps aux | grep -i "Macs Fan Control"
```

#### Monitor Temperatures
```bash
# Install if not present
brew install osx-cpu-temp

# Monitor during grading
while true; do
  echo "Mac 1: $(osx-cpu-temp)"
  ssh jamiehumphries@10.55.0.2 "osx-cpu-temp" | sed 's/^/Mac 2: /'
  sleep 5
done
```

#### Optimize Fan Curves
- Set minimum fan speed to 40% (not 30%)
- Start ramping at 60°C (not 70°C)
- Max out fans at 80°C (not 90°C)

---

### 4. **Network Latency**

**Current Setup:**
- Thunderbolt bridge: 10.55.0.x network
- Should be < 1ms latency

**Verification:**
```bash
# Test latency
ping -c 10 10.55.0.2

# Test bandwidth
iperf3 -c 10.55.0.2 -t 10
```

**If latency > 5ms:**
- Check Thunderbolt cable connection
- Verify network settings
- Restart network interfaces

---

## Implementation Priority

### Phase 1: Quick Wins (Do Now)
1. ✅ Verify Macs Fan Control on both machines
2. 🔧 Reduce max_tokens in config (800/1200)
3. 🔧 Increase file size limit to 600KB
4. 🔧 Reduce timeouts (120/150 seconds)

### Phase 2: Model Optimization (This Week)
1. 🚀 Switch Mac Studio 2 to 4-bit Qwen model
2. 📊 Benchmark performance improvements
3. 🎯 Adjust token limits based on results

### Phase 3: Smart Processing (Next Week)
1. 💡 Implement output truncation for large files
2. 🔄 Add streaming/chunked processing
3. 📈 Monitor and tune based on real usage

---

## Expected Improvements

### After Phase 1:
- **Throughput:** 50 → 70 tok/s (+40%)
- **File handling:** 400KB → 600KB limit
- **Timeout failures:** Reduced by 30%

### After Phase 2:
- **Throughput:** 70 → 120 tok/s (+70%)
- **Parallel efficiency:** 1.5x → 2.2x
- **Thermal stability:** Improved

### After Phase 3:
- **File handling:** Up to 1MB notebooks
- **Reliability:** 95%+ success rate
- **Processing time:** 2-3 min per submission

---

## Monitoring Commands

```bash
# Check server health
curl http://localhost:5001/health
curl http://10.55.0.2:5002/health

# Monitor performance
python monitor_dashboard.py

# Check processes
ps aux | grep -E "gpt_oss|qwen"

# View logs
tail -f grading_session_*.log
```

---

## Emergency Procedures

### If Server Crashes:
```bash
# Restart GPT-OSS (Mac 1)
python gpt_oss_server_working.py

# Restart Qwen (Mac 2)
ssh jamiehumphries@10.55.0.2
cd ~
python qwen_8bit_server.py
```

### If Performance Degrades:
1. Check temperatures
2. Restart servers
3. Clear any stuck processes
4. Verify network connectivity

### If Files Keep Failing:
1. Check file size
2. Verify notebook format
3. Try manual preprocessing
4. Use output truncation option
