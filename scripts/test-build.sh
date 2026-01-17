#!/bin/bash

# Quick test script for the Enterprise AI Development Platform

echo "🧪 Testing Enterprise AI Development Platform..."

# Test if Docker images exist
echo "📋 Checking Docker images..."
if docker images | grep -q "enterprise-ai-dev-platform-api"; then
    echo "✅ API image built successfully"
else
    echo "❌ API image not found"
    exit 1
fi

if docker images | grep -q "enterprise-ai-dev-platform-dashboard"; then
    echo "✅ Dashboard image built successfully"
else
    echo "❌ Dashboard image not found"
    exit 1
fi

# Test basic container functionality
echo "🐳 Testing container startup..."

# Test API container
echo "  - Testing API container..."
if docker run --rm --entrypoint python enterprise-ai-dev-platform-api -c "import fastapi; print('FastAPI import successful')" > /dev/null 2>&1; then
    echo "✅ API container can import dependencies"
else
    echo "❌ API container dependency test failed"
fi

# Test Dashboard container
echo "  - Testing Dashboard container..."
if docker run --rm --entrypoint npm enterprise-ai-dev-platform-dashboard --version > /dev/null 2>&1; then
    echo "✅ Dashboard container has npm available"
else
    echo "❌ Dashboard container npm test failed"
fi

echo ""
echo "🎉 Build verification complete!"
echo ""
echo "🚀 Ready to deploy with: ./scripts/deploy.sh"
echo ""
echo "📊 Services will be available at:"
echo "   - Dashboard: http://localhost"
echo "   - API: http://localhost/api"
echo "   - Grafana: http://localhost:3001"
echo "   - Prometheus: http://localhost:9090"
