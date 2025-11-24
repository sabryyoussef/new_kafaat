#!/bin/bash
# Script to mount external HDD (sabry_backup)
# Run with: sudo ./mount_external_hdd.sh

set -e

# Auto-detect the device by label
MOUNT_POINT="/mnt/sabry_backup"
LABEL="sabry_backup"

# Try to find device by label
DEVICE=$(sudo blkid -L "$LABEL" 2>/dev/null || echo "")

# If not found by label, try common device names
if [ -z "$DEVICE" ]; then
    for dev in /dev/sdc2 /dev/sdb2 /dev/sdd2; do
        if [ -b "$dev" ]; then
            DEV_LABEL=$(sudo blkid -s LABEL -o value "$dev" 2>/dev/null)
            if [ "$DEV_LABEL" = "$LABEL" ] || [ -n "$DEV_LABEL" ]; then
                DEVICE="$dev"
                break
            fi
        fi
    done
fi

# Fallback to sdc2 if nothing found
if [ -z "$DEVICE" ] && [ -b "/dev/sdc2" ]; then
    DEVICE="/dev/sdc2"
fi

echo "=========================================="
echo "Mounting External HDD"
echo "=========================================="
echo ""

# Check if device exists
if [ ! -b "$DEVICE" ]; then
    echo "❌ ERROR: Device $DEVICE not found"
    echo "Available block devices:"
    lsblk -o NAME,SIZE,TYPE,MOUNTPOINT | grep disk
    exit 1
fi

echo "✅ Device found: $DEVICE"

# Check if already mounted
if mountpoint -q "$MOUNT_POINT" 2>/dev/null; then
    echo "✅ External HDD is already mounted at $MOUNT_POINT"
    df -h | grep "$DEVICE"
    exit 0
fi

# Create mount point if it doesn't exist
if [ ! -d "$MOUNT_POINT" ]; then
    echo "Creating mount point: $MOUNT_POINT"
    mkdir -p "$MOUNT_POINT"
fi

# Check filesystem type
FS_TYPE=$(sudo blkid -s TYPE -o value "$DEVICE" 2>/dev/null || echo "ntfs")
echo "Filesystem type: $FS_TYPE"

# Mount the device
echo "Mounting $DEVICE to $MOUNT_POINT..."

if [ "$FS_TYPE" = "ntfs" ] || [ "$FS_TYPE" = "ntfs-3g" ]; then
    # Check if volume is dirty (needs force mount)
    VOLUME_DIRTY=$(dmesg 2>/dev/null | grep -i "dirty" | grep "$(basename $DEVICE)" | tail -1 || echo "")
    
    MOUNT_OPTS="uid=$(id -u),gid=$(id -g),umask=0002"
    
    # Add force option if volume is dirty
    if [ -n "$VOLUME_DIRTY" ]; then
        echo "⚠️  WARNING: Volume is marked as dirty. Using force mount option."
        MOUNT_OPTS="$MOUNT_OPTS,force"
    fi
    
    # Try ntfs-3g first (better support)
    if command -v ntfs-3g >/dev/null 2>&1; then
        sudo mount -t ntfs-3g -o "$MOUNT_OPTS" "$DEVICE" "$MOUNT_POINT"
    else
        # Try using kernel ntfs3 driver with force option
        sudo mount -t ntfs3 -o "$MOUNT_OPTS" "$DEVICE" "$MOUNT_POINT" 2>/dev/null || \
        sudo mount -t ntfs -o "$MOUNT_OPTS" "$DEVICE" "$MOUNT_POINT"
    fi
else
    # For other filesystems (ext4, etc.)
    sudo mount "$DEVICE" "$MOUNT_POINT"
fi

# Verify mount
if mountpoint -q "$MOUNT_POINT"; then
    echo ""
    echo "✅ External HDD mounted successfully!"
    echo ""
    echo "Mount point: $MOUNT_POINT"
    echo ""
    echo "Disk usage:"
    df -h | grep "$DEVICE"
    echo ""
    echo "Contents:"
    ls -lh "$MOUNT_POINT" | head -10
    echo ""
    echo "To unmount later, run:"
    echo "  sudo umount $MOUNT_POINT"
else
    echo "❌ ERROR: Failed to mount $DEVICE"
    exit 1
fi

