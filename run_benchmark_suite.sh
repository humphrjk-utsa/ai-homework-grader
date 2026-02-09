#!/bin/bash
# ═══════════════════════════════════════════════════════════════════════════════
# Parallax Benchmark Suite Orchestrator
# Runs benchmarks across all model + cluster configurations
#
# Usage:
#   ./run_benchmark_suite.sh                # Run full suite (all 6 phases)
#   ./run_benchmark_suite.sh --full-only    # Only full cluster tests
#   ./run_benchmark_suite.sh --macs-only    # Only macs-only tests
#   ./run_benchmark_suite.sh --sparks-only  # Only sparks-only tests
#   ./run_benchmark_suite.sh --report       # Just regenerate report from existing results
# ═══════════════════════════════════════════════════════════════════════════════

set -euo pipefail

# ─── Configuration ────────────────────────────────────────────────────────────

PROJECT_DIR="/Users/humphrjk/Library/CloudStorage/OneDrive-ionxs.ai/analytics/ai-homework-grader"
PARALLAX_DIR="/Users/humphrjk/parallax"
RESULTS_DIR="$PROJECT_DIR/benchmark_results"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

# Find Python - try project venv, then parallax venv, then system
if [ -f "$PROJECT_DIR/.venv/bin/python" ]; then
    PYTHON="$PROJECT_DIR/.venv/bin/python"
elif [ -f "$PROJECT_DIR/venv/bin/python" ]; then
    PYTHON="$PROJECT_DIR/venv/bin/python"
elif [ -f "$PARALLAX_DIR/venv/bin/python" ]; then
    PYTHON="$PARALLAX_DIR/venv/bin/python"
else
    PYTHON="python3"
fi

BENCHMARK_SCRIPT="$PROJECT_DIR/parallax_benchmark.py"

# Model IDs (SafeTensors from HuggingFace)
GPT_OSS_MODEL="openai/gpt-oss-120b"
QWEN_MODEL="Qwen/Qwen3-Coder-30B-A3B-Instruct"

# Benchmark settings
ITERATIONS=3
MAX_TOKENS=500
PROMPT_SIZES="2500 6500"

# Timing
WAIT_AFTER_START=30        # seconds after cluster start before readiness check
WAIT_AFTER_STOP=15         # seconds after cluster stop before next start
CLUSTER_READY_TIMEOUT=600  # max seconds to wait for inference readiness (10 min for large models)

# Network
SCHEDULER_IP="169.254.150.101"
SCHEDULER_URL="http://${SCHEDULER_IP}:3001"
MAC2_IP="169.254.150.102"
SPARK1_IP="169.254.150.106"
SPARK2_IP="169.254.150.105"

# ─── Helper Functions ─────────────────────────────────────────────────────────

log() {
    echo "[$(date '+%H:%M:%S')] $*"
}

separator() {
    echo ""
    echo "══════════════════════════════════════════════════════════════════════"
    echo "  $*"
    echo "══════════════════════════════════════════════════════════════════════"
}

verify_cluster() {
    log "Verifying cluster readiness (testing actual inference)..."
    local elapsed=0
    while [ $elapsed -lt $CLUSTER_READY_TIMEOUT ]; do
        # First check if scheduler is even responding
        if ! curl -s "${SCHEDULER_URL}/" > /dev/null 2>&1; then
            elapsed=$((elapsed + 15))
            log "  Scheduler not responding yet... ($elapsed/${CLUSTER_READY_TIMEOUT}s)"
            sleep 15
            continue
        fi

        # Test actual inference - this verifies workers have loaded model layers
        local result
        result=$(curl -s --max-time 30 -X POST "${SCHEDULER_URL}/v1/chat/completions" \
            -H 'Content-Type: application/json' \
            -d '{"messages":[{"role":"user","content":"Say hello"}],"max_tokens":10}' 2>/dev/null)

        if echo "$result" | grep -q '"choices"'; then
            log "Cluster is ready - inference working!"
            return 0
        fi

        elapsed=$((elapsed + 20))
        log "  Inference not ready yet... ($elapsed/${CLUSTER_READY_TIMEOUT}s)"
        sleep 20
    done
    log "ERROR: Cluster inference did not become ready after ${CLUSTER_READY_TIMEOUT}s"
    return 1
}

stop_cluster() {
    log "Stopping cluster..."
    "$PROJECT_DIR/parallax_cluster_stop.sh" 2>&1 || true
    log "Waiting ${WAIT_AFTER_STOP}s for clean shutdown..."
    sleep $WAIT_AFTER_STOP
}

# ─── Full Cluster Start (4 nodes) ────────────────────────────────────────────

start_full_cluster() {
    local model="$1"
    separator "Starting FULL CLUSTER (4 nodes) with: $model"

    # Use existing start script
    "$PROJECT_DIR/parallax_cluster_start.sh" "$model" 2>&1

    log "Waiting ${WAIT_AFTER_START}s for cluster to stabilize..."
    sleep $WAIT_AFTER_START

    if ! verify_cluster; then
        log "WARNING: Cluster may not be fully ready, proceeding anyway..."
    fi
}

