#!/bin/bash
# Fix and mount external HDD with proper error handling
# Run with: sudo ./fix_mount_external_hdd.sh

set -e

DEVICE="/dev/sdc2"
MOUNT_POINT="/mnt/sabry_backup"
LABEL="sabry_backup"

echo "=========================================="
echo "Fixing External HDD Mount Issue"
echo "=========================================="
echo ""

# Step 1: Unmount any existing mounts
echo "Step 1: Unmounting any existing mounts..."
sudo umount "$DEVICE" 2>/dev/null || true
sudo umount "/media/sabry3/sabry_backup2" 2>/dev/null || true
sudo umount "$MOUNT_POINT" 2>/dev/null || true
echo "✅ Cleaned up existing mounts"

# Step 2: Check if device exists
echo ""
echo "Step 2: Checking device..."
if [ ! -b "$DEVICE" ]; then
    echo "❌ ERROR: Device $DEVICE not found"
    echo "Available devices:"
    lsblk -o NAME,SIZE,LABEL | grep -E "NAME|sd"
    exit 1
fi
echo "✅ Device found: $DEVICE"

# Step 3: Check filesystem
echo ""
echo "Step 3: Checking filesystem type..."
FS_INFO=$(sudo blkid "$DEVICE" 2>/dev/null || echo "")
FS_TYPE=$(echo "$FS_INFO" | grep -oP 'TYPE="\K[^"]+' || echo "unknown")
echo "Filesystem type: $FS_TYPE"

# Step 4: Install ntfs-3g if needed
echo ""
echo "Step 4: Checking ntfs-3g..."
if ! command -v ntfs-3g >/dev/null 2>&1; then
    echo "⚠️  ntfs-3g not found. Installing..."
    sudo apt-get update -qq
    sudo apt-get install -y ntfs-3g
fi
echo "✅ ntfs-3g is available"

# Step 5: Create mount point
echo ""
echo "Step 5: Creating mount point..."
sudo mkdir -p "$MOUNT_POINT"
sudo chown sabry3:sabry3 "$MOUNT_POINT"
echo "✅ Mount point ready: $MOUNT_POINT"

# Step 6: Try to fix dirty volume (read-only check first)
echo ""
echo "Step 6: Checking volume status..."
if dmesg 2>/dev/null | grep -i "dirty" | grep -q "sdc2"; then
    echo "⚠️  Volume is marked as dirty"
    echo "   Attempting read-only mount first to check filesystem..."
    
    # Try read-only mount first
    if sudo mount -t ntfs-3g -o ro "$DEVICE" "$MOUNT_POINT" 2>/dev/null; then
        echo "✅ Read-only mount successful - filesystem is accessible"
        sudo umount "$MOUNT_POINT"
        echo "   Now attempting read-write mount with force option..."
    fi
fi

# Step 7: Mount with proper options
echo ""
echo "Step 7: Mounting device..."
MOUNT_OPTS="uid=1000,gid=1000,umask=0002"

# Try different mount methods
if sudo mount -t ntfs-3g -o "$MOUNT_OPTS,force" "$DEVICE" "$MOUNT_POINT" 2>&1; then
    echo "✅ Mounted successfully with ntfs-3g!"
elif sudo mount -t ntfs3 -o "$MOUNT_OPTS,force" "$DEVICE" "$MOUNT_POINT" 2>&1; then
    echo "✅ Mounted successfully with ntfs3 driver!"
else
    echo "❌ Mount failed. Trying with additional options..."
    # Last resort: try with windows_names and other options
    sudo mount -t ntfs-3g -o "$MOUNT_OPTS,force,windows_names" "$DEVICE" "$MOUNT_POINT" 2>&1 || {
        echo "❌ All mount attempts failed"
        echo ""
        echo "Troubleshooting steps:"
        echo "1. Check filesystem: sudo ntfsfix /dev/sdc2"
        echo "2. Check filesystem (Windows): chkdsk /f on Windows"
        echo "3. Try read-only: sudo mount -t ntfs-3g -o ro /dev/sdc2 $MOUNT_POINT"
        exit 1
    }
    echo "✅ Mounted with additional options!"
fi

# Step 8: Verify mount
echo ""
echo "Step 8: Verifying mount..."
if mountpoint -q "$MOUNT_POINT"; then
    echo "✅ Mount verified!"
    echo ""
    echo "Disk usage:"
    df -h | grep "$DEVICE"
    echo ""
    echo "Mount point: $MOUNT_POINT"
    echo ""
    echo "First few files:"
    ls -lh "$MOUNT_POINT" | head -10
    echo ""
    echo "✅ External HDD is now accessible at: $MOUNT_POINT"
else
    echo "❌ Mount verification failed"
    exit 1
fi

