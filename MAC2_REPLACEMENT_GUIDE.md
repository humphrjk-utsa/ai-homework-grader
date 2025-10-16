# Mac Studio 2 Replacement Guide

## 🎯 Quick Start

You're replacing Mac Studio 2 (Qwen server) with a larger/newer Mac Studio. This guide ensures zero downtime and complete data preservation.

---

## 📋 Pre-Replacement Checklist

### Before You Start:
- [ ] External drive connected and mounted
- [ ] Mac 2 is powered on and accessible
- [ ] Network connection is stable
- [ ] You have SSH access to Mac 2

---

## 🚀 Step 1: Run Complete Backup

```bash
# Update the external drive path in the script
nano backup_mac2_complete.sh
# Change: EXTERNAL_DRIVE="/Volumes/ExtDrive1"  # UPDATE THIS PATH

# Run the backup
./backup_mac2_complete.sh
```

**What gets backed up:**
- ✅ All Qwen model files (~10-30GB)
- ✅ MLX optimized models
- ✅ Server code and scripts
- ✅ All configuration files
- ✅ Python environment details
- ✅ Startup scripts
- ✅ System information

**Time estimate:** 30-60 minutes (depending on model size)

---

## 📦 Step 2: Verify Backup

```bash
# Check backup size (should be 10-30GB+)
du -sh /Volumes/ExtDrive1/mac2_complete_backup_*

# Verify critical files exist
ls -lh /Volumes/ExtDrive1/mac2_complete_backup_*/huggingface_cache/
ls -lh /Volumes/ExtDrive1/mac2_complete_backup_*/server_code/
ls -lh /Volumes/ExtDrive1/mac2_complete_backup_*/configs/

# Read the manifest
cat /Volumes/ExtDrive1/mac2_complete_backup_*/BACKUP_MANIFEST.txt
```

---

## 🔄 Step 3: Setup New Mac Studio

### Initial Setup:
1. **Unbox and power on** new Mac Studio
2. **Complete macOS setup** (user account, etc.)
3. **Connect to network** (Thunderbolt bridge to Mac 1)
4. **Assign IP address:** 10.55.0.2 (keep same as old Mac 2)

### Install Prerequisites:

```bash
# Install Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python@3.11

# Install MLX for Apple Silicon
pip3 install mlx mlx-lm

# Install other dependencies
pip3 install transformers torch flask requests
```

---

## 📥 Step 4: Restore from Backup

### Mount External Drive:
```bash
# Connect external drive to new Mac Studio
# It should auto-mount to /Volumes/ExtDrive1
```

### Restore Models:
```bash
# Create cache directories
mkdir -p ~/.cache/huggingface
mkdir -p ~/.cache/mlx

# Copy model files (this takes time!)
cp -R /Volumes/ExtDrive1/mac2_complete_backup_*/huggingface_cache/* ~/.cache/huggingface/
cp -R /Volumes/ExtDrive1/mac2_complete_backup_*/mlx_cache/* ~/.cache/mlx/

# Verify
ls -lh ~/.cache/huggingface/hub/
```

### Restore Server Code:
```bash
# Create server directory
mkdir -p ~/qwen-server

# Copy server files
cp -R /Volumes/ExtDrive1/mac2_complete_backup_*/server_code/* ~/qwen-server/
cp -R /Volumes/ExtDrive1/mac2_complete_backup_*/scripts/* ~/qwen-server/

# Make executable
chmod +x ~/qwen-server/*.sh

# Copy configs
cp /Volumes/ExtDrive1/mac2_complete_backup_*/configs/*.json ~/
```

### Restore Python Environment:
```bash
# Install exact same packages
pip3 install -r /Volumes/ExtDrive1/mac2_complete_backup_*/pip_requirements.txt
```

---

## 🧪 Step 5: Test New Server

### Start Server:
```bash
cd ~/qwen-server
./start_qwen_server.sh
```

### Test Locally:
```bash
# Check health endpoint
curl http://localhost:5002/health

# Test generation
curl -X POST http://localhost:5002/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello, world!", "max_tokens": 50}'
```

