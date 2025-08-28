# NitePutter Pro - Complete Deployment Guide

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Prerequisites](#prerequisites)
3. [Environment Setup](#environment-setup)
4. [Deployment Methods](#deployment-methods)
5. [SSL Certificate Setup](#ssl-certificate-setup)
6. [Database Setup](#database-setup)
7. [Monitoring Setup](#monitoring-setup)
8. [Backup Configuration](#backup-configuration)
9. [Troubleshooting](#troubleshooting)
10. [Maintenance](#maintenance)

## 🚀 Quick Start

```bash
# Clone repository
git clone https://github.com/niteputter/niteputter-pro.git
cd niteputter-pro

# Set up environment
cp backend/.env.example backend/.env.production
# Edit backend/.env.production with your values

# Deploy to production
chmod +x scripts/deploy.sh
./scripts/deploy.sh production deploy
```

## ✅ Prerequisites

### System Requirements
- Ubuntu 20.04+ or CentOS 8+
- Docker 20.10+
- Docker Compose 2.0+
- Git 2.25+
- 4+ CPU cores
- 8GB+ RAM
- 100GB+ SSD storage

### Required Accounts
- [ ] MongoDB Atlas account (or self-hosted MongoDB)
- [ ] Redis Cloud account (or self-hosted Redis)
- [ ] Stripe account with API keys
- [ ] SendGrid account for emails
- [ ] AWS account for S3 storage
- [ ] Domain name with DNS access

### Installation Commands

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Install required tools
sudo apt install -y git curl wget jq nginx certbot python3-certbot-nginx

# Verify installations
docker --version
docker-compose --version
git --version
```

## 🔧 Environment Setup

### 1. Create Production Environment File

```bash
cd /opt/niteputter
nano backend/.env.production
```

### 2. Required Environment Variables

```env
# Application
APP_NAME="NitePutter Pro"
APP_ENV=production
APP_DEBUG=false
SECRET_KEY=<generate-with-openssl-rand-hex-32>

# MongoDB (Use Atlas for production)
MONGODB_URL=mongodb+srv://username:password@cluster.mongodb.net/
MONGODB_DB_NAME=niteputter_prod
MONGO_ROOT_USERNAME=niteputter
MONGO_ROOT_PASSWORD=<secure-password>

# Redis
REDIS_URL=redis://default:password@redis-endpoint:6379
REDIS_PASSWORD=<secure-password>

# Stripe
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Email (SendGrid)
SENDGRID_API_KEY=SG....
FROM_EMAIL=orders@niteputter.com
SUPPORT_EMAIL=support@niteputter.com

# AWS S3
AWS_ACCESS_KEY_ID=AKIA...
AWS_SECRET_ACCESS_KEY=...
AWS_S3_BUCKET_NAME=niteputter-products
AWS_S3_REGION=us-east-1

# Monitoring
GRAFANA_PASSWORD=<secure-password>
SENTRY_DSN=https://...@sentry.io/...
```

### 3. Generate Secure Keys

```bash
# Generate SECRET_KEY
openssl rand -hex 32

# Generate passwords
openssl rand -base64 32

# Generate MongoDB password
openssl rand -base64 24 | tr -d "=+/" | cut -c1-25
```

## 🚢 Deployment Methods

### Method 1: Automated Deployment Script

```bash
# Make script executable
chmod +x scripts/deploy.sh

# Deploy to production
./scripts/deploy.sh production deploy

# Deploy to staging
./scripts/deploy.sh staging deploy

# Rollback if needed
./scripts/deploy.sh production rollback
```

### Method 2: Docker Compose Production

```bash
# Pull latest code
git pull origin main

# Build images
docker-compose -f docker-compose.production.yml build

# Start services
docker-compose -f docker-compose.production.yml up -d

# Check logs
docker-compose -f docker-compose.production.yml logs -f

# Scale backend
docker-compose -f docker-compose.production.yml up -d --scale backend=3
```

### Method 3: Manual Deployment

```bash
# 1. Build backend
cd backend
docker build -t niteputter/backend:latest .

# 2. Build frontend
cd ../frontend-v2
docker build -t niteputter/frontend:latest .

# 3. Push to registry
docker push niteputter/backend:latest
docker push niteputter/frontend:latest

# 4. Deploy on server
ssh user@server
docker pull niteputter/backend:latest
docker pull niteputter/frontend:latest
docker-compose up -d
```

## 🔒 SSL Certificate Setup

### Using Let's Encrypt

```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Generate certificates
sudo certbot certonly --nginx -d niteputter.com -d www.niteputter.com -d api.niteputter.com

# Auto-renewal
sudo certbot renew --dry-run

# Add to crontab
0 0 * * * /usr/bin/certbot renew --quiet
```

### Manual SSL Setup

```bash
# Create SSL directory
mkdir -p nginx/ssl

# Copy certificates
cp /path/to/niteputter.com.crt nginx/ssl/
cp /path/to/niteputter.com.key nginx/ssl/

# Generate DH parameters
openssl dhparam -out nginx/ssl/dhparam.pem 2048

# Set permissions
chmod 600 nginx/ssl/*.key
chmod 644 nginx/ssl/*.crt
```

## 🗄️ Database Setup

### MongoDB Atlas Setup

1. **Create Cluster**
   ```
   - Choose M10 or higher for production
   - Select region closest to your users
   - Enable backup
   ```

2. **Configure Security**
   ```
   - Add IP whitelist
   - Create database user
   - Enable encryption at rest
   ```

3. **Get Connection String**
   ```
   mongodb+srv://username:password@cluster.mongodb.net/niteputter_prod
   ```

### Self-Hosted MongoDB

```bash
# Create data directory
sudo mkdir -p /data/mongodb

# Run MongoDB container
docker run -d \
  --name mongodb \
  -p 27017:27017 \
  -v /data/mongodb:/data/db \
  -e MONGO_INITDB_ROOT_USERNAME=admin \
  -e MONGO_INITDB_ROOT_PASSWORD=secure_password \
  mongo:7.0 --auth

# Initialize database
docker exec -it mongodb mongosh
use niteputter_prod
db.createUser({
  user: "niteputter",
  pwd: "password",
  roles: [{role: "readWrite", db: "niteputter_prod"}]
})
```

### Database Initialization

```bash
# Connect to production database
docker-compose -f docker-compose.production.yml exec backend bash

# Run seed script
python scripts/seed_all.py

# Verify data
python scripts/check_database.py
```

## 📊 Monitoring Setup

### Grafana Dashboard

1. **Access Grafana**
   ```
   https://grafana.niteputter.com
   Username: admin
   Password: <GRAFANA_PASSWORD>
   ```

2. **Import Dashboards**
   - Go to Dashboards > Import
   - Upload `monitoring/dashboards/*.json`

3. **Configure Alerts**
   ```
   - API response time > 2s
   - Error rate > 1%
   - CPU usage > 80%
   - Memory usage > 90%
   - Disk usage > 85%
   ```

### Prometheus Configuration

```yaml
# monitoring/prometheus.yml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

scrape_configs:
  - job_name: 'backend'
    static_configs:
      - targets: ['backend:8000']
    
  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx:9113']
    
  - job_name: 'redis'
    static_configs:
      - targets: ['redis:9121']
```

### Application Monitoring

```bash
# Check health status
curl https://api.niteputter.com/monitoring/health

# Get metrics (requires auth)
curl -H "Authorization: Bearer $TOKEN" https://api.niteputter.com/monitoring/metrics

# View logs
docker-compose -f docker-compose.production.yml logs -f backend

# Real-time monitoring
watch -n 5 'docker stats --no-stream'
```

## 💾 Backup Configuration

### Automated Backups

```bash
# Create backup script
cat > /opt/scripts/backup.sh << 'EOF'
#!/bin/bash
cd /opt/niteputter
docker-compose -f docker-compose.production.yml exec -T backend \
  python scripts/backup_database.py backup --s3 --cleanup
EOF

chmod +x /opt/scripts/backup.sh

# Add to crontab (daily at 2 AM)
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/scripts/backup.sh") | crontab -
```

### Manual Backup

```bash
# Create backup
docker-compose -f docker-compose.production.yml exec backend \
  python scripts/backup_database.py backup --s3

# List backups
docker-compose -f docker-compose.production.yml exec backend \
  python scripts/backup_database.py list

# Restore from backup
docker-compose -f docker-compose.production.yml exec backend \
  python scripts/backup_database.py restore \
  --backup-file mongodb_backup_20240101_020000.tar.gz
```

## 🔧 Troubleshooting

### Common Issues and Solutions

#### 1. Container Won't Start

```bash
# Check logs
docker-compose -f docker-compose.production.yml logs backend

# Check container status
docker ps -a

# Restart container
docker-compose -f docker-compose.production.yml restart backend
```

#### 2. Database Connection Issues

```bash
# Test MongoDB connection
docker-compose -f docker-compose.production.yml exec backend \
  python -c "from app.database import connect_to_mongodb; import asyncio; asyncio.run(connect_to_mongodb())"

# Check MongoDB logs
docker-compose -f docker-compose.production.yml logs mongodb
```

#### 3. High Memory Usage

```bash
# Check memory usage
docker stats

# Clear Docker cache
docker system prune -a

# Restart services
docker-compose -f docker-compose.production.yml restart
```

#### 4. SSL Certificate Issues

```bash
# Test SSL
openssl s_client -connect niteputter.com:443

# Renew certificate
sudo certbot renew --force-renewal

# Reload Nginx
docker-compose -f docker-compose.production.yml exec nginx nginx -s reload
```

#### 5. Payment Processing Issues

```bash
# Check Stripe webhook
curl -X POST https://api.niteputter.com/api/webhooks/stripe \
  -H "Content-Type: application/json" \
  -H "Stripe-Signature: $WEBHOOK_SECRET" \
  -d @test-webhook.json

# View payment logs
docker-compose -f docker-compose.production.yml exec backend \
  tail -f /app/logs/payment.log
```

## 🛠️ Maintenance

### Daily Tasks

```bash
# Check system health
./scripts/deploy.sh production health

# Review error logs
docker-compose -f docker-compose.production.yml logs --tail=100 backend | grep ERROR

# Monitor disk space
df -h
```

### Weekly Tasks

```bash
# Update dependencies
docker-compose -f docker-compose.production.yml pull

# Clean up Docker resources
docker system prune -f

# Review security logs
grep "Failed login" /app/logs/audit.log

# Test backup restore
# (Do this in staging environment)
```

### Monthly Tasks

```bash
# Security updates
sudo apt update && sudo apt upgrade

# Review and rotate logs
find /var/log -name "*.log" -mtime +30 -delete

# Performance analysis
docker-compose -f docker-compose.production.yml exec backend \
  python scripts/performance_report.py

# Update SSL certificates
sudo certbot renew
```

## 📈 Performance Optimization

### Docker Optimization

```yaml
# Add to docker-compose.production.yml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2.0'
          memory: 2G
        reservations:
          cpus: '1.0'
          memory: 1G
```

### Nginx Caching

```nginx
# Add to nginx.conf
proxy_cache_path /var/cache/nginx levels=1:2 keys_zone=api_cache:10m max_size=1g;

location /api/products {
    proxy_cache api_cache;
    proxy_cache_valid 200 1h;
    proxy_cache_use_stale error timeout updating;
}
```

### Database Indexing

```javascript
// MongoDB indexes
db.products.createIndex({"slug": 1}, {unique: true})
db.products.createIndex({"category": 1, "status": 1})
db.products.createIndex({"name": "text", "description": "text"})
db.orders.createIndex({"customer_email": 1, "created_at": -1})
db.reviews.createIndex({"product_id": 1, "rating": -1})
```

## 📱 Mobile Optimization

```nginx
# Add compression
gzip on;
gzip_types text/plain application/json application/javascript text/css;
gzip_min_length 1000;

# Enable HTTP/2
listen 443 ssl http2;

# Add cache headers
location ~* \.(jpg|jpeg|png|gif|ico|css|js)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

## 🔐 Security Hardening

```bash
# Firewall setup
sudo ufw allow 22/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw enable

# Fail2ban installation
sudo apt install fail2ban
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local
sudo systemctl enable fail2ban
sudo systemctl start fail2ban

# Security audit
docker run --rm -v /var/run/docker.sock:/var/run/docker.sock \
  aquasec/trivy image niteputter/backend:latest
```

## 📞 Support

- **Technical Issues**: tech-support@niteputter.com
- **Security Issues**: security@niteputter.com
- **Emergency Hotline**: +1-XXX-XXX-XXXX
- **Documentation**: https://docs.niteputter.com
- **Status Page**: https://status.niteputter.com

---

© 2024 NitePutter Pro. All rights reserved.