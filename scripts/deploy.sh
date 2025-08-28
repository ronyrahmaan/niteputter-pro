#!/bin/bash

# NitePutter Pro Production Deployment Script
# This script handles the complete deployment process

set -e  # Exit on error

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
DEPLOY_ENV=${1:-production}
DEPLOY_DIR="/opt/niteputter"
BACKUP_DIR="/backup/niteputter"
LOG_FILE="/var/log/niteputter-deploy.log"
HEALTH_CHECK_URL="https://api.niteputter.com/health"
SLACK_WEBHOOK=${SLACK_WEBHOOK_URL}

# Logging function
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a $LOG_FILE
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a $LOG_FILE
    exit 1
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1" | tee -a $LOG_FILE
}

# Send notification to Slack
notify_slack() {
    local message=$1
    local status=${2:-"info"}
    
    if [ ! -z "$SLACK_WEBHOOK" ]; then
        curl -X POST -H 'Content-type: application/json' \
            --data "{\"text\":\"${message}\", \"username\":\"Deploy Bot\", \"icon_emoji\":\":rocket:\"}" \
            $SLACK_WEBHOOK 2>/dev/null
    fi
}

# Check prerequisites
check_prerequisites() {
    log "Checking prerequisites..."
    
    # Check if running as appropriate user
    if [ "$EUID" -eq 0 ]; then
        warning "Running as root. Consider using a dedicated deploy user."
    fi
    
    # Check required tools
    for cmd in docker docker-compose git curl jq; do
        if ! command -v $cmd &> /dev/null; then
            error "$cmd is not installed"
        fi
    done
    
    # Check Docker daemon
    if ! docker info &> /dev/null; then
        error "Docker daemon is not running"
    fi
    
    # Check disk space
    available_space=$(df $DEPLOY_DIR | awk 'NR==2 {print $4}')
    if [ $available_space -lt 5000000 ]; then  # Less than 5GB
        error "Insufficient disk space. At least 5GB required."
    fi
    
    log "Prerequisites check completed"
}

# Pull latest code
pull_latest_code() {
    log "Pulling latest code from repository..."
    
    cd $DEPLOY_DIR
    
    # Stash any local changes
    git stash
    
    # Fetch latest changes
    git fetch origin
    
    # Checkout appropriate branch
    if [ "$DEPLOY_ENV" = "production" ]; then
        git checkout main
        git pull origin main
    else
        git checkout develop
        git pull origin develop
    fi
    
    # Record current commit
    CURRENT_COMMIT=$(git rev-parse HEAD)
    log "Deployed commit: $CURRENT_COMMIT"
}

# Validate environment files
validate_environment() {
    log "Validating environment configuration..."
    
    # Check for required environment files
    if [ ! -f "$DEPLOY_DIR/backend/.env.${DEPLOY_ENV}" ]; then
        error "Environment file backend/.env.${DEPLOY_ENV} not found"
    fi
    
    # Validate required environment variables
    source "$DEPLOY_DIR/backend/.env.${DEPLOY_ENV}"
    
    required_vars=(
        "MONGODB_URL"
        "REDIS_URL"
        "SECRET_KEY"
        "STRIPE_SECRET_KEY"
        "STRIPE_PUBLISHABLE_KEY"
    )
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            error "Required environment variable $var is not set"
        fi
    done
    
    log "Environment validation completed"
}

# Build Docker images
build_images() {
    log "Building Docker images..."
    
    cd $DEPLOY_DIR
    
    # Build with production configuration
    docker-compose -f docker-compose.production.yml build --no-cache
    
    # Tag images with version
    docker tag niteputter/backend:latest niteputter/backend:$CURRENT_COMMIT
    docker tag niteputter/frontend:latest niteputter/frontend:$CURRENT_COMMIT
    
    log "Docker images built successfully"
}

# Database backup
backup_database() {
    log "Creating database backup..."
    
    # Create backup directory
    mkdir -p $BACKUP_DIR
    
    # Run backup script in container
    docker-compose -f docker-compose.production.yml exec -T backend \
        python scripts/backup_database.py backup --s3 --cleanup
    
    if [ $? -eq 0 ]; then
        log "Database backup completed successfully"
    else
        error "Database backup failed"
    fi
}

# Run database migrations
run_migrations() {
    log "Running database migrations..."
    
    # Run migration script if exists
    if [ -f "$DEPLOY_DIR/backend/scripts/migrate.py" ]; then
        docker-compose -f docker-compose.production.yml exec -T backend \
            python scripts/migrate.py
    fi
    
    log "Migrations completed"
}