# ─── Macs-Only Cluster Start (2 Mac workers) ────────────────────────────────

start_macs_only() {
    local model="$1"
    separator "Starting MACS-ONLY CLUSTER (2 Mac workers) with: $model"

    # Step 1: Start scheduler on Mac 1 (localhost) - scheduler only, not a worker
    log "[1/3] Starting Mac 1 (Scheduler - localhost)..."
    cd "$PARALLAX_DIR"
    source venv/bin/activate
    nohup parallax run -m "$model" -n 2 --host 0.0.0.0 > /tmp/parallax_scheduler.log 2>&1 &
    log "  Scheduler starting (log: /tmp/parallax_scheduler.log)"
    log "  Waiting 15s for scheduler initialization..."
    sleep 15

    # Check scheduler
    if curl -s http://localhost:3001/ > /dev/null 2>&1; then
        log "  Scheduler is online"
    else
        log "  Scheduler may still be starting, continuing..."
    fi

    # Step 2: Join Mac 1 as local worker (512GB M3 Ultra - handles bulk of layers)
    log ""
    log "[2/3] Starting Mac 1 (Local Worker - localhost)..."
    nohup parallax join --param-mem-ratio 0.5 > /tmp/parallax_mac1_worker.log 2>&1 &
    log "  Local worker starting (log: /tmp/parallax_mac1_worker.log)"

    # Step 3: Join Mac 2 as worker with reduced param_mem_ratio to avoid OOM
    # Mac 2 (128GB) with 0.2 ratio = 25.6GB for params → ~21 layers (not all 48)
    log ""
    log "[3/3] Starting Mac 2 (Worker - ${MAC2_IP}, param_mem_ratio=0.2)..."
    ssh humphrjk@${MAC2_IP} "cd ${PARALLAX_DIR} && source venv/bin/activate && nohup parallax join --param-mem-ratio 0.2 > /tmp/parallax_worker.log 2>&1 &"
    log "  Worker starting (log: /tmp/parallax_worker.log on Mac 2)"

    # NO DGX Spark containers started

    log "Waiting ${WAIT_AFTER_START}s for cluster to stabilize..."
    sleep $WAIT_AFTER_START

    if ! verify_cluster; then
        log "WARNING: Cluster may not be fully ready, proceeding anyway..."
    fi

    log "Macs-Only cluster started (Mac 1 worker + Mac 2 worker, no DGX Sparks)"
}

# ─── Sparks-Only Cluster Start (2 DGX nodes + scheduler) ─────────────────

start_sparks_only() {
    local model="$1"
    separator "Starting SPARKS-ONLY CLUSTER (2 DGX Sparks) with: $model"

    # Step 1: Start scheduler on Mac 1 (coordinator only, not a worker)
    log "[1/3] Starting Mac 1 (Scheduler only - localhost)..."
    cd "$PARALLAX_DIR"
    source venv/bin/activate
    nohup parallax run -m "$model" -n 2 --host 0.0.0.0 > /tmp/parallax_scheduler.log 2>&1 &
    log "  Scheduler starting (log: /tmp/parallax_scheduler.log)"
    log "  Waiting 15s for scheduler initialization..."
    sleep 15

    # Check scheduler
    if curl -s http://localhost:3001/ > /dev/null 2>&1; then
        log "  Scheduler is online"
    else
        log "  Scheduler may still be starting, continuing..."
    fi

    # Step 2: Start spark-2935 Docker container
    log ""
    log "[2/3] Starting spark-2935 (${SPARK1_IP})..."
    ssh humphrjk@${SPARK1_IP} "sudo docker run -d --gpus all --network host -v /home/humphrjk/.cache/huggingface:/root/.cache/huggingface gradientservice/parallax:latest-spark parallax join" && log "  Docker container started" || log "  Failed to start container"

    # Step 3: Start RR191562IP01 Docker container
    log ""
    log "[3/3] Starting RR191562IP01 (${SPARK2_IP})..."
    ssh humphrjk@${SPARK2_IP} "sudo docker run -d --gpus all --network host -v /home/humphrjk/.cache/huggingface:/root/.cache/huggingface gradientservice/parallax:latest-spark parallax join" && log "  Docker container started" || log "  Failed to start container"

    # NO Mac 2 worker started — Sparks handle everything

    log "Waiting ${WAIT_AFTER_START}s for cluster to stabilize..."
    sleep $WAIT_AFTER_START

    if ! verify_cluster; then
        log "WARNING: Cluster may not be fully ready, proceeding anyway..."
    fi

    log "Sparks-Only cluster started (2x DGX Spark, no Mac workers)"
}

# ─── Run Benchmark ────────────────────────────────────────────────────────────

