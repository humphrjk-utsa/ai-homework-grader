# Comprehensive Metrics Guide - AI Homework Grader Inference System

**Last Updated:** 2026-02-03

This document explains all performance metrics tracked by the inference test app.

---

## Table of Contents

1. [Key Performance Indicators](#key-performance-indicators)
2. [Performance Breakdown](#performance-breakdown)
3. [Token Analysis](#token-analysis)
4. [Efficiency Metrics](#efficiency-metrics)
5. [Comparison Metrics](#comparison-metrics)
6. [Export Formats](#export-formats)

---

## Key Performance Indicators

### Total Time
**Metric:** `total_time` (seconds)
**What it measures:** End-to-end time from request to complete response
**Good values:**
- Small prompts (<100 tokens): < 5s
- Medium prompts (500-1000 tokens): 5-15s
- Large prompts (2000+ tokens): 15-30s

**Why it matters:** Direct measure of user-facing latency. Lower is better.

### Prefill Speed (Disaggregated only)
**Metric:** `prefill_speed` (tokens/second)
**What it measures:** How fast the DGX processes the input prompt
**Good values:**
- Qwen-30B on DGX: 200-300 tok/s
- GPT-OSS-120B on DGX: 150-250 tok/s

**Why it matters:** Indicates GPU utilization and parallel processing efficiency. Higher is better.

### Decode Speed
**Metric:** `decode_speed` (tokens/second)
**What it measures:** How fast new tokens are generated
**Good values:**
- Mac Studio (Qwen-30B): 25-35 tok/s
- Mac Studio (GPT-OSS-120B): 10-20 tok/s

**Why it matters:** Determines how quickly responses appear. Limited by sequential generation.

### Overall Throughput
**Metric:** `total_tokens / total_time` (tokens/second)
**What it measures:** Average processing speed across entire request
**Good values:**
- Disaggregated (large prompts): 100-150 tok/s
- Mac-only (large prompts): 30-50 tok/s

**Why it matters:** Best single metric for comparing different approaches.

---

## Performance Breakdown

### Disaggregated Mode

#### Prefill Phase (DGX)
- **Server:** Which DGX Spark (3 or 4)
- **Time:** Time spent processing input prompt
- **Speed:** Tokens processed per second
- **Tokens processed:** Input prompt token count
- **% of total time:** What portion of total time was prefill

**Optimal:** 20-40% of total time for large prompts

#### Decode Phase (Mac)
- **Server:** Which Mac Studio (1 or 2)
- **Time:** Time spent generating new tokens
- **Speed:** Tokens generated per second
- **Tokens generated:** Output token count
- **% of total time:** What portion of total time was decode

**Optimal:** 60-80% of total time (most time spent generating)

#### Network Transfer
- **State Size:** KV cache size in megabytes
  - Typical: 200-342 MB for 2000-4000 token contexts
  - Scales with: context length, model size
- **Est. Transfer Time:** State size ÷ network bandwidth (1.25 GB/s for 10 Gb/s)
  - Should be: < 0.3 seconds
- **Bandwidth Used:** Data transferred in megabits
  - Typical: 1600-2700 Mb per request

### Mac-only Mode

- **Server:** Which Mac Studio
- **Total time:** End-to-end generation time
- **Speed:** Overall tokens/second
- **Method:** `llamacpp_full` (prefill + decode in one phase)

---

## Token Analysis

### Input Tokens
**Metric:** `prompt_tokens`
**What it measures:** Number of tokens in the input prompt
**Typical values:**
- Small test: 20-100 tokens
- Code analysis: 500-2000 tokens
- Full grading: 2000-5000 tokens

**Why it matters:** Determines prefill workload. Larger inputs benefit more from disaggregated.

### Output Tokens
**Metric:** `completion_tokens` or `tokens_generated`
**What it measures:** Number of tokens in the generated response
**Typical values:**
- Quick answer: 50-200 tokens
- Code analysis: 500-1500 tokens
- Full feedback: 1500-2000 tokens

**Why it matters:** Determines decode workload. More outputs = longer generation time.

### Total Tokens
**Metric:** `total_tokens` = input + output
**What it measures:** Total processing load
**Why it matters:** Used to calculate overall throughput and efficiency.

### Output/Input Ratio
**Metric:** `completion_tokens / prompt_tokens`
**What it measures:** Response length relative to prompt
**Typical values:**
- Concise answers: 0.5-1.0x
- Detailed analysis: 1.0-2.0x
- Comprehensive feedback: 2.0-4.0x

**Why it matters:** Shows how much analysis/expansion the model does.

---

## Efficiency Metrics

### Throughput
**Overall:** Total tokens ÷ total time
**Prefill:** Input tokens ÷ prefill time
**Decode:** Output tokens ÷ decode time

**What it measures:** Processing speed at different stages
**Why it matters:** Identifies bottlenecks (prefill vs decode)

### Latency (ms/token)
**Metric:** `(decode_time * 1000) / completion_tokens`
**What it measures:** Milliseconds per generated token
**Good values:**
- < 30 ms/token: Excellent (feels instant)
- 30-50 ms/token: Good (smooth generation)
- > 50 ms/token: Slow (noticeable delays)

**Why it matters:** User experience - lower latency feels more responsive.

### Decode Rate (tokens/minute)
**Metric:** `decode_speed * 60`
**What it measures:** Tokens generated per minute
**Good values:**
- > 1500 tok/min: Excellent
- 600-1500 tok/min: Good
- < 600 tok/min: Needs optimization

**Why it matters:** Easier to understand than tok/s for long-form generation.

### Utilization %
**Metric:** `(actual_speed / max_theoretical_speed) * 100`
**What it measures:** How close to peak performance
**Reference values:**
- DGX Prefill max: ~300 tok/s
- Mac Decode max: ~50 tok/s
- Mac Standalone max: ~50 tok/s

**Why it matters:** Shows if hardware is being used effectively.

---

## Comparison Metrics

When both Mac-only and Disaggregated modes are tested:

### Speedup
**Metric:** `mac_time / disagg_time`
**What it measures:** How much faster disaggregated is
**Example:** 2.0x = disaggregated is twice as fast
**Expected:**
- Small prompts (<100 tokens): ~1.0x (similar)
- Large prompts (2000+ tokens): 1.5-2.5x (significant)

### Time Saved
**Metric:** `mac_time - disagg_time` (seconds)
**What it measures:** Absolute time difference
**Why it matters:** Real-world impact
**Example:** For 100 students, 15s difference = 25 minutes saved total

### Throughput Gain
**Metric:** `((disagg_speed / mac_speed) - 1) * 100` (%)
**What it measures:** Percentage improvement in processing speed
**Expected:** 50-150% for large prompts

### Cost Efficiency
**Metric:** Relative cost per 1000 tokens
**What it measures:** Which mode is more cost-effective
**Calculation:** Time per 1000 tokens (as cost proxy)
**Why it matters:** Helps decide when to use disaggregated vs standalone

---

## Export Formats

### JSON Export
Contains complete raw metrics:
```json
{
  "total_time": 15.63,
  "prefill_time": 9.15,
  "decode_time": 6.47,
  "prefill_speed": 277.2,
  "decode_speed": 17.6,
  "prompt_tokens": 2537,
  "completion_tokens": 100,
  "total_tokens": 2637,
  "state_size_mb": 280.5,
  "method": "disaggregated_llamacpp",
  "prefill_server": "DGX Spark 4 (169.254.150.106:8080)",
  "decode_server": "Mac Studio 1 (169.254.150.101:8081)"
}
```

### CSV Export
Flattened key-value pairs:
```csv
Metric,Value
total_time,15.63
prefill_time,9.15
decode_time,6.47
prefill_speed,277.2
...
```

### Markdown Report
Human-readable summary:
```markdown
# Performance Test Report
Generated: 2026-02-03 14:30:25

## Mode
Disaggregated (DGX + Mac)

## Key Metrics
- Total Time: 15.63s
- Prefill Speed: 277.2 tok/s
- Decode Speed: 17.6 tok/s
- State Size: 280.5 MB
- Total Tokens: 2637
```

---

## Performance History Tracking

The app tracks all tests in a session and provides:

### Session Statistics
- **Total tests run:** Count of all tests
- **Tests by mode:** Disaggregated vs Mac-only breakdown
- **Average metrics:** Mean performance across all tests

### Disaggregated Stats
- Number of tests
- Average total time
- Average prefill speed
- Average decode speed

### Mac-only Stats
- Number of tests
- Average total time
- Average generation speed

---

## Interpreting Results

### When Disaggregated Wins

**Scenario:** Large prompt (2000+ tokens), moderate output (500-1500 tokens)
**Expected Result:**
- Prefill: 200-300 tok/s on DGX (vs 3-5 tok/s on Mac)
- Overall: 2x faster than Mac-only
- Time saved: 10-20 seconds per request

**Why:** DGX excels at parallel prefill processing

### When Mac-only is Comparable

**Scenario:** Small prompt (<100 tokens), small output (<200 tokens)
**Expected Result:**
- Total time: 3-5 seconds (both modes)
- Disaggregated overhead cancels out prefill advantage

**Why:** Network transfer and state loading overhead dominates for tiny prompts

### Red Flags

**Slow Prefill (<100 tok/s):**
- Check: GPU utilization on DGX
- Check: Ollama or other services competing for GPU
- Fix: Stop competing services, restart server

**Slow Decode (<10 tok/s):**
- Check: Mac GPU utilization
- Check: Memory pressure
- Fix: Restart decode server, reduce context length

**Large State Size (>400 MB):**
- Check: Context length setting
- Consider: Reducing n_ctx from 8192 to 6144
- Impact: Smaller states = faster transfers

---

## Best Practices

1. **Run both modes** on the same prompt to get accurate comparisons
2. **Test with realistic workloads** - use actual assignment code
3. **Track performance history** to identify trends
4. **Export metrics** for offline analysis and reporting
5. **Monitor resource usage** to catch degradation early

---

## Troubleshooting

### Unexpectedly Slow Performance

**Check:**
1. Server health (curl /health endpoints)
2. Other processes using GPU (nvidia-smi on DGX, activity monitor on Mac)
3. Network congestion (ping times between machines)
4. Model loaded correctly (check server logs)

### Inconsistent Results

**Possible causes:**
1. GPU thermal throttling (check temperatures)
2. Background processes interfering
3. Network congestion
4. Different prompt sizes (normalize by tokens)

### Missing Metrics

**If disaggregated mode missing prefill_speed:**
- Check prefill server response format
- Verify server is returning 'speed' field
- Update client code if needed

---

## Summary

This metrics system provides comprehensive visibility into:
- ✅ **Performance** - Speed, throughput, latency
- ✅ **Efficiency** - Resource utilization, cost effectiveness
- ✅ **Comparisons** - Mac-only vs Disaggregated
- ✅ **Trends** - Performance history over time
- ✅ **Export** - Data for analysis and reporting

Use these metrics to optimize your inference pipeline and demonstrate the benefits of disaggregated inference!
