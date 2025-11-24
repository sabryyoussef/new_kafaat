#!/bin/bash
# Quick remount as read-write - run with sudo
# Usage: sudo ./QUICK_REMOUNT_RW.sh

echo "Remounting /dev/sdc2 as read-write..."

# Unmount (lazy if busy)
sudo umount /mnt/sabry_backup 2>/dev/null || sudo umount -l /mnt/sabry_backup 2>/dev/null
sleep 2

# Remount with ntfs-3g, force, and rw
sudo mount -t ntfs-3g -o uid=1000,gid=1000,umask=0002,force,rw /dev/sdc2 /mnt/sabry_backup

# Verify
if mount | grep sdc2 | grep -q "rw"; then
    echo "✅ Successfully remounted as read-write!"
    mount | grep sdc2
    echo ""
    echo "Testing write access..."
    if touch /mnt/sabry_backup/.rw_test 2>/dev/null && rm /mnt/sabry_backup/.rw_test 2>/dev/null; then
        echo "✅ Write test passed - drive is writable!"
    else
        echo "❌ Write test failed"
    fi
else
    echo "❌ Still read-only. Check mount output:"
    mount | grep sdc2
fi

