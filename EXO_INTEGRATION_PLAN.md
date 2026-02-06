# Exo Distributed Inference Integration Plan

## What is Exo?

Exo (https://github.com/exo-explore/exo) is a distributed AI inference framework that allows running large language models across multiple heterogeneous devices by splitting model layers across machines.

## Current Setup vs Exo

### Current Disaggregated Inference (Working)
- **Architecture**: Prefill on DGX → KV cache transfer → Decode on Mac
- **Performance**: 198.4 tok/s prefill, 17-22 tok/s decode
- **Throughput**: 125 students/hour
- **Pros**: Working well, optimized KV cache transfer
- **Cons**: State transfer overhead for large prompts

### Potential Exo Setup
- **Architecture**: Model layers split across DGX + Mac
- **How it works**:
  - Early layers run on DGX (fast GPU)
  - Later layers run on Mac (Metal GPU)
  - Activations transferred between devices (much smaller than KV cache)
- **Potential Benefits**:
  - Smaller data transfer (activations vs full KV cache)
  - Both devices actively compute during generation
  - Better resource utilization

## Integration Options

### Option 1: Replace Current System (Not Recommended)
- Switch entirely to exo
- Risk: May not work well for your use case
- Benefit: Simpler architecture if it works

### Option 2: Add Exo as Alternative Backend (Recommended)
- Keep current disaggregated inference system
- Add exo as alternative for comparison
- Choose best approach based on benchmarks
- Architecture:
  ```
  batch_grader.py
      ├── DisaggregatedClient (current, working)
      └── ExoClient (new, experimental)
  ```

### Option 3: Hybrid Approach
- Use current system for sequential grading
- Use exo for parallel batch processing
- Leverage both systems for maximum throughput

## Next Steps

1. **Install Exo**
   ```bash
   pip install exo-lang
   # or
   git clone https://github.com/exo-explore/exo
   cd exo && pip install -e .
   ```

2. **Configure Exo Cluster**
   - Set up DGX Spark nodes as exo workers
   - Set up Mac Studio nodes as exo workers
   - Configure model layer distribution

3. **Create ExoClient**
   - Wrapper similar to DisaggregatedClient
   - Interface for grading system

4. **Benchmark**
   - Compare exo vs current disaggregated inference
   - Measure throughput, latency, resource utilization

5. **Choose Best Approach**
   - May keep current system if it's faster
   - May switch to exo if it offers better performance
   - May use both for different scenarios

## Questions

1. Where did you get exo from? (GitHub, custom build, etc.)
2. Have you already tested it with your DGX + Mac setup?
3. What specific benefits are you hoping to get from exo?

## Current Status

- ✅ Working disaggregated inference system (198.4 tok/s prefill)
- 🔄 New branch created: `exo-distributed-inference`
- ⏳ Ready to install and test exo
