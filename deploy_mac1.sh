#!/bin/bash
# Deploy to Mac Studio 1 (Qwen Server)
echo "🚀 Deploying to Mac Studio 1 (10.55.0.1)"
echo "=========================================="

# Copy files to Mac Studio 1
echo "📤 Copying files to Mac Studio 1..."
scp -r mac_studio_deployment/mac_studio_1/ jamiehumphries@10.55.0.1:~/homework_grader/

if [ $? -eq 0 ]; then
    echo "✅ Files copied successfully!"
    
    # SSH and setup
    echo "🔧 Setting up Mac Studio 1..."
    ssh jamiehumphries@10.55.0.1 << 'EOF'
        cd ~/homework_grader
        chmod +x *.sh
        echo "📦 Installing dependencies..."
        ./install.sh
        echo "✅ Setup complete!"
        echo "🚀 Starting Qwen server..."
        echo "Press Ctrl+C to stop the server"
        ./start_server.sh
EOF
else
    echo "❌ File copy failed. Check network connection."
fi