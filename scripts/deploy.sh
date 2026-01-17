#!/bin/bash

# Enterprise AI Development Platform - Setup Script
# This script sets up the complete development environment

set -e

echo "🚀 Setting up Enterprise AI Development Platform..."

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p uploads
mkdir -p artifacts
mkdir -p secrets

# Set up environment variables
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please update .env with your actual configuration values"
fi

# Build and start services
echo "🔨 Building Docker images..."
docker-compose -f docker-compose.production.yml build

echo "🗄️  Running database migrations..."
docker-compose -f docker-compose.production.yml run --rm api python -m alembic upgrade head

echo "🚀 Starting services..."
docker-compose -f docker-compose.production.yml up -d

# Wait for services to be ready
echo "⏳ Waiting for services to be ready..."
sleep 30

# Check service health
echo "🔍 Checking service health..."
if curl -f http://localhost/health > /dev/null 2>&1; then
    echo "✅ All services are running correctly!"
else
    echo "❌ Some services may not be ready. Please check the logs:"
    docker-compose -f docker-compose.production.yml logs
fi

# Show service URLs
echo ""
echo "🌐 Service URLs:"
echo "   Dashboard: http://localhost"
echo "   API:       http://localhost/api"
echo "   Grafana:   http://localhost:3001 (admin/admin)"
echo "   Prometheus: http://localhost:9090"

echo ""
echo "🎉 Setup complete! The Enterprise AI Development Platform is now running."
echo ""
echo "📚 Next steps:"
echo "   1. Update .env with your API keys and configuration"
echo "   2. Visit http://localhost to access the dashboard"
echo "   3. Create your first project"
echo "   4. Configure GitHub OAuth for authentication"
echo ""
echo "🛠️  Useful commands:"
echo "   View logs: docker-compose -f docker-compose.production.yml logs -f"
echo "   Stop services: docker-compose -f docker-compose.production.yml down"
echo "   Restart services: docker-compose -f docker-compose.production.yml restart"
