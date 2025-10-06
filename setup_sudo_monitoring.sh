#!/bin/bash
# Setup passwordless sudo for powermetrics on both Mac Studios

echo "🔧 Setting up passwordless sudo for monitoring..."
echo ""

# Mac 1 (current machine - humphrjk)
echo "📍 Configuring Mac Studio 1 (local - humphrjk)..."
echo "humphrjk ALL=(ALL) NOPASSWD: /usr/bin/powermetrics" | sudo tee /etc/sudoers.d/powermetrics_humphrjk
sudo chmod 440 /etc/sudoers.d/powermetrics_humphrjk
echo "✅ Mac 1 configured"
echo ""

# Mac 2 (remote - jamiehumphries)
echo "📍 Configuring Mac Studio 2 (remote - jamiehumphries@10.55.0.2)..."
ssh jamiehumphries@10.55.0.2 "echo 'jamiehumphries ALL=(ALL) NOPASSWD: /usr/bin/powermetrics' | sudo tee /etc/sudoers.d/powermetrics_jamiehumphries && sudo chmod 440 /etc/sudoers.d/powermetrics_jamiehumphries"
echo "✅ Mac 2 configured"
echo ""

echo "🎉 Done! Both Macs now allow passwordless sudo for powermetrics"
echo "You can now run: python monitor_dashboard_full.py"
