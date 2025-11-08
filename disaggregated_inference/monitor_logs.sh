#!/bin/bash
# Monitor all server logs in a tmux session

echo "🔍 Setting up log monitoring..."

# Check if tmux is installed
if ! command -v tmux &> /dev/null; then
    echo "❌ tmux not installed. Install with: brew install tmux"
    exit 1
fi

# Kill existing session if it exists
tmux kill-session -t disagg_logs 2>/dev/null

# Create new session
tmux new-session -d -s disagg_logs -n "Logs"

# Split into 4 panes
tmux split-window -h -t disagg_logs
tmux split-window -v -t disagg_logs:0.0
tmux split-window -v -t disagg_logs:0.2

# Set up each pane
tmux select-pane -t disagg_logs:0.0
tmux send-keys -t disagg_logs:0.0 "echo '=== DGX Spark 1 (Qwen Prefill) ===' && ssh humphrjk@169.254.150.103 'tail -f ~/logs/prefill_qwen.log'" C-m

tmux select-pane -t disagg_logs:0.1
tmux send-keys -t disagg_logs:0.1 "echo '=== Mac Studio 1 (Qwen Decode) ===' && tail -f ~/logs/decode_qwen.log" C-m

tmux select-pane -t disagg_logs:0.2
tmux send-keys -t disagg_logs:0.2 "echo '=== DGX Spark 2 (GPT-OSS Prefill) ===' && ssh humphrjk@169.254.150.104 'tail -f ~/logs/prefill_gpt_oss.log'" C-m

tmux select-pane -t disagg_logs:0.3
tmux send-keys -t disagg_logs:0.3 "echo '=== Mac Studio 2 (GPT-OSS Decode) ===' && ssh humphrjk@169.254.150.102 'tail -f ~/logs/decode_gpt_oss.log'" C-m

# Attach to session
echo "✅ Log monitoring ready!"
echo ""
echo "📊 Attaching to tmux session..."
echo "   Press Ctrl+B then D to detach"
echo ""
sleep 2

tmux attach -t disagg_logs
