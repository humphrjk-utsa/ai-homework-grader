#!/bin/bash
# Setup passwordless SSH to new DGX Sparks

echo "=========================================="
echo "Setting Up Passwordless SSH"
echo "=========================================="
echo ""

# Check if SSH key exists
if [ ! -f ~/.ssh/id_rsa ]; then
    echo "No SSH key found. Generating new SSH key..."
    ssh-keygen -t rsa -b 4096 -f ~/.ssh/id_rsa -N ""
    echo "✅ SSH key generated"
else
    echo "✅ SSH key already exists"
fi

echo ""
echo "SSH Public Key:"
echo "----------------------------------------"
cat ~/.ssh/id_rsa.pub
echo "----------------------------------------"
echo ""

# Function to setup SSH for a host
setup_ssh() {
    local host=$1
    local name=$2
    
    echo "Setting up SSH for $name ($host)..."
    echo ""
    echo "You will be prompted for the password for $host"
    echo "This is a ONE-TIME setup."
    echo ""
    
    # Copy SSH key
    ssh-copy-id -o StrictHostKeyChecking=no $host
    
    if [ $? -eq 0 ]; then
        echo "✅ SSH key copied to $name"
        
        # Test connection
        echo "Testing passwordless connection..."
        if ssh -o BatchMode=yes -o ConnectTimeout=5 $host "echo 'Connection successful'" 2>/dev/null; then
            echo "✅ Passwordless SSH working for $name"
        else
            echo "⚠️ SSH key copied but connection test failed"
        fi
    else
        echo "❌ Failed to copy SSH key to $name"
        return 1
    fi
    
    echo ""
}

# Setup SSH for both Sparks
echo "=========================================="
echo "Setup DGX Spark 3 (169.254.150.105)"
echo "=========================================="
echo ""
echo "What is the username for Spark 3?"
read -p "Username: " SPARK3_USER
setup_ssh "${SPARK3_USER}@169.254.150.105" "Spark 3"

echo ""
echo "=========================================="
echo "Setup DGX Spark 4 (169.254.150.106)"
echo "=========================================="
echo ""
echo "What is the username for Spark 4?"
read -p "Username: " SPARK4_USER
setup_ssh "${SPARK4_USER}@169.254.150.106" "Spark 4"

echo ""
echo "=========================================="
echo "Summary"
echo "=========================================="
echo ""

# Test all connections
echo "Testing all SSH connections..."
echo ""

for host in "169.254.150.103" "169.254.150.104" "169.254.150.105" "169.254.150.106"; do
    echo -n "  $host: "
    if timeout 2 ssh -o BatchMode=yes -o ConnectTimeout=2 $host "echo OK" 2>/dev/null | grep -q "OK"; then
        echo "✅ Working"
    else
        echo "❌ Not configured or not accessible"
    fi
done

echo ""
echo "=========================================="
echo "Next Steps"
echo "=========================================="
echo ""
echo "Now you can run automated deployment:"
echo "  ./deploy_to_new_sparks.sh"
echo ""
echo "Or manually SSH without password:"
echo "  ssh ${SPARK3_USER}@169.254.150.105"
echo "  ssh ${SPARK4_USER}@169.254.150.106"
echo ""