# Deploy with zero downtime
deploy_zero_downtime() {
    log "Starting zero-downtime deployment..."
    
    cd $DEPLOY_DIR
    
    # Start new containers alongside old ones
    docker-compose -f docker-compose.production.yml up -d --no-deps --scale backend=2 backend
    
    # Wait for new containers to be healthy
    sleep 30
    
    # Check health of new containers
    for i in {1..10}; do
        if docker-compose -f docker-compose.production.yml exec -T backend \
            curl -f http://localhost:8000/monitoring/health &>/dev/null; then
            log "New backend containers are healthy"
            break
        fi
        
        if [ $i -eq 10 ]; then
            error "New containers failed health check"
        fi
        
        sleep 5
    done
    
    # Update frontend
    docker-compose -f docker-compose.production.yml up -d --no-deps frontend
    
    # Scale back to single backend instance
    docker-compose -f docker-compose.production.yml up -d --no-deps --scale backend=1 backend
    
    # Update other services
    docker-compose -f docker-compose.production.yml up -d redis celery-worker celery-beat
    
    log "Zero-downtime deployment completed"
}

# Standard deployment
deploy_standard() {
    log "Starting standard deployment..."
    
    cd $DEPLOY_DIR
    
    # Stop existing containers
    docker-compose -f docker-compose.production.yml down
    
    # Start new containers
    docker-compose -f docker-compose.production.yml up -d
    
    log "Standard deployment completed"
}

# Health checks
run_health_checks() {
    log "Running health checks..."
    
    # Wait for services to start
    sleep 20
    
    # Check backend health
    if ! curl -f $HEALTH_CHECK_URL &>/dev/null; then
        error "Backend health check failed"
    fi
    
    # Check frontend
    if ! curl -f https://niteputter.com &>/dev/null; then
        warning "Frontend health check failed"
    fi
    
    # Check database connectivity
    docker-compose -f docker-compose.production.yml exec -T backend \
        python -c "from app.database import connect_to_mongodb; import asyncio; asyncio.run(connect_to_mongodb())"
    
    if [ $? -ne 0 ]; then
        error "Database connectivity check failed"
    fi
    
    log "All health checks passed"
}

# Run smoke tests
run_smoke_tests() {
    log "Running smoke tests..."
    
    # Test API endpoints
    endpoints=(
        "/api/products"
        "/api/auth/status"
        "/monitoring/health"
    )
    
    for endpoint in "${endpoints[@]}"; do
        response=$(curl -s -o /dev/null -w "%{http_code}" https://api.niteputter.com$endpoint)
        if [ $response -ne 200 ] && [ $response -ne 401 ]; then
            warning "Endpoint $endpoint returned status $response"
        fi
    done
    
    log "Smoke tests completed"
}

# Cleanup old images
cleanup() {
    log "Cleaning up old Docker resources..."
    
    # Remove unused images
    docker image prune -f
    
    # Remove unused volumes
    docker volume prune -f
    
    # Remove old tagged images (keep last 5)
    docker images | grep niteputter | tail -n +6 | awk '{print $3}' | xargs -r docker rmi -f
    
    log "Cleanup completed"
}

# Rollback deployment
rollback() {
    log "Starting rollback..."
    
    cd $DEPLOY_DIR
    
    # Checkout previous commit
    git checkout HEAD~1
    
    # Rebuild and deploy
    build_images
    deploy_standard
    
    log "Rollback completed"
}

# Main deployment flow
main() {
    log "=========================================="
    log "NitePutter Pro Deployment Started"
    log "Environment: $DEPLOY_ENV"
    log "=========================================="
    
    notify_slack "Deployment started for $DEPLOY_ENV environment"
    
    # Pre-deployment checks
    check_prerequisites
    validate_environment
    
    # Backup current state
    backup_database
    
    # Pull and build
    pull_latest_code
    build_images
    
    # Run migrations
    run_migrations
    
    # Deploy based on environment
    if [ "$DEPLOY_ENV" = "production" ]; then
        deploy_zero_downtime
    else
        deploy_standard
    fi
    
    # Post-deployment
    run_health_checks
    run_smoke_tests
    cleanup
    
    log "=========================================="
    log "Deployment completed successfully!"
    log "=========================================="
    
    notify_slack "✅ Deployment completed successfully for $DEPLOY_ENV"
}

# Handle script arguments
case "${2:-deploy}" in
    deploy)
        main
        ;;
    rollback)
        rollback
        ;;
    backup)
        backup_database
        ;;
    health)
        run_health_checks
        ;;
    *)
        echo "Usage: $0 [production|staging] [deploy|rollback|backup|health]"
        exit 1
        ;;
esac