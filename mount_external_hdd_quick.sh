#!/bin/bash
# Quick mount script for external HDD (sabry_backup)
# Device may change (sdb2, sdc2, etc.) - this script auto-detects it

MOUNT_POINT="/mnt/sabry_backup"
LABEL="sabry_backup"

echo "Mounting external HDD (sabry_backup)..."

# Find device by label
DEVICE=$(sudo blkid -L "$LABEL" 2>/dev/null)

if [ -z "$DEVICE" ]; then
    # Try common device names
    for dev in /dev/sdc2 /dev/sdb2 /dev/sdd2; do
        if [ -b "$dev" ]; then
            DEV_LABEL=$(sudo blkid -s LABEL -o value "$dev" 2>/dev/null)
            if [ "$DEV_LABEL" = "$LABEL" ]; then
                DEVICE="$dev"
                break
            fi
        fi
    done
fi

if [ -z "$DEVICE" ]; then
    echo "❌ ERROR: Could not find device with label '$LABEL'"
    echo "Available block devices:"
    lsblk -o NAME,SIZE,LABEL | grep -E "NAME|sd"
    exit 1
fi

echo "Found device: $DEVICE"

# Check if already mounted
if mountpoint -q "$MOUNT_POINT" 2>/dev/null; then
    echo "✅ Already mounted at $MOUNT_POINT"
    df -h | grep "$DEVICE"
    exit 0
fi

# Mount with force option (volume may be dirty)
echo "Mounting $DEVICE to $MOUNT_POINT..."
sudo mount -t ntfs-3g -o uid=1000,gid=1000,umask=0002,force "$DEVICE" "$MOUNT_POINT" 2>&1

if mountpoint -q "$MOUNT_POINT" 2>/dev/null; then
    echo "✅ Mounted successfully!"
    df -h | grep "$DEVICE"
else
    echo "❌ Mount failed. Trying with ntfs3 driver..."
    sudo mount -t ntfs3 -o uid=1000,gid=1000,umask=0002,force "$DEVICE" "$MOUNT_POINT" 2>&1
    if mountpoint -q "$MOUNT_POINT" 2>/dev/null; then
        echo "✅ Mounted successfully with ntfs3!"
        df -h | grep "$DEVICE"
    else
        echo "❌ Mount failed. Check logs above for details."
        exit 1
    fi
fi