### Test from Mac 1:
```bash
# SSH to Mac 1
ssh humphrjk@10.55.0.1

# Test connection
curl http://10.55.0.2:5002/health

# Test grading system
cd ~/ai-homework-grader-clean
python -c "from homework_grader.server_status_manager import test_server_status; test_server_status()"
```

---

## 🔧 Step 6: Update Configurations (if IP changed)

**If you had to use a different IP address:**

### On New Mac Studio:
```bash
# Update server configs
nano ~/server_config.json
# Change IP to new address

nano ~/distributed_config.json
# Update qwen_url
```

### On Mac 1:
```bash
cd ~/ai-homework-grader-clean

# Update distributed config
nano distributed_config.json
# Change: "qwen_url": "http://10.55.0.2:5002" to new IP

# Update server config
nano server_config.json
# Update Mac 2 IP address

# Restart grading system
./restart_servers.sh
```

---

## ✅ Step 7: Verification Checklist

Run through this checklist to ensure everything works:

### Server Health:
- [ ] Server starts without errors
- [ ] Health endpoint responds
- [ ] Can generate text locally
- [ ] No error messages in logs

### Network Connectivity:
- [ ] Mac 1 can ping new Mac Studio
- [ ] Mac 1 can access health endpoint
- [ ] Thunderbolt bridge is configured
- [ ] Firewall allows port 5002

### Grading System:
- [ ] Server status shows "online"
- [ ] Can grade a test notebook
- [ ] Parallel processing works
- [ ] Response times are good

### Performance:
- [ ] Inference speed is acceptable
- [ ] Memory usage is normal
- [ ] No thermal throttling
- [ ] Tokens per second is good

---

## 🎯 Step 8: Decommission Old Mac 2

**Only after everything is verified working:**

1. **Stop server on old Mac 2:**
   ```bash
   ssh humphrjk@10.55.0.2  # (old Mac)
   pkill -f qwen_server
   ```

2. **Keep old Mac 2 running for 1 week** as backup

3. **After 1 week of successful operation:**
   - Wipe old Mac 2
   - Repurpose or sell

---

## 🚨 Troubleshooting

### Models Not Loading:
```bash
# Check model files exist
ls -lh ~/.cache/huggingface/hub/

# Check permissions
chmod -R 755 ~/.cache/huggingface

# Check disk space
df -h
```

### Server Won't Start:
```bash
# Check Python version
python3 --version  # Should be 3.9+

# Check packages
pip3 list | grep mlx
pip3 list | grep transformers

# Check logs
tail -f ~/qwen-server/logs/*.log
```

### Mac 1 Can't Connect:
```bash
# Test network
ping 10.55.0.2

# Check firewall
sudo pfctl -s rules | grep 5002

# Test port
nc -zv 10.55.0.2 5002
```

### Slow Performance:
```bash
# Check CPU/Memory
top

# Check GPU usage
sudo powermetrics --samplers gpu_power -i 1000 -n 1

# Check thermal throttling
pmset -g thermlog
```

---

## 📊 Performance Comparison

### Old Mac Studio 2:
- Model: [Check system_info.txt in backup]
- RAM: [Check backup]
- Inference speed: [Baseline]

### New Mac Studio:
- Model: [Update after setup]
- RAM: [Update after setup]
- Inference speed: [Compare after testing]

**Expected improvements:**
- Faster inference (if M4 Ultra)
- More RAM capacity
- Better thermal management
- Longer sustained performance

---

## 📞 Support

**If you encounter issues:**

1. Check backup restoration guide: `RESTORE_INSTRUCTIONS.md`
2. Review backup manifest: `BACKUP_MANIFEST.txt`
3. Check system logs: `~/qwen-server/logs/`
4. Compare with original system info
5. Test with simple generation first

**Backup Location:**
```
/Volumes/ExtDrive1/mac2_complete_backup_YYYYMMDD_HHMM/
```

---

## 🎉 Success Criteria

You're done when:
- ✅ New Mac Studio runs Qwen server
- ✅ Mac 1 can connect and grade
- ✅ Performance is equal or better
- ✅ No errors in logs
- ✅ Grading system works end-to-end
- ✅ Old Mac 2 is safely backed up

---

*Backup created: [Date]*  
*Restoration tested: [Date]*  
*System verified: [Date]*
