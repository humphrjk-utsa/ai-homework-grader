#!/bin/bash
# Quick Deployment Script
echo "🚀 Quick Deployment to Headless Mac Studios"
echo "============================================"

# Check if we have the deployment package
if [ ! -d "mac_studio_deployment" ]; then
    echo "❌ Run python3 deploy_to_headless_mac.py first"
    exit 1
fi

echo "📋 This script will help you deploy to both Mac Studios"
echo ""

# Get SSH details
read -p "Enter username for Mac Studios: " username
read -p "Enter Mac Studio 1 IP (default: 10.55.0.1): " mac1_ip
read -p "Enter Mac Studio 2 IP (default: 10.55.0.2): " mac2_ip

mac1_ip=${mac1_ip:-10.55.0.1}
mac2_ip=${mac2_ip:-10.55.0.2}

echo ""
echo "🔄 Deploying to Mac Studios..."

# Deploy to Mac Studio 1
echo "📤 Deploying to Mac Studio 1 ($mac1_ip)..."
scp -r mac_studio_deployment/mac_studio_1/ $username@$mac1_ip:~/homework_grader/
if [ $? -eq 0 ]; then
    echo "✅ Mac Studio 1 deployment successful"
else
    echo "❌ Mac Studio 1 deployment failed"
fi

# Deploy to Mac Studio 2
echo "📤 Deploying to Mac Studio 2 ($mac2_ip)..."
scp -r mac_studio_deployment/mac_studio_2/ $username@$mac2_ip:~/homework_grader/
if [ $? -eq 0 ]; then
    echo "✅ Mac Studio 2 deployment successful"
else
    echo "❌ Mac Studio 2 deployment failed"
fi

echo ""
echo "🎉 Deployment complete!"
echo ""
echo "Next steps:"
echo "1. SSH to Mac Studio 1: ssh $username@$mac1_ip"
echo "2. Run: cd ~/homework_grader && ./install.sh && ./start_server.sh"
echo "3. SSH to Mac Studio 2: ssh $username@$mac2_ip"
echo "4. Run: cd ~/homework_grader && ./install.sh && ./start_server.sh"
echo "5. Test: python3 test_distributed_system.py"
