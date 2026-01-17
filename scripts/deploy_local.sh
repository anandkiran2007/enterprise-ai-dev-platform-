#!/bin/bash

# Local Production Deployment Script
# For testing without a domain

set -e

echo "🚀 Starting Local Production Deployment..."

# Configuration
DOMAIN="localhost"
BASE_URL="http://localhost"
DASHBOARD_URL="http://localhost"
API_URL="http://localhost"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
    exit 1
}

# Check prerequisites
log "🔍 Checking prerequisites..."

if ! command -v docker &> /dev/null; then
    error "Docker is not installed. Please install Docker first."
fi

if ! command -v docker-compose &> /dev/null; then
    error "Docker Compose is not installed. Please install Docker Compose first."
fi

# Ensure Docker daemon is running (Docker Desktop on macOS)
if ! docker info > /dev/null 2>&1; then
    error "Cannot connect to the Docker daemon. Start Docker Desktop and try again."
fi

COMPOSE_FILE="docker-compose.production.yml"

# Create production environment
log "📝 Setting up production environment..."

# Copy from .env.production if it exists
if [ -f ".env.production" ]; then
    cp .env.production .env
    log "✅ Copied .env.production to .env"
fi

# Update URLs for local deployment
sed -i '' 's|BASE_URL=https://your-domain.com|BASE_URL=http://localhost|g' .env
sed -i '' 's|DASHBOARD_URL=https://your-domain.com|DASHBOARD_URL=http://localhost|g' .env

# Create logs directory
mkdir -p logs

# Update GitHub OAuth app for local testing
log "🔧 GitHub OAuth Setup Instructions:"
echo ""
echo "1. Go to: https://github.com/settings/applications/new"
echo "2. Application name: Enterprise AI Platform (Local)"
echo "3. Homepage URL: ${DASHBOARD_URL}"
echo "4. Authorization callback URL: ${API_URL}/api/auth/github/callback"
echo "5. Update your GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET in .env"
echo ""

# Deploy services
log "🐳 Deploying services..."

# Stop existing services
docker-compose -f "$COMPOSE_FILE" down || true

# Start database and redis first
log "🗄️ Starting database and Redis..."
docker-compose -f "$COMPOSE_FILE" up -d db redis

# Wait for database
log "⏳ Waiting for database..."
sleep 10

# Start API
log "🚀 Starting API service..."
docker-compose -f "$COMPOSE_FILE" up -d api

# Wait for API
log "⏳ Waiting for API..."
sleep 5

# Start dashboard
log "🎨 Starting dashboard..."
docker-compose -f "$COMPOSE_FILE" up -d dashboard

# Start Nginx
log "🌐 Starting Nginx proxy..."
docker-compose -f "$COMPOSE_FILE" up -d nginx

# Health checks
log "🏥 Running health checks..."

# Check API health
for i in {1..10}; do
    if curl -f ${API_URL}/api/health > /dev/null 2>&1; then
        log "✅ API is healthy"
        break
    else
        if [ $i -eq 10 ]; then
            error "API health check failed"
        fi
        log "⏳ Waiting for API... (attempt $i/10)"
        sleep 5
    fi
done

# Check dashboard
for i in {1..10}; do
    if curl -f ${DASHBOARD_URL} > /dev/null 2>&1; then
        log "✅ Dashboard is healthy"
        break
    else
        if [ $i -eq 10 ]; then
            error "Dashboard health check failed"
        fi
        log "⏳ Waiting for dashboard... (attempt $i/10)"
        sleep 5
    fi
done

# Show status
log "📊 Deployment Status:"
docker-compose -f "$COMPOSE_FILE" ps

# Show URLs
echo ""
log "🎉 Local Production Deployment Complete!"
echo ""
echo "🌐 Available URLs:"
echo "   App (Nginx): http://localhost"
echo "   Health:     http://localhost/api/health"
echo ""
echo "📋 Next Steps:"
echo "   1. Update GitHub OAuth app callback URL: http://localhost/api/auth/github/callback"
echo "   2. Visit: http://localhost"
echo "   3. Test OAuth flow"
echo ""
warning "⚠️  This is for local testing only. For real production:"
echo "   - Get a domain name"
echo "   - Set up SSL certificates"
echo "   - Use ./scripts/deploy_production.sh for real deployment"

# Start monitoring
log "📊 Starting monitoring..."
docker-compose -f "$COMPOSE_FILE" logs -f --tail=100
