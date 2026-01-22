# Mac Studio 2 - Manual Setup Required

## Issue
macOS security prevents SSH from launching GUI applications remotely. This means **Macs Fan Control** cannot be auto-started on Mac Studio 2 via the health check script.

## Solution: One-Time Manual Setup

### Option 1: Set to Auto-Start (Recommended)

1. **On Mac Studio 2**, open **System Settings**
2. Go to **General** → **Login Items**
3. Click the **+** button under "Open at Login"
4. Navigate to `/Applications/Macs Fan Control.app`
5. Add it to the list
6. ✅ Macs Fan Control will now start automatically when Mac Studio 2 boots

### Option 2: Start Manually Each Time

1. **SSH into Mac Studio 2**:
   ```bash
   ssh 10.55.0.2
   ```

2. **Start Macs Fan Control**:
   ```bash
   open -a "Macs Fan Control"
   ```

3. **Verify it's running**:
   ```bash
   ps aux | grep "Macs Fan Control" | grep -v grep
   ```

## Current Behavior

The health check script will:
- ✅ Start Macs Fan Control on Mac Studio 1 (local machine)
- ⚠️  Log a warning for Mac Studio 2 (cannot start remotely)
- ✅ Continue with Ollama and decode server startup
- ✅ System will still be fully operational for grading

## Why This Matters

Macs Fan Control helps keep the Mac Studios cool during heavy inference workloads. Without it:
- Fans may not spin up fast enough
- System may thermal throttle
- Performance may degrade over time

**Recommendation**: Use Option 1 (Auto-Start) for best results.

## Verification

To check if Macs Fan Control is running on Mac Studio 2:

```bash
ssh 10.55.0.2 "ps aux | grep 'Macs Fan Control' | grep -v grep"
```

If you see output, it's running. If not, follow Option 1 or 2 above.
