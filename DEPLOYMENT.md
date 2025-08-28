# NitePutter Pro - Production Deployment Guide

## Overview

This guide covers the complete deployment process for NitePutter Pro e-commerce platform, including infrastructure setup, security configurations, and monitoring.

## Table of Contents

1. [Infrastructure Requirements](#infrastructure-requirements)
2. [Environment Setup](#environment-setup)
3. [Database Configuration](#database-configuration)
4. [Deployment Process](#deployment-process)
5. [Security Checklist](#security-checklist)
6. [Monitoring & Maintenance](#monitoring--maintenance)
7. [Backup & Recovery](#backup--recovery)
8. [Troubleshooting](#troubleshooting)

## Infrastructure Requirements

### Minimum Production Requirements

- **Server**: 4 vCPUs, 8GB RAM, 100GB SSD
- **Database**: MongoDB Atlas M10 or higher
- **Cache**: Redis Cloud 250MB minimum
- **CDN**: CloudFlare or AWS CloudFront
- **SSL**: Let's Encrypt or commercial certificate

### Recommended Stack

- **Cloud Provider**: AWS, GCP, or Azure
- **Container Orchestration**: Docker Swarm or Kubernetes
- **Load Balancer**: Nginx or HAProxy
- **Monitoring**: Prometheus + Grafana
- **Logging**: ELK Stack or CloudWatch

## Environment Setup

### 1. Clone Repository

```bash
git clone https://github.com/niteputter/niteputter-pro.git
cd niteputter-pro
```

### 2. Configure Environment Variables

Copy and configure production environment:

```bash
cp backend/.env.example backend/.env
# Edit .env with production values
```

### 3. Generate Security Keys

```bash
# Generate SECRET_KEY
openssl rand -hex 32

# Generate SESSION_SECRET_KEY
openssl rand -hex 32
```

### 4. Configure External Services

#### MongoDB Atlas
1. Create production cluster
2. Configure IP whitelist
3. Create database user
4. Get connection string

#### Redis Cloud
1. Create Redis database
2. Configure persistence
3. Get connection credentials

#### Stripe
1. Get production API keys
2. Configure webhook endpoints
3. Set up webhook secret

#### SendGrid
1. Create API key
2. Verify sender domain
3. Configure email templates

#### AWS S3
1. Create S3 bucket
2. Configure CORS policy
3. Create IAM user with S3 access
4. Get access credentials

## Database Configuration

### Initial Setup

```bash
# Connect to MongoDB
mongosh "mongodb+srv://cluster.mongodb.net/niteputter_prod"

# Create indexes
use niteputter_prod
db.products.createIndex({"sku": 1}, {unique: true})
db.products.createIndex({"slug": 1}, {unique: true})
db.users.createIndex({"email": 1}, {unique: true})
db.orders.createIndex({"order_number": 1}, {unique: true})
```

### Seed Production Data

```bash
cd backend
python scripts/seed_all.py
```

## Deployment Process

### Docker Deployment

#### 1. Build Images

```bash
docker-compose build --no-cache
```

#### 2. Start Services

```bash
# Development
docker-compose up -d

# Production (with profiles)
docker-compose --profile production up -d
```

#### 3. Verify Health

```bash
curl http://localhost:8000/monitoring/health
```

### Manual Deployment

#### 1. Install Dependencies

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd ../frontend-v2
npm install
```

#### 2. Build Frontend

```bash
npm run build
```

#### 3. Start Services

```bash
# Backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

# Frontend (served by Nginx)
```

### Kubernetes Deployment

```bash
# Apply configurations
kubectl apply -f k8s/

# Check status
kubectl get pods -n niteputter

# Scale deployment
kubectl scale deployment backend --replicas=3 -n niteputter
```

## Security Checklist

### Pre-Deployment

- [ ] Change all default passwords
- [ ] Generate unique secret keys
- [ ] Configure firewall rules
- [ ] Enable SSL/TLS
- [ ] Set up WAF (Web Application Firewall)
- [ ] Configure rate limiting
- [ ] Enable CORS properly
- [ ] Review security headers

### Post-Deployment

- [ ] Run security scan
- [ ] Test authentication flow
- [ ] Verify payment security
- [ ] Check data encryption
- [ ] Review access logs
- [ ] Set up intrusion detection
- [ ] Configure backup encryption

### Security Headers

Add to Nginx configuration:

```nginx
add_header X-Frame-Options "SAMEORIGIN" always;
add_header X-XSS-Protection "1; mode=block" always;
add_header X-Content-Type-Options "nosniff" always;
add_header Referrer-Policy "no-referrer-when-downgrade" always;
add_header Content-Security-Policy "default-src 'self' http: https: data: blob: 'unsafe-inline'" always;
add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
```

## Monitoring & Maintenance

### Health Checks

```bash
# Basic health check
curl https://api.niteputter.com/monitoring/health

# Detailed status (requires admin auth)
curl -H "Authorization: Bearer $TOKEN" https://api.niteputter.com/monitoring/status

# Metrics
curl -H "Authorization: Bearer $TOKEN" https://api.niteputter.com/monitoring/metrics
```

### Log Management

```bash
# View backend logs
docker-compose logs -f backend

# View error logs
docker-compose exec backend tail -f /app/logs/error.log

# Export logs
docker-compose exec backend cat /app/logs/app.log > backup-logs.txt
```

### Performance Monitoring

1. **Response Time**: Monitor API response times
2. **Error Rate**: Track 4xx and 5xx errors
3. **Database Performance**: Monitor query times
4. **Cache Hit Rate**: Track Redis cache efficiency
5. **Resource Usage**: Monitor CPU, memory, disk

### Alerts Setup

Configure alerts for:
- High error rate (>1%)
- Slow response time (>2s)
- Low disk space (<10%)
- Database connection issues
- Payment failures
- Security events

## Backup & Recovery

### Automated Backups

```bash
# Run backup manually
docker-compose exec backend python scripts/backup_database.py backup --s3

# Schedule daily backup (cron)
0 2 * * * cd /opt/niteputter && docker-compose exec -T backend python scripts/backup_database.py backup --s3 --cleanup
```

### Restore Process

```bash
# List available backups
docker-compose exec backend python scripts/backup_database.py list

# Restore from backup
docker-compose exec backend python scripts/backup_database.py restore \
  --backup-file mongodb_backup_20240101_020000.tar.gz \
  --drop
```

### Disaster Recovery Plan

1. **RPO (Recovery Point Objective)**: 24 hours
2. **RTO (Recovery Time Objective)**: 4 hours
3. **Backup Locations**: Local + S3
4. **Test Frequency**: Monthly
5. **Documentation**: Updated quarterly

## Troubleshooting

### Common Issues

#### Database Connection Failed
```bash
# Check MongoDB status
docker-compose exec mongodb mongosh --eval "db.adminCommand('ping')"

# Verify connection string
echo $MONGODB_URL
```

#### Redis Connection Failed
```bash
# Check Redis status
docker-compose exec redis redis-cli ping

# Test connection
docker-compose exec backend python -c "import redis; r = redis.from_url('$REDIS_URL'); print(r.ping())"
```

#### Payment Processing Issues
```bash
# Check Stripe webhook
curl -X POST https://api.niteputter.com/api/webhooks/stripe \
  -H "Stripe-Signature: $WEBHOOK_SIGNATURE" \
  -d @test-webhook.json
```

#### High Memory Usage
```bash
# Check memory usage
docker stats

# Restart services
docker-compose restart backend
```

### Debug Mode

Enable debug logging:

```python
# backend/.env
APP_DEBUG=true
LOG_LEVEL=DEBUG
```

### Support Contacts

- **Technical Issues**: tech@niteputter.com
- **Security Issues**: security@niteputter.com
- **Emergency**: +1-XXX-XXX-XXXX

## Deployment Checklist

### Pre-Launch

- [ ] All environment variables configured
- [ ] Database migrations completed
- [ ] SSL certificate installed
- [ ] CDN configured
- [ ] Email service verified
- [ ] Payment gateway tested
- [ ] Backup system verified
- [ ] Monitoring alerts configured
- [ ] Security scan completed
- [ ] Load testing performed

### Launch Day

- [ ] Final backup created
- [ ] Deployment executed
- [ ] Health checks passing
- [ ] Smoke tests completed
- [ ] Monitoring active
- [ ] Team notified

### Post-Launch

- [ ] Monitor error rates
- [ ] Check performance metrics
- [ ] Review security logs
- [ ] Verify backups
- [ ] Document issues
- [ ] Plan improvements

## Version History

- **v1.0.0** - Initial production release
- **v1.1.0** - Added Redis caching
- **v1.2.0** - Enhanced security features

## License

Copyright © 2024 NitePutter Pro. All rights reserved.