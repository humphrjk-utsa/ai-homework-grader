#!/bin/bash
# Complete Mac Studio 2 Backup for Replacement
# Backs up Qwen server, models, configs, and all related data

# ============================================================================
# CONFIGURATION
# ============================================================================

MAC2_USER="jamiehumphries"
MAC2_IP="10.55.0.2"
EXTERNAL_DRIVE="/Volumes/ext1"
BACKUP_NAME="mac2_complete_backup_$(date +%Y%m%d_%H%M)"
BACKUP_DIR="$EXTERNAL_DRIVE/$BACKUP_NAME"

# ============================================================================
# PRE-FLIGHT CHECKS
# ============================================================================

echo "🚀 Mac Studio 2 Complete Backup"
echo "================================"
echo "Source: Mac 2 ($MAC2_IP)"
echo "Destination: $BACKUP_DIR"
echo ""

# Check external drive
if [ ! -d "$EXTERNAL_DRIVE" ]; then
    echo "❌ External drive not found: $EXTERNAL_DRIVE"
    echo "   Please mount the drive and try again"
    exit 1
fi

# Check connectivity to Mac 2
echo "🔍 Checking connection to Mac 2..."
if ! ping -c 1 -W 2 $MAC2_IP > /dev/null 2>&1; then
    echo "❌ Cannot reach Mac 2 at $MAC2_IP"
    echo "   Please check network connection"
    exit 1
fi

echo "✅ Connection OK"
echo ""

# Create backup directory
mkdir -p "$BACKUP_DIR"

# ============================================================================
# BACKUP 1: QWEN MODEL FILES
# ============================================================================

echo "📦 [1/7] Backing up Qwen model files..."
echo "   Location: ~/.cache/huggingface/"
echo "   This will take a while (models are 10-30GB)..."
echo ""

rsync -avz --progress \
    -e "ssh" \
    "$MAC2_USER@$MAC2_IP:~/.cache/huggingface/" \
    "$BACKUP_DIR/huggingface_cache/"

echo "✅ Model files backed up"
echo ""

# ============================================================================
# BACKUP 2: MLX MODELS (if using MLX)
# ============================================================================

echo "📦 [2/7] Backing up MLX models..."
echo "   Location: ~/.cache/mlx/"
echo ""

rsync -avz --progress \
    -e "ssh" \
    "$MAC2_USER@$MAC2_IP:~/.cache/mlx/" \
    "$BACKUP_DIR/mlx_cache/" 2>/dev/null || echo "   (No MLX cache found - skipping)"

echo ""

# ============================================================================
# BACKUP 3: QWEN SERVER CODE
# ============================================================================

echo "📦 [3/7] Backing up Qwen server code..."
echo "   Looking for server scripts..."
echo ""

# Common server locations
for server_path in \
    "~/qwen-server" \
    "~/qwen_server" \
    "~/servers/qwen" \
    "~/ai-homework-grader-clean/qwen_8bit_server.py" \
    "~/ai-homework-grader-clean/qwen_server.py"
do
    rsync -avz --progress \
        -e "ssh" \
        "$MAC2_USER@$MAC2_IP:$server_path" \
        "$BACKUP_DIR/server_code/" 2>/dev/null && echo "   ✅ Found: $server_path"
done

echo ""

# ============================================================================
# BACKUP 4: CONFIGURATION FILES
# ============================================================================

echo "📦 [4/7] Backing up configuration files..."
echo ""

# Server configs
for config in \
    "~/server_config.json" \
    "~/distributed_config.json" \
    "~/.config/qwen/" \
    "~/ai-homework-grader-clean/server_config.json" \
    "~/ai-homework-grader-clean/distributed_config.json"
do
    rsync -avz --progress \
        -e "ssh" \
        "$MAC2_USER@$MAC2_IP:$config" \
        "$BACKUP_DIR/configs/" 2>/dev/null && echo "   ✅ Found: $config"
done

echo ""

# ============================================================================
# BACKUP 5: PYTHON ENVIRONMENT
# ============================================================================

echo "📦 [5/7] Backing up Python environment info..."
echo ""

