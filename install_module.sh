#!/bin/bash
# Script to install web_enterprise module via Odoo CLI

DB_NAME=${1:-kafaat19}
MODULE_NAME=${2:-web_enterprise}

echo "Installing $MODULE_NAME in database $DB_NAME..."

# Get container name - use docker-compose service name
cd /home/sabry3/Downloads/kafaat-main
CONTAINER=$(docker-compose ps -q odoo 2>/dev/null | head -1)

# If not found, try by name
if [ -z "$CONTAINER" ]; then
    CONTAINER=$(docker ps -q --filter "name=kafaat-main-odoo" | head -1)
fi

# Convert to name if we have an ID
if [ -n "$CONTAINER" ] && [ ${#CONTAINER} -eq 64 ]; then
    CONTAINER_NAME=$(docker ps --format "{{.Names}}" --filter "id=$CONTAINER" | head -1)
    CONTAINER=${CONTAINER_NAME:-$CONTAINER}
fi

if [ -z "$CONTAINER" ]; then
    echo "ERROR: Odoo container not found"
    echo "Available containers:"
    docker ps --format "{{.Names}}"
    exit 1
fi

echo "Using container: $CONTAINER"

# Install module using Odoo CLI with proper database connection
docker exec $CONTAINER odoo \
    -d $DB_NAME \
    -i $MODULE_NAME \
    --stop-after-init \
    --db_host=db \
    --db_user=odoo \
    --db_password=odoo \
    --db_port=5432 \
    --addons-path=/mnt/extra-addons,/mnt/enterprise-addons,/usr/lib/python3/dist-packages/odoo/addons

echo "Installation command executed. Check logs for results."

