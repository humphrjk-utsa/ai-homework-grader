#!/bin/bash
# Create humphrjk user on Mac Studio 2 with admin rights

MAC2_HOST="jamiehumphries@10.55.0.2"

echo "="*80
echo "🔧 CREATING humphrjk USER ON MAC STUDIO 2"
echo "="*80
echo "This will create a new admin user 'humphrjk' on Mac Studio 2"
echo "for consistency across the cluster"
echo ""

read -p "Continue? (y/n): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Cancelled"
    exit 0
fi

echo ""
echo "📝 Creating user on Mac Studio 2..."
echo ""

# Create the user creation script
cat > /tmp/create_user.sh << 'USERSCRIPT'
#!/bin/bash
# Run this on Mac Studio 2 to create humphrjk user

USERNAME="humphrjk"
FULLNAME="Jamie Humphries (Admin)"

echo "Creating user: $USERNAME"

# Create user
sudo dscl . -create /Users/$USERNAME
sudo dscl . -create /Users/$USERNAME UserShell /bin/zsh
sudo dscl . -create /Users/$USERNAME RealName "$FULLNAME"
sudo dscl . -create /Users/$USERNAME UniqueID 502
sudo dscl . -create /Users/$USERNAME PrimaryGroupID 20
sudo dscl . -create /Users/$USERNAME NFSHomeDirectory /Users/$USERNAME

# Set password (you'll be prompted)
echo "Setting password for $USERNAME..."
sudo dscl . -passwd /Users/$USERNAME

# Add to admin group
echo "Adding to admin group..."
sudo dscl . -append /Groups/admin GroupMembership $USERNAME

# Create home directory
echo "Creating home directory..."
sudo createhomedir -c -u $USERNAME

echo "✅ User $USERNAME created successfully!"
echo ""
echo "📝 Next steps:"
echo "1. Set up SSH keys for passwordless access"
echo "2. Copy .zshrc and other config files"
echo "3. Install necessary software"
USERSCRIPT

# Copy script to Mac 2
echo "📤 Copying user creation script to Mac Studio 2..."
scp /tmp/create_user.sh $MAC2_HOST:/tmp/

echo ""
echo "🚀 Running user creation script on Mac Studio 2..."
echo "   (You'll be prompted for sudo password and new user password)"
echo ""

ssh -t $MAC2_HOST "chmod +x /tmp/create_user.sh && /tmp/create_user.sh"

if [ $? -eq 0 ]; then
    echo ""
    echo "="*80
    echo "✅ USER CREATED SUCCESSFULLY"
    echo "="*80
    echo ""
    echo "📝 Next steps:"
    echo ""
    echo "1. Set up SSH key for passwordless access:"
    echo "   ssh-copy-id humphrjk@10.55.0.2"
    echo ""
    echo "2. Test SSH access:"
    echo "   ssh humphrjk@10.55.0.2"
    echo ""
    echo "3. Update distribute_fp4_models.sh to use humphrjk@10.55.0.2"
    echo ""
else
    echo ""
    echo "❌ User creation failed"
    echo "You may need to create the user manually"
fi

# Cleanup
rm /tmp/create_user.sh
