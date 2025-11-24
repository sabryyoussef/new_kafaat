#!/bin/bash
# Complete Docker cleanup and rebuild script with Enterprise Addons
# Run this script with: sudo ./rebuild_docker.sh

set -e

echo "=========================================="
echo "Docker Cleanup and Rebuild Script"
echo "=========================================="
echo ""

cd /home/sabry3/Downloads/kafaat-main

# Step 1: Stop and remove all containers
echo "Step 1: Stopping and removing containers..."
docker-compose down -v --remove-orphans 2>/dev/null || true

# Step 2: Remove any orphaned containers
echo "Step 2: Removing orphaned containers..."
docker ps -a | grep -E "kafaat|odoo" | awk '{print $1}' | xargs -r docker rm -f 2>/dev/null || true

# Step 3: Force remove the problematic container if it exists
echo "Step 3: Force removing problematic container..."
docker rm -f 2ca312b69339b0b4ada54d635414aec581398d14c3458300f6cecfc4ed6277df 2>/dev/null || true

# Step 4: Clean up networks
echo "Step 4: Cleaning up networks..."
docker network prune -f 2>/dev/null || true

# Step 5: Verify docker-compose.yml has enterprise addons
echo "Step 5: Verifying configuration..."
if grep -q "enterprise-addons" docker-compose.yml; then
    echo "✅ Enterprise addons configured in docker-compose.yml"
else
    echo "❌ ERROR: Enterprise addons not found in docker-compose.yml"
    exit 1
fi

# Step 6: Verify enterprise addons directory exists
if [ -d "odoo_enterprise19" ]; then
    echo "✅ Enterprise addons directory exists"
    echo "   Found $(ls -1 odoo_enterprise19 | wc -l) modules"
else
    echo "❌ ERROR: odoo_enterprise19 directory not found"
    exit 1
fi

# Step 7: Rebuild images
echo ""
echo "Step 7: Rebuilding Docker images..."
docker-compose build --no-cache

# Step 8: Start containers
echo ""
echo "Step 8: Starting containers..."
docker-compose up -d

# Step 9: Wait for services to be ready
echo ""
echo "Step 9: Waiting for services to start..."
sleep 10

# Step 10: Verify enterprise addons are mounted
echo ""
echo "Step 10: Verifying enterprise addons are mounted..."
if docker-compose exec -T odoo ls /mnt/enterprise-addons/web_enterprise > /dev/null 2>&1; then
    echo "✅ Enterprise addons are mounted correctly"
else
    echo "❌ WARNING: Enterprise addons may not be mounted"
    echo "   Checking logs..."
    docker-compose logs odoo | grep -i "addons paths" | tail -1
fi

# Step 11: Check container status
echo ""
echo "Step 11: Container status:"
docker-compose ps

# Step 12: Show addons path from logs
echo ""
echo "Step 12: Odoo addons paths:"
docker-compose logs odoo | grep -i "addons paths" | tail -1

echo ""
echo "=========================================="
echo "Rebuild Complete!"
echo "=========================================="
echo ""
echo "Odoo is available at: http://localhost:10019"
echo ""
echo "To install web_enterprise module, run:"
echo "  ./install_module.sh kafaat19 web_enterprise"
echo ""

