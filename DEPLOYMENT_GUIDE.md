# Nite Putter Pro - Production Deployment & Maintenance Guide

## 📋 Prerequisites

### System Requirements
- **Server**: Ubuntu 22.04 LTS or CentOS 8+ (minimum 4GB RAM, 2 CPU cores)
- **Node.js**: Version 18+ 
- **Python**: Version 3.11+
- **MongoDB**: Version 6.0+
- **Redis**: Version 7.0+ (optional, for caching)
- **Domain**: Registered domain name with SSL certificate
- **Email**: SMTP server for transactional emails

### Development Tools
- **Docker & Docker Compose** (recommended for production)
- **Git** for version control
- **PM2** for process management
- **Nginx** for reverse proxy and SSL

## 🚀 Production Deployment

### 1. Server Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install essential packages
sudo apt install -y git nginx certbot python3-certbot-nginx nodejs npm python3 python3-pip python3-venv

# Install MongoDB
curl -fsSL https://www.mongodb.org/static/pgp/server-6.0.asc | sudo gpg -o /usr/share/keyrings/mongodb-server-6.0.gpg --dearmor
echo "deb [ arch=amd64,arm64 signed-by=/usr/share/keyrings/mongodb-server-6.0.gpg ] https://repo.mongodb.org/apt/ubuntu jammy/mongodb-org/6.0 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-6.0.list
sudo apt update && sudo apt install -y mongodb-org

# Install Redis (optional)
sudo apt install redis-server

# Start services
sudo systemctl start mongod nginx redis-server
sudo systemctl enable mongod nginx redis-server
```

### 2. Environment Configuration

```bash
# Clone repository
git clone https://github.com/your-username/niteputter_version4.git
cd niteputter_version4-main

# Create production environment file
cp backend/.env.example backend/.env.production
```

**Configure `backend/.env.production`:**
```env
# CRITICAL: Update ALL values for production
ENVIRONMENT=production
DEBUG=false

# Generate secure JWT secret: python -c "import secrets; print(secrets.token_urlsafe(64))"
JWT_SECRET=YOUR_SECURE_64_CHARACTER_JWT_SECRET_HERE

# Database (use your production MongoDB connection)
MONGODB_URL=mongodb://localhost:27017/niteputter_prod
DB_NAME=niteputter_prod

# Stripe (LIVE keys for production)
STRIPE_API_KEY=sk_live_YOUR_LIVE_SECRET_KEY
STRIPE_PUBLISHABLE_KEY=pk_live_YOUR_LIVE_PUBLISHABLE_KEY
STRIPE_WEBHOOK_SECRET=whsec_YOUR_LIVE_WEBHOOK_SECRET

# Domain configuration
CORS_ORIGINS=https://your-domain.com
ALLOWED_HOSTS=your-domain.com,www.your-domain.com

# Email configuration
SMTP_HOST=smtp.your-provider.com
SMTP_PORT=587
SMTP_USER=your-email@your-domain.com
SMTP_PASSWORD=your-app-password

# Admin account
SUPER_ADMIN_EMAIL=admin@your-domain.com
SUPER_ADMIN_PASSWORD=SecurePassword123!
```

### 3. Backend Deployment

```bash
# Backend setup
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Database initialization
python scripts/create_super_admin.py
python scripts/setup_content_data.py

# Test backend
uvicorn server:app --host 0.0.0.0 --port 8000

# Install PM2 for process management
npm install -g pm2

# Create PM2 ecosystem file
cat > ecosystem.config.js << 'EOF'
module.exports = {
  apps: [{
    name: 'niteputter-api',
    script: 'uvicorn',
    args: 'server:app --host 0.0.0.0 --port 8000 --workers 4',
    cwd: '/path/to/niteputter_version4-main/backend',
    env: {
      NODE_ENV: 'production',
      ENV_FILE: '.env.production'
    },
    error_file: '/var/log/niteputter-api-error.log',
    out_file: '/var/log/niteputter-api-out.log',
    log_file: '/var/log/niteputter-api.log'
  }]
}
EOF

# Start with PM2
pm2 start ecosystem.config.js
pm2 startup
pm2 save
```

### 4. Frontend Deployment

```bash
cd ../frontend

# Install dependencies
npm install

# Create production build configuration
cat > .env.production << 'EOF'
REACT_APP_BACKEND_URL=https://your-domain.com/api
REACT_APP_STRIPE_PUBLISHABLE_KEY=pk_live_YOUR_LIVE_PUBLISHABLE_KEY
REACT_APP_ENVIRONMENT=production
EOF

# Build for production
npm run build

# Serve with PM2
pm2 serve build 3000 --name niteputter-frontend --spa
```

### 5. Nginx Configuration

```bash
# Create Nginx configuration
sudo tee /etc/nginx/sites-available/niteputter << 'EOF'
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name your-domain.com www.your-domain.com;

    ssl_certificate /etc/letsencrypt/live/your-domain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/your-domain.com/privkey.pem;
    
    # Security headers
    add_header X-Frame-Options DENY;
    add_header X-Content-Type-Options nosniff;
    add_header X-XSS-Protection "1; mode=block";
    add_header Strict-Transport-Security "max-age=63072000; includeSubDomains; preload";

    # Frontend (React app)
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }

    # Backend API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # API rate limiting
        limit_req zone=api burst=20 nodelay;
    }

    # Static files caching
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
        access_log off;
    }
}