# Get pip freeze output
ssh "$MAC2_USER@$MAC2_IP" "pip freeze" > "$BACKUP_DIR/pip_requirements.txt" 2>/dev/null
ssh "$MAC2_USER@$MAC2_IP" "pip3 freeze" > "$BACKUP_DIR/pip3_requirements.txt" 2>/dev/null
ssh "$MAC2_USER@$MAC2_IP" "conda list" > "$BACKUP_DIR/conda_packages.txt" 2>/dev/null || echo "   (No conda found)"

# Get Python version
ssh "$MAC2_USER@$MAC2_IP" "python --version" > "$BACKUP_DIR/python_version.txt" 2>&1

echo "✅ Environment info saved"
echo ""

# ============================================================================
# BACKUP 6: STARTUP SCRIPTS
# ============================================================================

echo "📦 [6/7] Backing up startup scripts..."
echo ""

for script in \
    "~/start_qwen_server.sh" \
    "~/start_server.sh" \
    "~/restart_qwen_server.sh" \
    "~/ai-homework-grader-clean/start_qwen_server.sh" \
    "~/ai-homework-grader-clean/qwen_8bit_server.py"
do
    rsync -avz --progress \
        -e "ssh" \
        "$MAC2_USER@$MAC2_IP:$script" \
        "$BACKUP_DIR/scripts/" 2>/dev/null && echo "   ✅ Found: $script"
done

echo ""

# ============================================================================
# BACKUP 7: SYSTEM INFO
# ============================================================================

echo "📦 [7/7] Collecting system information..."
echo ""

# Create system info file
ssh "$MAC2_USER@$MAC2_IP" "system_profiler SPHardwareDataType" > "$BACKUP_DIR/system_info.txt" 2>&1
ssh "$MAC2_USER@$MAC2_IP" "sw_vers" >> "$BACKUP_DIR/system_info.txt" 2>&1
ssh "$MAC2_USER@$MAC2_IP" "uname -a" >> "$BACKUP_DIR/system_info.txt" 2>&1

echo "✅ System info collected"
echo ""

# ============================================================================
# CREATE RESTORATION GUIDE
# ============================================================================

echo "📝 Creating restoration guide..."

cat > "$BACKUP_DIR/RESTORE_INSTRUCTIONS.md" << 'EOF'
# Mac Studio 2 Restoration Guide

## What Was Backed Up

This backup contains everything needed to restore Qwen server on a new Mac Studio:

