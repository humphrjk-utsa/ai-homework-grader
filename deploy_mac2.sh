#!/bin/bash
# Deploy to Mac Studio 2 (Gemma Server)
echo "🚀 Deploying to Mac Studio 2 (10.55.0.2)"
echo "=========================================="

# Create directory and copy files to Mac Studio 2
echo "📤 Creating directory and copying files to Mac Studio 2..."
ssh jamiehumphries@10.55.0.2 "mkdir -p ~/homework_grader"
scp -r mac_studio_deployment/mac_studio_2/* jamiehumphries@10.55.0.2:~/homework_grader/

if [ $? -eq 0 ]; then
    echo "✅ Files copied successfully!"
    
    # SSH and setup
    echo "🔧 Setting up Mac Studio 2..."
    ssh jamiehumphries@10.55.0.2 << 'EOF'
        cd ~/homework_grader
        chmod +x *.sh
        echo "📦 Installing dependencies..."
        ./install.sh
        echo "✅ Setup complete!"
        echo "🚀 Starting Gemma server..."
        echo "Press Ctrl+C to stop the server"
        ./start_server.sh
EOF
else
    echo "❌ File copy failed. Check network connection."
fi