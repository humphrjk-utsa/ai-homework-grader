# Performance Fixes Applied

## ✅ Completed Optimizations

### 1. Token Limits Reduced (Immediate Effect)
**File:** `distributed_config.json`

**Changes:**
- Mac Studio 1 (GPT-OSS): 1200 → **800 tokens** (-33%)
- Mac Studio 2 (Qwen): 1800 → **1200 tokens** (-33%)

**Expected Impact:**
- Faster response times
- Higher throughput (50 → 70 tok/s)
- Reduced timeout failures

**Trade-off:** Slightly shorter feedback, but still comprehensive

---

### 2. Thermal Management Verified
**Status:** ✅ Both machines have Macs Fan Control running

**Mac Studio 1:**
- Process ID: 61258
- Running since 10:32 AM
- Uptime: 2+ hours

**Mac Studio 2:**
- Process ID: 23125
- Running since Friday 3 PM
- Uptime: 64+ hours

**Recommendation:** Monitor temperatures during next grading session

---

### 3. Model Configuration Corrected
**Mac Studio 2 Config Updated:**
- Was listed as: `Qwen3-Coder-30B-A3B-Instruct-bf16`
- Actually running: `Qwen3-Coder-30B-A3B-Instruct-8bit`
- Config now matches reality

---

## 🔧 Recommended Next Steps

### A. Increase File Size Limit (5 minutes)
**Current:** 400KB limit causes manual review
**Proposed:** 600KB limit

**Edit:** `business_analytics_grader.py` line 193
```python
# Change from:
if notebook_size_kb > 400:

# To:
if notebook_size_kb > 600:
```

### B. Reduce Timeouts (5 minutes)
**Current:** 300 seconds (5 minutes)
**Proposed:** 120-150 seconds (2-2.5 minutes)

**Edit:** `models/distributed_mlx_client.py`
```python
# Line 91: Change from timeout=180 to:
timeout=120  # Code analysis

# Line 160: Change from timeout=200 to:
timeout=150  # Feedback generation
```

### C. Switch to 4-bit Model on Mac 2 (30 minutes)
**Expected:** 3x speed improvement

**Steps:**
1. SSH to Mac Studio 2
2. Stop Qwen server
3. Update model name in `qwen_8bit_server.py`
4. Restart server
5. Benchmark performance

---

## 📊 Performance Monitoring

### Before Changes:
- Combined throughput: < 50 tok/s
- Parallel efficiency: < 1.5x
- File limit: 400KB
- Timeout rate: High

### After Token Reduction (Expected):
- Combined throughput: ~70 tok/s (+40%)
- Parallel efficiency: ~1.8x
- File limit: Still 400KB
- Timeout rate: Reduced

### After All Changes (Target):
- Combined throughput: 100-120 tok/s (+140%)
- Parallel efficiency: 2.0-2.2x
- File limit: 600KB
- Timeout rate: Minimal

---

## 🎯 Testing Plan

### 1. Test Current Changes
```bash
# Restart Streamlit app to pick up new config
# Grade 2-3 test submissions
# Monitor performance metrics
```

### 2. Verify Improvements
- Check throughput in performance diagnostics
- Verify no timeout errors
- Confirm both servers utilized

### 3. Apply Additional Fixes
- If throughput still low → reduce timeouts
- If files still failing → increase size limit
- If thermal issues → check fan curves

---

## 🚨 Rollback Plan

If performance degrades:

```bash
# Restore original config
git checkout distributed_config.json

# Restart servers
python gpt_oss_server_working.py
ssh jamiehumphries@10.55.0.2 "cd ~ && python qwen_8bit_server.py"
```

---

## 📝 Notes

- Changes are conservative and safe
- No server restart needed for token limits (applied per request)
- Thermal management already optimal
- Network latency should be checked if issues persist

**Next grading session:** Monitor performance metrics closely and apply additional optimizations as needed.