# Rate limiting
http {
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/niteputter /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx

# Setup SSL with Let's Encrypt
sudo certbot --nginx -d your-domain.com -d www.your-domain.com
```

## 🔐 Security Configuration

### 1. Firewall Setup
```bash
sudo ufw allow OpenSSH
sudo ufw allow 'Nginx Full'
sudo ufw deny 8000  # Block direct access to backend
sudo ufw deny 3000  # Block direct access to frontend
sudo ufw enable
```

### 2. MongoDB Security
```bash
# Create MongoDB admin user
mongosh
> use admin
> db.createUser({
    user: "admin",
    pwd: "SecureMongoPassword123!",
    roles: ["userAdminAnyDatabase", "dbAdminAnyDatabase", "readWriteAnyDatabase"]
})

# Enable authentication in /etc/mongod.conf
sudo nano /etc/mongod.conf
# Add:
# security:
#   authorization: enabled

sudo systemctl restart mongod
```

### 3. Backup Configuration
```bash
# Create backup script
sudo tee /opt/backup-niteputter.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backup/niteputter"
DATE=$(date +%Y%m%d_%H%M%S)

# Create backup directory
mkdir -p $BACKUP_DIR

# MongoDB backup
mongodump --db niteputter_prod --out $BACKUP_DIR/mongo_$DATE

# Application files backup
tar -czf $BACKUP_DIR/app_$DATE.tar.gz /path/to/niteputter_version4-main

# Clean old backups (keep 30 days)
find $BACKUP_DIR -name "*.tar.gz" -mtime +30 -delete
find $BACKUP_DIR -type d -name "mongo_*" -mtime +30 -exec rm -rf {} \;

echo "Backup completed: $DATE"
EOF

sudo chmod +x /opt/backup-niteputter.sh

# Setup cron job for daily backups
sudo crontab -e
# Add: 0 2 * * * /opt/backup-niteputter.sh >> /var/log/backup.log 2>&1
```

## 📊 Monitoring & Logging

### 1. Application Monitoring
```bash
# Install monitoring tools
npm install -g pm2-logrotate
pm2 install pm2-server-monit

# Setup log rotation
pm2 set pm2-logrotate:max_size 100M
pm2 set pm2-logrotate:compress true
pm2 set pm2-logrotate:retain 30
```

### 2. Health Check Endpoint
Add to your monitoring system:
- **API Health**: `https://your-domain.com/api/` 
- **Database**: Monitor MongoDB connection
- **SSL Certificate**: Check expiry dates

## 🔄 Maintenance Tasks

### Daily
- [ ] Check application logs for errors
- [ ] Monitor server resources (CPU, RAM, Disk)
- [ ] Verify backup completion

### Weekly  
- [ ] Review API error rates and response times
- [ ] Check SSL certificate status
- [ ] Update security patches: `sudo apt update && sudo apt upgrade`

### Monthly
- [ ] Review and analyze user analytics
- [ ] Test backup restoration process
- [ ] Update dependencies: `npm audit` and `pip list --outdated`
- [ ] Review and rotate API keys if needed

### Quarterly
- [ ] Full security audit
- [ ] Performance optimization review
- [ ] Database optimization and indexing review
- [ ] Disaster recovery testing

## 🚨 Troubleshooting

### Common Issues

**503 Service Unavailable**
```bash
# Check PM2 processes
pm2 status
pm2 logs niteputter-api

# Restart services
pm2 restart all
```

**Database Connection Issues**
```bash
# Check MongoDB status
sudo systemctl status mongod
mongosh --eval "db.adminCommand('ismaster')"
```

**SSL Certificate Issues**
```bash
# Renew certificate
sudo certbot renew --dry-run
sudo nginx -t && sudo systemctl reload nginx
```

**High Memory Usage**
```bash
# Monitor processes
htop
pm2 monit

# Restart if needed
pm2 restart all
```

## 📞 Emergency Contacts

- **Domain Registrar**: [Contact Information]
- **Hosting Provider**: [Contact Information] 
- **SSL Certificate**: Let's Encrypt (auto-renewal)
- **Payment Processor**: Stripe Support
- **Developer**: [Your Contact Information]

## 📈 Scaling Considerations

### When to Scale
- CPU usage consistently > 80%
- Memory usage consistently > 80%
- Response times > 2 seconds
- Error rates > 1%

### Scaling Options
1. **Vertical Scaling**: Upgrade server resources
2. **Horizontal Scaling**: Add load balancer and multiple servers
3. **Database Scaling**: MongoDB replica sets or sharding
4. **CDN**: Cloudflare for static assets

---

**Last Updated**: January 2025  
**Version**: 1.0.0

> ⚠️ **CRITICAL**: Always test deployments in a staging environment first. Never deploy directly to production without testing.