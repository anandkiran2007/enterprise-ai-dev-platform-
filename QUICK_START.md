# 🚀 Quick Start Guide

## ✅ Prerequisites
- Docker & Docker Compose installed
- Git installed

## 🛠️ Setup Steps

### 1. GitHub OAuth App (Required for Login)

1. **Create GitHub OAuth App**:
   - Visit: https://github.com/settings/applications/new
   - App name: `Enterprise AI Development Platform`
   - Homepage URL: `http://localhost`
   - Authorization callback URL: `http://localhost/api/auth/github/callback`
   - Enable: Web application flow
   - Disable: Device authorization flow

2. **Get Credentials**:
   - Copy the **Client ID** and **Client Secret** from GitHub

### 2. Environment Configuration

Create `.env` file in project root:
```bash
# GitHub OAuth (replace with your actual credentials)
GITHUB_CLIENT_ID=your_github_client_id_here
GITHUB_CLIENT_SECRET=your_github_client_secret_here

# Optional: OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here

# Optional: Other services
AWS_ACCESS_KEY_ID=your_aws_key
AWS_SECRET_ACCESS_KEY=your_aws_secret
```

### 3. Deploy Platform

```bash
# Clone and navigate
cd enterprise-ai-dev-platform

# Start all services
chmod +x scripts/deploy.sh
./scripts/deploy.sh
```

### 4. Access Services

- **Dashboard**: http://localhost
- **API**: http://localhost/api
- **API Docs**: http://localhost/docs
- **Grafana**: http://localhost:3001 (admin/admin)
- **Prometheus**: http://localhost:9090

### 5. Test OAuth Flow

1. Visit http://localhost
2. Click "Sign in with GitHub"
3. You'll be redirected to GitHub
4. Authorize the application
5. You'll return to the dashboard authenticated

## 🧪 Troubleshooting

### If you see "502 Bad Gateway":
```bash
# Check API logs
docker-compose -f docker-compose.production.yml logs api

# Check API health
curl http://localhost:8000/health

# Restart services
docker-compose -f docker-compose.production.yml restart
```

### If GitHub OAuth doesn't work:
1. Verify `.env` file has correct GitHub credentials
2. Check GitHub OAuth app callback URL matches exactly: `http://localhost/api/auth/github/callback`
3. Ensure GitHub app is configured as a "Web application" not "GitHub App"

### If services won't start:
```bash
# Clean up
docker-compose -f docker-compose.production.yml down -v

# Remove orphaned containers
docker-compose -f docker-compose.production.yml up -d --remove-orphans
```

## 📊 Monitoring

- **System Health**: All services include health checks
- **Metrics**: Prometheus collects from all services
- **Logs**: Use `docker-compose logs [service-name]` to debug

## 🎯 Production Deployment

For production deployment:
1. Update environment variables in production
2. Configure SSL certificates in nginx
3. Set up proper domain names
4. Update GitHub OAuth callback URLs to production domain

---

**🎉 Your Enterprise AI Development Platform is ready to use!**
