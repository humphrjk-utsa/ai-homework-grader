# Setup Macs Fan Control on Mac Studio 2

## Quick Setup (One-Time, 2 Minutes)

### Step 1: Add to Login Items

1. **On Mac Studio 2**, open **System Settings** (⚙️)
2. Click **General** in the sidebar
3. Click **Login Items**
4. Under "Open at Login", click the **+** button
5. Navigate to **Applications** folder
6. Select **Macs Fan Control.app**
7. Click **Open**

✅ Done! Macs Fan Control will now start automatically when Mac Studio 2 boots.

### Step 2: Start It Now (Without Rebooting)

On Mac Studio 2, either:
- **Option A**: Double-click Macs Fan Control in Applications folder
- **Option B**: From terminal: `open -a "Macs Fan Control"`

## Verification

To verify it's running:
```bash
ssh 10.55.0.2 "ps aux | grep 'Macs Fan Control' | grep -v grep"
```

If you see output, it's running! ✅

## Why This Matters

- Keeps Mac Studio 2 cool during heavy inference workloads
- Prevents thermal throttling
- Maintains consistent performance
- Protects hardware

## Alternative: Manual Start Each Time

If you prefer not to auto-start, you can manually start it when needed:
```bash
ssh 10.55.0.2
open -a "Macs Fan Control"
```

**Note**: The health check script will work either way - the system is fully operational for grading with or without Macs Fan Control running.
