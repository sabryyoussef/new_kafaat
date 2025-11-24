#!/bin/bash

# Odoo 19 Docker Setup Script
# This script helps you start the Odoo 19 Docker environment

echo "=========================================="
echo "Odoo 19 Docker Setup"
echo "=========================================="
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if docker-compose is available
if ! command -v docker-compose &> /dev/null; then
    echo "❌ docker-compose is not installed. Please install it first."
    exit 1
fi

echo "📦 Building Docker images..."
docker-compose build

echo ""
echo "🚀 Starting containers..."
docker-compose up -d

echo ""
echo "⏳ Waiting for services to be ready..."
sleep 5

# Check if containers are running
if docker-compose ps | grep -q "Up"; then
    echo ""
    echo "✅ Odoo 19 is running!"
    echo ""
    echo "🌐 Access Odoo at: http://localhost:10019"
    echo ""
    echo "📊 View logs with: docker-compose logs -f odoo"
    echo "🛑 Stop with: docker-compose down"
    echo ""
else
    echo ""
    echo "❌ Containers failed to start. Check logs with: docker-compose logs"
    exit 1
fi

