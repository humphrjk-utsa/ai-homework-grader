#!/bin/bash
# Backup Qwen Server and Models from Mac 2 to Mac 1 External Drive

# ============================================================================
# CONFIGURATION - UPDATE THESE PATHS
# ============================================================================

# Mac 2 (source)
MAC2_USER="your_username"
MAC2_IP="10.55.0.2"
QWEN_MODEL_PATH="~/.cache/huggingface/hub/"  # Adjust if different
QWEN_SERVER_PATH="~/qwen-server/"            # Adjust if different

# Mac 1 (destination)
EXTERNAL_DRIVE="/Volumes/ExtDrive1"          # UPDATE THIS
BACKUP_DIR="$EXTERNAL_DRIVE/qwen_backup_$(date +%Y%m%d)"

# ============================================================================
# BACKUP SCRIPT
# ============================================================================

echo "🔄 Qwen Backup Script"
echo "===================="
echo "Source: Mac 2 ($MAC2_IP)"
echo "Destination: $BACKUP_DIR"
echo ""

# Check if external drive is mounted
if [ ! -d "$EXTERNAL_DRIVE" ]; then
    echo "❌ External drive not found: $EXTERNAL_DRIVE"
    echo "   Please mount the drive and try again"
    exit 1
fi

# Create backup directory
echo "📁 Creating backup directory..."
mkdir -p "$BACKUP_DIR"

# Backup 1: Qwen Model Files
echo ""
echo "📦 Backing up Qwen model files..."
echo "   This may take a while (models are large)..."
rsync -avz --progress \
    "$MAC2_USER@$MAC2_IP:$QWEN_MODEL_PATH" \
    "$BACKUP_DIR/models/"

# Backup 2: Qwen Server Code
echo ""
echo "📦 Backing up Qwen server code..."
rsync -avz --progress \
    "$MAC2_USER@$MAC2_IP:$QWEN_SERVER_PATH" \
    "$BACKUP_DIR/server/"

# Backup 3: Server Configuration
echo ""
echo "📦 Backing up server configuration..."
rsync -avz --progress \
    "$MAC2_USER@$MAC2_IP:~/server_config.json" \
    "$BACKUP_DIR/" 2>/dev/null || echo "   (No server_config.json found)"

# Create backup manifest
echo ""
echo "📝 Creating backup manifest..."
cat > "$BACKUP_DIR/BACKUP_INFO.txt" << EOF
Qwen Server Backup
==================
Date: $(date)
Source: Mac 2 ($MAC2_IP)
Destination: $BACKUP_DIR

Contents:
- models/     : Qwen model files from HuggingFace cache
- server/     : Qwen server code and scripts
- config files: Server configuration

To restore:
1. Copy models/ to ~/.cache/huggingface/hub/ on target machine
2. Copy server/ to desired location
3. Update paths in configuration files
4. Test server startup

Model Size: $(du -sh "$BACKUP_DIR/models" 2>/dev/null | cut -f1)
Server Size: $(du -sh "$BACKUP_DIR/server" 2>/dev/null | cut -f1)
Total Size: $(du -sh "$BACKUP_DIR" | cut -f1)
EOF

# Display summary
echo ""
echo "✅ Backup Complete!"
echo "===================="
cat "$BACKUP_DIR/BACKUP_INFO.txt"
echo ""
echo "📍 Backup location: $BACKUP_DIR"

# Optional: Create a compressed archive
read -p "Create compressed archive? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🗜️  Creating compressed archive..."
    cd "$EXTERNAL_DRIVE"
    tar -czf "qwen_backup_$(date +%Y%m%d).tar.gz" "$(basename $BACKUP_DIR)"
    echo "✅ Archive created: qwen_backup_$(date +%Y%m%d).tar.gz"
fi

echo ""
echo "🎉 All done!"
