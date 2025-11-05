# Monitor App Improvements

## ✅ Changes Made

### 1. Added Throughput and Active Requests Display
- System Health section now shows:
  - Combined Throughput (tokens/sec from both servers)
  - Active Requests (total from both servers)
- Added better error handling for health endpoint

### 2. Added Auto-Refresh Toggle
- New checkbox in sidebar: "Auto-refresh"
- Allows you to pause updates to examine data
- Prevents constant screen pulsing when you want to read

### 3. Improved Health Endpoint Parsing
- Now checks for multiple field names:
  - `tokens_per_second` or `throughput`
  - `active_requests` or `requests`
- Better error logging to debug health endpoint issues

## 🎯 About the Pulsing Effect

The "pulsing" you see is caused by Streamlit's `st.rerun()` mechanism, which refreshes the entire page. This is normal Streamlit behavior.

### Options to Reduce Pulsing:

#### Option 1: Disable Auto-Refresh (Now Available)
- Uncheck "Auto-refresh" in sidebar
- Click "Manual Refresh" when you want to update
- No pulsing, full control

#### Option 2: Increase Refresh Rate
- Set refresh rate to 5-10 seconds
- Less frequent updates = less pulsing
- Still automatic but slower

#### Option 3: Use Terminal Monitor (No Pulsing)
```bash
python3 monitor_dashboard.py
```
- Terminal-based, no web interface
- Updates in place, no pulsing
- Simple text display

## 📊 Current Display

### System Health Section Shows:
```
🏥 System Health

System Status        Combined Throughput    Avg CPU Usage    Active Requests
🟢 Online           45.2 tok/s             12.3%            2
Both servers
```

### If Health Endpoint Returns Data:
- **tokens_per_second** or **throughput** → Combined Throughput
- **active_requests** or **requests** → Active Requests

### If Health Endpoint Doesn't Return Data:
- Shows 0.0 tok/s and 0 requests
- Check console logs for health endpoint errors

## 🔍 Debugging Health Endpoint

If throughput shows 0, check:

1. **Are the servers running?**
   ```bash
   curl http://10.55.0.1:5001/health
   curl http://10.55.0.2:5002/health
   ```

2. **What does the health endpoint return?**
   - Should return JSON with metrics
   - Check console logs in monitor app

3. **Is the health endpoint implemented?**
   - The MLX servers need to expose `/health` endpoint
   - Should return: `{"tokens_per_second": X, "active_requests": Y}`

## 🚀 Recommendations

### For Smooth Monitoring:
1. **Use Terminal Monitor** (`monitor_dashboard.py`) for no pulsing
2. **Or disable auto-refresh** in Streamlit app and refresh manually
3. **Or increase refresh rate** to 5-10 seconds

### For Detailed Charts:
1. **Use Streamlit Monitor** (port 8502) with auto-refresh disabled
2. **Examine historical charts** without constant updates
3. **Enable auto-refresh** only when actively monitoring

## 📝 Health Endpoint Format

For the throughput/requests to show, the MLX servers should return:

```json
{
  "status": "healthy",
  "tokens_per_second": 45.2,
  "active_requests": 2,
  "model": "qwen3-coder-30b",
  "uptime": 3600
}
```

Or alternative field names:
```json
{
  "status": "healthy",
  "throughput": 45.2,
  "requests": 2
}
```

The monitor now checks for both formats!
