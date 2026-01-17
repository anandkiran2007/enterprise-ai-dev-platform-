# Production Deployment Guide

## 🚀 Production-Ready Setup

This guide covers deploying the Enterprise AI Development Platform to production with enterprise-grade reliability, security, and monitoring.

## 📋 Prerequisites

### Infrastructure
- **Docker & Docker Compose** v20.10+
- **PostgreSQL** 14+ with pgvector extension
- **Redis** 6+ for caching and sessions
- **Nginx** 1.20+ for reverse proxy
- **SSL Certificate** for HTTPS (Let's Encrypt or commercial)

### Security Requirements
- **GitHub OAuth App** registered with proper callbacks
- **Strong secrets** (32+ character keys)
- **Environment isolation** (separate .env files)
- **Network security** (VPC, firewall rules)

## 🔧 Configuration

### 1. Environment Setup

```bash
# Copy production environment template
cp .env.production .env

# Edit with your production values
nano .env
```

### 2. Required Environment Variables

| Variable | Required | Description |
|-----------|-----------|-------------|
| `SECRET_KEY` | ✅ | 32+ character JWT secret |
| `GITHUB_CLIENT_ID` | ✅ | GitHub OAuth App ID |
| `GITHUB_CLIENT_SECRET` | ✅ | GitHub OAuth App Secret |
| `DATABASE_URL` | ✅ | PostgreSQL connection string |
| `REDIS_URL` | ✅ | Redis connection string |
| `BASE_URL` | ✅ | Your domain (https://your-domain.com) |
| `DASHBOARD_URL` | ✅ | Frontend URL |

### 3. Security Configuration

```bash
# Generate strong secrets
openssl rand -base64 32  # For SECRET_KEY
openssl rand -base64 40  # For additional secrets

# Set proper file permissions
chmod 600 .env
chown appuser:appuser .env  # In production
```

## 🚀 Deployment Methods

### Method 1: Automated Deployment (Recommended)

```bash
# Deploy with health checks and monitoring
./scripts/deploy_production.sh production
```

### Method 2: Manual Docker Compose

```bash
# Build production images
docker-compose -f docker-compose.production.yml build --no-cache

# Start services
docker-compose -f docker-compose.production.yml up -d

# Check status
docker-compose -f docker-compose.production.yml ps
```

### Method 3: Kubernetes

```bash
# Apply Kubernetes manifests
kubectl apply -f k8s/
```

## 🔍 Health Monitoring

### Health Endpoints

- **Basic**: `GET /api/health`
- **Detailed**: `GET /api/health/detailed`
- **Service Status**: `GET /api/health/detailed`

### Monitoring Setup

```bash
# Check all services
curl https://your-domain.com/api/health/detailed

# Monitor logs
docker-compose -f docker-compose.production.yml logs -f api

# Check resource usage
docker stats
```

## 🛡️ Security Hardening

### 1. Network Security

```bash
# Use HTTPS only (Nginx configuration)
server {
    listen 443 ssl http2;
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains";
    add_header X-Frame-Options "DENY";
    add_header X-Content-Type-Options "nosniff";
}
```

### 2. Application Security

- **Rate Limiting**: 100 requests/minute per IP
- **Input Validation**: All user inputs validated
- **Error Handling**: No sensitive data leaked in errors
- **CORS**: Restricted to your domain only
- **JWT Tokens**: Proper expiration and validation

### 3. Database Security

```sql
-- Create dedicated database user
CREATE USER app_user WITH PASSWORD 'strong_password';
GRANT CONNECT ON DATABASE enterprise_ai_prod TO app_user;

-- Enable row-level security
ALTER TABLE projects ENABLE ROW LEVEL SECURITY;
```

## 📊 Performance Optimization

### 1. Caching Strategy

- **Redis Caching**: User sessions, GitHub API responses
- **Application Cache**: 5-minute TTL for auth data
- **Database Pooling**: Connection pooling configured
- **Static Assets**: CDN for frontend assets

### 2. Scaling Configuration

```yaml
# docker-compose.production.yml
services:
  api:
    deploy:
      replicas: 3  # Horizontal scaling
    environment:
      - WORKERS=4  # Process scaling
    resources:
      limits:
        cpus: '2'
        memory: 4G
      reservations:
        cpus: '1'
        memory: 2G
```

## 🔧 Troubleshooting

### Common Issues & Solutions

#### 500 Errors
```bash
# Check application logs
docker-compose logs -f api --tail=100

# Check health status
curl https://your-domain.com/api/health/detailed

# Restart services
docker-compose -f docker-compose.production.yml restart api
```

#### Database Connection Issues
```bash
# Test database connection
docker-compose exec db psql -U postgres -d enterprise_ai_prod -c "SELECT 1;"

# Check database logs
docker-compose logs -f db
```

#### GitHub OAuth Issues
```bash
# Verify OAuth app configuration
curl -H "Authorization: token YOUR_ACCESS_TOKEN" \
     https://api.github.com/applications/YOUR_CLIENT_ID

# Check rate limits
curl -H "Authorization: token YOUR_ACCESS_TOKEN" \
     https://api.github.com/rate_limit
```

## 📈 Monitoring & Alerting

### 1. Application Metrics

```bash
# Enable detailed logging
export LOG_LEVEL=INFO

# Monitor response times
curl -w "@curl-format.txt" https://your-domain.com/api/health
```

### 2. Infrastructure Monitoring

- **Prometheus**: Metrics collection on port 9090
- **Grafana**: Visualization on port 3001
- **Log Aggregation**: Centralized log management
- **Alerting**: Email/Slack notifications

### 3. Health Check Automation

```bash
# Add to crontab for continuous monitoring
*/5 * * * * curl -f https://your-domain.com/api/health || \
    mail -s "Health Check Failed" admin@your-domain.com
```

## 🔄 CI/CD Integration

### GitHub Actions Example

```yaml
name: Deploy Production
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to Production
        run: |
          ./scripts/deploy_production.sh production
```

## 📋 Production Checklist

### Pre-Deployment
- [ ] Environment variables configured
- [ ] SSL certificates installed
- [ ] Database backups enabled
- [ ] Monitoring configured
- [ ] Security headers set
- [ ] Rate limits configured
- [ ] Error logging enabled

### Post-Deployment
- [ ] Health checks passing
- [ ] OAuth flow tested
- [ ] Database connectivity verified
- [ ] Monitoring alerts configured
- [ ] Backup procedures tested
- [ ] Performance benchmarks recorded

## 🆘 Rollback Procedures

```bash
# Quick rollback to previous version
git checkout HEAD~1
./scripts/deploy_production.sh production

# Database rollback (if needed)
docker-compose exec db psql -U postgres -d enterprise_ai_prod < backup.sql
```

## 📞 Support

### Emergency Contacts
- **DevOps**: devops@your-domain.com
- **Security**: security@your-domain.com
- **On-Call**: +1-555-DEV-OPS

### Escalation Procedures
1. **Level 1**: Check health endpoints and logs
2. **Level 2**: Restart affected services
3. **Level 3**: Rollback to previous version
4. **Level 4**: Engage on-call engineering team

---

## 🎯 Production Best Practices

1. **Never commit `.env` files** to version control
2. **Use separate secrets management** (HashiCorp Vault, AWS Secrets Manager)
3. **Implement gradual rollouts** (blue-green deployment)
4. **Monitor everything** (logs, metrics, traces)
5. **Test disaster recovery** procedures regularly
6. **Keep dependencies updated** for security patches
7. **Document everything** for team knowledge sharing

This production setup ensures enterprise-grade reliability, security, and maintainability for the AI Development Platform.
