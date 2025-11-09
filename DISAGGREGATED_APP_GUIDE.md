# Using the Grading App with Disaggregated System

## 🚀 App is Running

**URL:** http://localhost:8502

## What to Expect

When you grade a submission through the app, the disaggregated system will automatically be used:

### 1. Upload & Configure
- Upload a student notebook (e.g., `homework_lesson_6_joins_Michael_Alexander.ipynb`)
- Select Assignment 6 rubric
- Select the solution notebook
- Enter student name

### 2. Grading Process
The system will show:
- ✅ **4-Layer Validation** (instant)
- ✅ **Code Analysis** via Qwen (DGX Spark 1 → Mac Studio 2)
- ✅ **Feedback Generation** via GPT-OSS (DGX Spark 2 → Mac Studio 1)

### 3. Performance Metrics

You should see metrics like:

**Qwen Metrics (Code Analysis):**
```
Method: disaggregated
Prefill Server: 169.254.150.103:8000 (DGX Spark 1)
Decode Server: 169.254.150.102:8001 (Mac Studio 2)
Prefill Time: ~1-2s
Decode Time: ~5-7s
Decode Speed: ~85 tok/s
```

**GPT-OSS Metrics (Feedback):**
```
Method: disaggregated
Prefill Server: 169.254.150.104:8000 (DGX Spark 2)
Decode Server: 169.254.150.101:8001 (Mac Studio 1)
Prefill Time: ~0.01s
Decode Time: ~15-20s
Decode Speed: ~70 tok/s
```

### 4. Total Time
Expect **~20-30 seconds** for complete grading with detailed feedback.

## Architecture in Action

```
┌─────────────────────────────────────────────────────────┐
│                    YOUR GRADING APP                      │
│                  (Mac Studio 1 - localhost)              │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
┌──────────────┐          ┌──────────────┐
│ QWEN PAIR    │          │ GPT-OSS PAIR │
└──────────────┘          └──────────────┘
        │                         │
        ▼                         ▼
DGX Spark 1 (prefill)     DGX Spark 2 (prefill)
169.254.150.103:8000      169.254.150.104:8000
        │                         │
        ▼                         ▼
Mac Studio 2 (decode)     Mac Studio 1 (decode)
169.254.150.102:8001      localhost:8001
```

## Verification

After grading, check the results page for:
1. ✅ "Method: disaggregated" in metrics
2. ✅ Prefill/Decode server IPs shown
3. ✅ Separate timing for prefill and decode
4. ✅ Token/second speeds displayed

## Troubleshooting

If you see "Method: direct_ollama" instead:
- Check server status: `python3 test_disaggregated_setup.py`
- Restart servers if needed
- Check logs in `~/logs/`

## Test Notebook

Use this for testing:
- **File:** `data/raw/homework_lesson_6_joins_Michael_Alexander.ipynb`
- **Rubric:** Assignment 6
- **Solution:** `homework_lesson_6_joins_SOLUTION.ipynb`
- **Expected Score:** ~7.5/100 (has some output mismatches)
- **Expected Time:** ~19 seconds

## Success Indicators

✅ Both models show "disaggregated" method
✅ Different server pairs for Qwen vs GPT-OSS
✅ Prefill times are fast (< 2s)
✅ Decode speeds are good (70-85 tok/s)
✅ Total grading time is reasonable (~20-30s)
