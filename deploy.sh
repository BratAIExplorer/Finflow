#!/usr/bin/env bash
set -e

echo "=========================================="
echo "🚀 Deploying FinFlow on VPS"
echo "=========================================="

# 1. Verify Docker and Docker Compose
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed."
    exit 1
fi

COMPOSE_CMD="docker-compose"
if ! command -v docker-compose &> /dev/null; then
    COMPOSE_CMD="docker compose"
fi

# 2. Ensure environment file exists
if [ ! -f .env ]; then
    echo "⚠️  No .env file found. Generating one from .env.example..."
    cp .env.example .env
    echo "ℹ️  Created .env file. Please review secrets if needed."
fi

# 3. Pull latest changes from git
echo "📥 Pulling latest commits from GitHub..."
git pull origin main

# 4. Build and run containers
echo "🐳 Building and launching containers..."
$COMPOSE_CMD down --remove-orphans
$COMPOSE_CMD up -d --build

# 5. Output running status
echo "📊 Current Container Status:"
$COMPOSE_CMD ps

echo "=========================================="
echo "✅ FinFlow Deployment Complete!"
echo "   Frontend (Light/Dark UI): http://localhost:3000"
echo "   Backend API:              http://localhost:8000"
echo "   Swagger API Docs:         http://localhost:8000/docs"
echo "=========================================="
