# Performance Logging System

Monitor and analyze Mac Studio performance during grading operations.

## Quick Start

### 1. Start Continuous Logging

Log metrics every 5 seconds (default):
```bash
python performance_logger.py
```

Custom interval (every 10 seconds):
```bash
python performance_logger.py --interval 10
```

### 2. Log Single Snapshots

Log a single snapshot with event marker:
```bash
python performance_logger.py --single --event "Started batch grading" --notes "25 submissions"
```

### 3. Analyze Logs

Analyze the latest log:
```bash
python analyze_performance_logs.py
```

Analyze specific log file:
```bash
python analyze_performance_logs.py performance_logs/performance_log_20250105_143022.csv
```

## Use Cases

### During Batch Grading

**Terminal 1** - Start logging:
```bash
python performance_logger.py --interval 5
```

**Terminal 2** - Run your grading:
```bash
streamlit run app.py
```

Then grade your submissions. The logger will capture:
- CPU usage on both Mac Studios
- Memory usage
- Server status (up/down)
- Tokens per second
- Active requests

### Mark Important Events

While grading is running, in another terminal:
```bash
# Mark when you start grading
python performance_logger.py --single --event "Started grading Assignment 3"

# Mark when a server crashes
python performance_logger.py --single --event "Qwen crashed" --notes "During Alejandro's notebook"

# Mark when grading completes
python performance_logger.py --single --event "Batch complete" --notes "25/25 graded"
```

## Log Files

Logs are saved to `performance_logs/` directory:
- Format: `performance_log_YYYYMMDD_HHMMSS.csv`
- Each row is a snapshot with timestamp
- Includes metrics from both Mac Studios

### CSV Columns

- `timestamp` - When snapshot was taken
- `mac1_*` - Mac Studio 1 (GPT-OSS) metrics
- `mac2_*` - Mac Studio 2 (Qwen) metrics
- `event` - Event marker (optional)
- `notes` - Additional notes (optional)

## Analysis Output

The analyzer provides:

### Summary
- Start/end times
- Total duration
- Number of snapshots

### Per-Machine Stats
- Average/max/min CPU usage
- Average/max tokens per second
- Total requests processed
- Server uptime percentage

### Issue Detection
- High CPU periods (>80%)
- Server downtime
- Low performance periods (<10 tok/s)
- Timestamps of all issues

## Example Workflow

```bash
# Start logging before grading session
python performance_logger.py --interval 5 &
LOGGER_PID=$!

# Mark start
python performance_logger.py --single --event "Grading session start"

# Do your grading...
# (run streamlit app, grade submissions)

# Mark end
python performance_logger.py --single --event "Grading session end"

# Stop logger
kill $LOGGER_PID

# Analyze results
python analyze_performance_logs.py
```

## Tips

1. **Lower interval for detailed analysis**: Use `--interval 2` for more granular data
2. **Higher interval for long sessions**: Use `--interval 30` to reduce log size
3. **Mark events liberally**: They help correlate issues with specific operations
4. **Keep logs**: They're useful for diagnosing intermittent issues

## Troubleshooting

### "Connection refused" errors
- Check that Mac Studios are accessible via SSH
- Verify IP addresses in the script match your network

### "No data in log file"
- Ensure logger ran for at least one interval
- Check file permissions in `performance_logs/` directory

### Missing pandas for analysis
```bash
pip install pandas
```