1. **huggingface_cache/** - All Qwen model files (~10-30GB)
2. **mlx_cache/** - MLX optimized models (if applicable)
3. **server_code/** - Qwen server scripts and code
4. **configs/** - All configuration files
5. **scripts/** - Startup and management scripts
6. **pip_requirements.txt** - Python packages to reinstall
7. **system_info.txt** - Original system specifications

## Restoration Steps

### 1. Setup New Mac Studio

```bash
# Install Homebrew (if not already installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python
brew install python@3.11

# Install MLX (for Apple Silicon)
pip install mlx mlx-lm
```

### 2. Restore Model Files

```bash
# Copy HuggingFace cache
mkdir -p ~/.cache/huggingface
cp -R huggingface_cache/* ~/.cache/huggingface/

# Copy MLX cache (if exists)
mkdir -p ~/.cache/mlx
cp -R mlx_cache/* ~/.cache/mlx/
```

### 3. Restore Server Code

```bash
# Copy server code to desired location
mkdir -p ~/qwen-server
cp -R server_code/* ~/qwen-server/

# Make scripts executable
chmod +x ~/qwen-server/*.sh
```

### 4. Restore Configuration

```bash
# Copy config files
cp configs/server_config.json ~/
cp configs/distributed_config.json ~/

# Update IP address in configs (change to new Mac's IP)
# Edit server_config.json and update IP from 10.55.0.2 to new IP
```

### 5. Reinstall Python Packages

```bash
# Install required packages
pip install -r pip_requirements.txt

# Or install manually:
pip install transformers torch mlx mlx-lm flask requests
```

### 6. Test Server

```bash
# Start server
cd ~/qwen-server
./start_qwen_server.sh

# Test from Mac 1
curl http://NEW_IP:5002/health
```

### 7. Update Mac 1 Configuration

On Mac 1, update the Qwen server IP:

```bash
# Edit distributed_config.json
# Change "qwen_url": "http://10.55.0.2:5002" to new IP

# Edit server_config.json
# Update Mac 2 IP address

# Restart grading system
./restart_servers.sh
```

## Network Configuration

**Original Mac 2:**
- IP: 10.55.0.2
- Port: 5002
- Connection: Thunderbolt bridge

**New Mac Studio:**
- IP: [UPDATE THIS]
- Port: 5002 (keep same)
- Connection: Thunderbolt bridge (reconfigure)

## Verification Checklist

- [ ] Models load successfully
- [ ] Server starts without errors
- [ ] Health endpoint responds
- [ ] Can generate text
- [ ] Mac 1 can connect
- [ ] Grading system works end-to-end

## Troubleshooting

**Models not found:**
- Check ~/.cache/huggingface/hub/ has model files
- Verify permissions: `chmod -R 755 ~/.cache/huggingface`

**Server won't start:**
- Check Python version: `python --version` (should be 3.9+)
- Check packages: `pip list | grep mlx`
- Check logs in server directory

**Mac 1 can't connect:**
- Verify IP address in configs
- Check firewall settings
- Test network: `ping NEW_IP`
- Verify port 5002 is open

## Performance Comparison

Original Mac 2: [See system_info.txt]
New Mac Studio: [Update after setup]

Expected improvements:
- Faster inference (if M4 Ultra)
- More RAM (if upgraded)
- Better thermal management

## Support

If issues arise:
1. Check logs in ~/qwen-server/logs/
2. Verify model files are complete
3. Test with simple generation first
4. Compare with system_info.txt

Backup Date: $(date)
Backup Location: $BACKUP_DIR
EOF

# ============================================================================
# CREATE BACKUP MANIFEST
# ============================================================================

cat > "$BACKUP_DIR/BACKUP_MANIFEST.txt" << EOF
Mac Studio 2 Complete Backup
=============================
Date: $(date)
Source: Mac 2 ($MAC2_IP)
User: $MAC2_USER
Destination: $BACKUP_DIR

Contents:
---------
$(du -sh "$BACKUP_DIR"/* 2>/dev/null)

Total Backup Size: $(du -sh "$BACKUP_DIR" | cut -f1)

Files Backed Up:
----------------
$(find "$BACKUP_DIR" -type f | wc -l) files
$(find "$BACKUP_DIR" -type d | wc -l) directories

Critical Files:
---------------
Models: $(du -sh "$BACKUP_DIR/huggingface_cache" 2>/dev/null | cut -f1 || echo "N/A")
Server: $(du -sh "$BACKUP_DIR/server_code" 2>/dev/null | cut -f1 || echo "N/A")
Configs: $(find "$BACKUP_DIR/configs" -type f 2>/dev/null | wc -l) files

Python Environment:
-------------------
$(cat "$BACKUP_DIR/python_version.txt" 2>/dev/null || echo "N/A")
Packages: $(wc -l < "$BACKUP_DIR/pip_requirements.txt" 2>/dev/null || echo "0") installed

Next Steps:
-----------
1. Verify backup completeness
2. Test restoration on new Mac Studio
3. Update network configuration
4. Update Mac 1 to point to new IP
5. Test end-to-end grading system

Restoration Guide: See RESTORE_INSTRUCTIONS.md
EOF

# ============================================================================
# FINAL SUMMARY
# ============================================================================

echo ""
echo "✅ BACKUP COMPLETE!"
echo "===================="
echo ""
cat "$BACKUP_DIR/BACKUP_MANIFEST.txt"
echo ""
echo "📍 Backup Location: $BACKUP_DIR"
echo "📖 Restoration Guide: $BACKUP_DIR/RESTORE_INSTRUCTIONS.md"
echo ""
echo "🎯 Next Steps:"
echo "   1. Verify backup size is reasonable (should be 10-30GB+)"
echo "   2. Keep external drive safe during Mac replacement"
echo "   3. Follow RESTORE_INSTRUCTIONS.md on new Mac Studio"
echo "   4. Update IP addresses in configs"
echo "   5. Test thoroughly before removing old Mac"
echo ""
echo "🎉 Ready for Mac Studio upgrade!"
