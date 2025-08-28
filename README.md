# Nite Putter Pro - Professional Full-Stack Application

[![CI/CD Pipeline](https://github.com/your-org/niteputter/workflows/CI/badge.svg)](https://github.com/your-org/niteputter/actions)
[![Code Coverage](https://codecov.io/gh/your-org/niteputter/branch/main/graph/badge.svg)](https://codecov.io/gh/your-org/niteputter)
[![Security Rating](https://sonarcloud.io/api/project_badges/measure?project=niteputter&metric=security_rating)](https://sonarcloud.io/dashboard?id=niteputter)

## 🏗️ Architecture Overview

Professional full-stack application built with modern technologies and enterprise-grade practices.

### Tech Stack
- **Frontend**: React 19, TypeScript, Tailwind CSS, Vite
- **Backend**: Python 3.12, FastAPI, Pydantic v2
- **Database**: MongoDB 7.0 with Motor (async driver)
- **Cache**: Redis 7
- **Authentication**: JWT with refresh tokens
- **Container**: Docker & Docker Compose
- **CI/CD**: GitHub Actions
- **Monitoring**: Structured logging, health checks

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for local development)
- Python 3.12+ (for local development)

### Production Deployment
```bash
# Clone repository
git clone https://github.com/your-org/niteputter.git
cd niteputter

# Configure environment
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env

# Deploy with Docker Compose
docker-compose up -d

# Initialize database
docker-compose exec backend python scripts/setup_initial_data.py
```

### Local Development
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate
pip install -r requirements.txt
uvicorn server:app --reload --host 0.0.0.0 --port 8000

# Frontend (new terminal)
cd frontend
npm install
npm start
```
