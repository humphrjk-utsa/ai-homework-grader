# Timeout and Auto-Restart Improvements

## Changes Made

### 1. Added Explicit Timeout Handling
Both Qwen and Gemma generation now catch and handle timeouts properly:

**Qwen**: 180 second (3 minute) timeout
**Gemma**: 200 second (3.3 minute) timeout

```python
except requests.exceptions.Timeout:
    print(f"⏰ Server timeout after X seconds")
    st.error(f"⏰ Server timeout - request took too long")
    return None
```

### 2. Fixed Auto-Restart for Qwen
Previously, auto-restart wasn't working. Now it:
- Detects when server is down (connection error or non-200 status)
- Calls `self.auto_restart_server('qwen')` or `self.auto_restart_server('gemma')`
- Waits 5 seconds for server to start
- Retries the request once

```python
except requests.exceptions.ConnectionError as e:
    if retry_count == 0 and self.auto_restart_enabled:
        print("🔄 Attempting to auto-restart Qwen server...")
        if self.auto_restart_server('qwen'):
            time.sleep(5)
            return self.generate_code_analysis(prompt, max_tokens, retry_count=1)
```

### 3. Added Retry Logic
Both methods now accept a `retry_count` parameter:
- First attempt: `retry_count=0` - will try auto-restart on failure
- Second attempt: `retry_count=1` - will not retry again (prevents infinite loops)

### 4. Better Error Messages
Now distinguishes between:
- ⏰ **Timeout errors** - request took too long
- ❌ **Connection errors** - server is down/unreachable
- ❌ **HTTP errors** - server returned non-200 status
- ❌ **Other errors** - unexpected failures

## Testing

The auto-restart will trigger when:
1. Qwen server crashes or becomes unresponsive
2. Gemma server crashes or becomes unresponsive
3. Network connection is lost
4. Server returns error status code

## Files Modified

- `models/distributed_mlx_client.py`:
  - Added `retry_count` parameter to both generation methods
  - Added explicit timeout exception handling
  - Added connection error handling with auto-restart
  - Added retry logic after successful restart

## Benefits

1. **More resilient** - automatically recovers from server crashes
2. **Better debugging** - clear error messages about what went wrong
3. **Prevents hangs** - explicit timeouts prevent indefinite waiting
4. **User-friendly** - shows progress and recovery attempts in UI

## Notes

- Auto-restart requires `ServerManager` to be available
- Retry only happens once to prevent infinite loops
- 5-second wait after restart gives server time to initialize
- Timeouts are generous (3+ minutes) to handle large prompts
