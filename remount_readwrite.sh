#!/bin/bash
# Remount external HDD as read-write
# Run with: sudo ./remount_readwrite.sh

set -e

DEVICE="/dev/sdc2"
MOUNT_POINT="/mnt/sabry_backup"

echo "=========================================="
echo "Remounting External HDD as Read-Write"
echo "=========================================="
echo ""

# Step 1: Unmount current read-only mount
echo "Step 1: Unmounting current mount..."
if mountpoint -q "$MOUNT_POINT" 2>/dev/null; then
    # Try normal unmount first
    sudo umount "$MOUNT_POINT" 2>&1 || {
        echo "⚠️  Normal unmount failed, trying lazy unmount..."
        # If busy, use lazy unmount
        sudo umount -l "$MOUNT_POINT" 2>&1
        sleep 3
    }
    echo "✅ Unmounted"
    sleep 2
else
    echo "⚠️  Not mounted or already unmounted"
fi

# Step 2: Remount with read-write using ntfs-3g
echo ""
echo "Step 2: Remounting as read-write with ntfs-3g..."
sudo mount -t ntfs-3g -o uid=1000,gid=1000,umask=0002,force,rw /dev/sdc2 /mnt/sabry_backup 2>&1

# Step 3: Verify mount
echo ""
echo "Step 3: Verifying mount..."
sleep 1

MOUNT_INFO=$(mount | grep sdc2)
if echo "$MOUNT_INFO" | grep -q "rw"; then
    echo "✅ Mounted as read-write!"
    echo ""
    echo "Mount info:"
    echo "$MOUNT_INFO"
    echo ""
    
    # Test write
    echo "Step 4: Testing write access..."
    if touch /mnt/sabry_backup/.write_test 2>/dev/null; then
        rm -f /mnt/sabry_backup/.write_test
        echo "✅ Write test successful - drive is writable!"
    else
        echo "❌ Write test failed - still read-only"
        exit 1
    fi
else
    echo "❌ Still mounted as read-only"
    echo "Mount info: $MOUNT_INFO"
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ External HDD is now mounted read-write!"
echo "=========================================="
echo ""
echo "Location: /mnt/sabry_backup"
df -h | grep sdc2

