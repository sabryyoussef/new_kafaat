#!/bin/bash
# Complete fix for read-only external HDD
# Run with: sudo ./fix_readonly_complete.sh

set -e

DEVICE="/dev/sdc2"
MOUNT_POINT="/mnt/sabry_backup"

echo "=========================================="
echo "Fixing Read-Only External HDD"
echo "=========================================="
echo ""

# Step 1: Kill processes using the mount
echo "Step 1: Checking for processes using the mount..."
PROCS=$(lsof "$MOUNT_POINT" 2>/dev/null | tail -n +2 | awk '{print $2}' | sort -u)
if [ -n "$PROCS" ]; then
    echo "⚠️  Found processes using the mount: $PROCS"
    echo "   Killing processes..."
    for pid in $PROCS; do
        sudo kill -9 "$pid" 2>/dev/null || true
    done
    sleep 2
    echo "✅ Processes terminated"
else
    echo "✅ No processes using the mount"
fi

# Step 2: Unmount
echo ""
echo "Step 2: Unmounting..."
if mountpoint -q "$MOUNT_POINT" 2>/dev/null; then
    # Try normal unmount
    if sudo umount "$MOUNT_POINT" 2>&1; then
        echo "✅ Unmounted successfully"
    else
        echo "⚠️  Normal unmount failed, trying lazy unmount..."
        sudo umount -l "$MOUNT_POINT" 2>&1
        sleep 3
        echo "✅ Lazy unmount completed"
    fi
else
    echo "⚠️  Not mounted"
fi

# Step 3: Wait a moment
sleep 2

# Step 4: Remount as read-write
echo ""
echo "Step 3: Remounting as read-write with ntfs-3g..."
sudo mount -t ntfs-3g -o uid=1000,gid=1000,umask=0002,force,rw "$DEVICE" "$MOUNT_POINT" 2>&1

# Step 5: Verify
echo ""
echo "Step 4: Verifying mount..."
sleep 2

MOUNT_INFO=$(mount | grep "$DEVICE" || echo "")
if echo "$MOUNT_INFO" | grep -q "rw"; then
    echo "✅ Mounted as READ-WRITE!"
    echo ""
    echo "Mount details:"
    echo "$MOUNT_INFO"
    echo ""
    
    # Test write
    echo "Step 5: Testing write access..."
    TEST_FILE="$MOUNT_POINT/.rw_test_$(date +%s)"
    if touch "$TEST_FILE" 2>/dev/null; then
        rm -f "$TEST_FILE"
        echo "✅ Write test PASSED - drive is writable!"
    else
        echo "❌ Write test FAILED"
        exit 1
    fi
else
    echo "❌ Still mounted as read-only!"
    echo "Mount info: $MOUNT_INFO"
    echo ""
    echo "Troubleshooting:"
    echo "1. Check if device is locked: sudo fuser -m $MOUNT_POINT"
    echo "2. Try: sudo mount -t ntfs-3g -o force,rw $DEVICE $MOUNT_POINT"
    exit 1
fi

echo ""
echo "=========================================="
echo "✅ SUCCESS - External HDD is now writable!"
echo "=========================================="
echo ""
echo "Location: $MOUNT_POINT"
df -h | grep "$DEVICE"

