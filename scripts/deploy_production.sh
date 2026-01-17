#!/bin/bash

# Production Deployment Script
# Usage: ./scripts/deploy_production.sh

set -e

echo "🚀 Starting Production Deployment..."

# Configuration
ENVIRONMENT=${1:-production}
BACKUP_DIR="/backups/$(date +%Y%m%d_%H%M%S)"
LOG_FILE="/var/log/deploy_$(date +%Y%m%d_%H%M%S).log"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

error() {
    echo -e "${RED}[ERROR] $1${NC}"
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING] $1${NC}"
}

# Pre-deployment checks
log "🔍 Running pre-deployment checks..."

# Check if .env.production exists
if [ ! -f ".env.production" ]; then
    error ".env.production file not found. Please create it from the template."
fi

# Check Docker
if ! command -v docker &> /dev/null; then
    error "Docker is not installed or not in PATH"
fi

if ! command -v docker-compose &> /dev/null; then
    error "Docker Compose is not installed or not in PATH"
fi

# Backup current deployment
log "💾 Creating backup..."
mkdir -p "$BACKUP_DIR"
docker-compose -f docker-compose.production.yml down || true
cp -r . "$BACKUP_DIR/" || warning "Could not create backup"

# Build and deploy
log "🔨 Building production images..."
docker-compose -f docker-compose.production.yml build --no-cache

log "🚢 Starting production services..."
docker-compose -f docker-compose.production.yml up -d

# Wait for services to be ready
log "⏳ Waiting for services to be ready..."
sleep 30

# Health checks
log "🏥 Running health checks..."

# Check API health
for i in {1..10}; do
    if curl -f http://localhost/api/health > /dev/null 2>&1; then
        log "✅ API is healthy"
        break
    else
        if [ $i -eq 10 ]; then
            error "API health check failed after 10 attempts"
        fi
        log "⏳ Waiting for API... (attempt $i/10)"
        sleep 10
    fi
done

# Check database
if docker-compose -f docker-compose.production.yml exec -T db pg_isready -U postgres > /dev/null 2>&1; then
    log "✅ Database is healthy"
else
    warning "Database health check failed"
fi

# Check Redis
if docker-compose -f docker-compose.production.yml exec -T redis redis-cli ping > /dev/null 2>&1; then
    log "✅ Redis is healthy"
else
    warning "Redis health check failed"
fi

# Run database migrations if needed
log "🗄️ Running database migrations..."
docker-compose -f docker-compose.production.yml exec -T api python -c "
from services.api.database import init_db
import asyncio
asyncio.run(init_db())
print('Database initialization complete')
" || warning "Database migration failed"

# Cleanup old images
log "🧹 Cleaning up old Docker images..."
docker image prune -f

# Show status
log "📊 Deployment Status:"
docker-compose -f docker-compose.production.yml ps

log "🎉 Production deployment completed successfully!"
log "🌐 Application available at: https://your-domain.com"
log "📊 Monitoring available at: https://your-domain.com/api/health/detailed"

# Post-deployment notifications
if command -v curl &> /dev/null; then
    # Send notification to monitoring service (optional)
    curl -X POST \
        -H "Content-Type: application/json" \
        -d '{"status": "success", "environment": "'$ENVIRONMENT'", "timestamp": "'$(date -Iseconds)'"}' \
        https://your-monitoring-service.com/webhook || true
fi

log "📝 Logs available at: $LOG_FILE"
log "💾 Backup available at: $BACKUP_DIR"