run_benchmark() {
    local model="$1"
    local config="$2"

    local model_slug=$(echo "$model" | tr '/' '_')
    local log_file="${RESULTS_DIR}/log_${config}_${model_slug}_${TIMESTAMP}.txt"

    log "Running benchmark: model=$model config=$config"
    log "Log file: $log_file"

    "$PYTHON" "$BENCHMARK_SCRIPT" --run \
        --model "$model" \
        --cluster-config "$config" \
        --prompt-sizes $PROMPT_SIZES \
        --iterations $ITERATIONS \
        --max-tokens $MAX_TOKENS \
        --output-dir "$RESULTS_DIR" \
        --scheduler-url "$SCHEDULER_URL" \
        2>&1 | tee "$log_file"

    local exit_code=${PIPESTATUS[0]}
    if [ $exit_code -ne 0 ]; then
        log "WARNING: Benchmark exited with code $exit_code"
    fi
}

# ─── Generate Report ──────────────────────────────────────────────────────────

generate_report() {
    log "Generating comparison report..."
    local json_files=$(find "$RESULTS_DIR" -name "*.json" -newer "$RESULTS_DIR" -o -name "*.json" | head -20)

    if [ -z "$json_files" ]; then
        # Fall back to all JSON files in directory
        json_files=$(ls "$RESULTS_DIR"/*.json 2>/dev/null || true)
    fi

    if [ -z "$json_files" ]; then
        log "No JSON result files found in $RESULTS_DIR"
        return 1
    fi

    "$PYTHON" "$BENCHMARK_SCRIPT" --report $json_files --output-dir "$RESULTS_DIR" 2>&1
}

# ─── Main ─────────────────────────────────────────────────────────────────────

main() {
    local mode="${1:---all}"

    separator "PARALLAX BENCHMARK SUITE"
    log "Mode: $mode"
    log "Models: $GPT_OSS_MODEL, $QWEN_MODEL"
    log "Prompt sizes: $PROMPT_SIZES tokens"
    log "Iterations: $ITERATIONS per configuration"
    log "Max output tokens: $MAX_TOKENS"
    log "Python: $PYTHON"
    log "Results: $RESULTS_DIR"
    log ""

    mkdir -p "$RESULTS_DIR"

    # Report-only mode
    if [ "$mode" = "--report" ]; then
        generate_report
        return 0
    fi

    local start_time=$(date +%s)

    # ─── Full Cluster Benchmarks ──────────────────────────────────────────
    if [ "$mode" = "--all" ] || [ "$mode" = "--full-only" ]; then

        # Phase 1: Full Cluster + GPT-OSS 120B
        separator "PHASE 1/6: Full Cluster + GPT-OSS 120B"
        stop_cluster
        start_full_cluster "$GPT_OSS_MODEL"
        run_benchmark "$GPT_OSS_MODEL" "full_cluster"
        stop_cluster

        # Phase 2: Full Cluster + Qwen3 Coder
        separator "PHASE 2/6: Full Cluster + Qwen3 Coder 30B"
        start_full_cluster "$QWEN_MODEL"
        run_benchmark "$QWEN_MODEL" "full_cluster"
        stop_cluster
    fi

    # ─── Macs-Only Benchmarks ─────────────────────────────────────────────
    if [ "$mode" = "--all" ] || [ "$mode" = "--macs-only" ]; then

        # Phase 3: Macs Only + GPT-OSS 120B
        separator "PHASE 3/6: Macs Only + GPT-OSS 120B"
        stop_cluster
        start_macs_only "$GPT_OSS_MODEL"
        run_benchmark "$GPT_OSS_MODEL" "macs_only"
        stop_cluster

        # Phase 4: Macs Only + Qwen3 Coder
        separator "PHASE 4/6: Macs Only + Qwen3 Coder 30B"
        start_macs_only "$QWEN_MODEL"
        run_benchmark "$QWEN_MODEL" "macs_only"
        stop_cluster
    fi

    # ─── Sparks-Only Benchmarks ───────────────────────────────────────────
    if [ "$mode" = "--all" ] || [ "$mode" = "--sparks-only" ]; then

        # Phase 5: Sparks Only + GPT-OSS 120B
        separator "PHASE 5/6: Sparks Only + GPT-OSS 120B"
        stop_cluster
        start_sparks_only "$GPT_OSS_MODEL"
        run_benchmark "$GPT_OSS_MODEL" "sparks_only"
        stop_cluster

        # Phase 6: Sparks Only + Qwen3 Coder
        separator "PHASE 6/6: Sparks Only + Qwen3 Coder 30B"
        start_sparks_only "$QWEN_MODEL"
        run_benchmark "$QWEN_MODEL" "sparks_only"
        stop_cluster
    fi

    # ─── Generate Comparison Report ───────────────────────────────────────
    separator "GENERATING COMPARISON REPORT"
    generate_report

    local end_time=$(date +%s)
    local duration=$(( end_time - start_time ))
    local minutes=$(( duration / 60 ))
    local seconds=$(( duration % 60 ))

    separator "BENCHMARK SUITE COMPLETE"
    log "Total time: ${minutes}m ${seconds}s"
    log "Results directory: $RESULTS_DIR"
    log ""
    log "Result files:"
    ls -la "$RESULTS_DIR"/*.json 2>/dev/null || log "  (no JSON files)"
    log ""
    log "Report:"
    ls -la "$RESULTS_DIR"/comparison_report_*.txt 2>/dev/null || log "  (no report)"
}

main "$@"
