# NitePutter Pro E-Commerce Platform

## Production-Ready Golf Training Equipment Store

### Tech Stack
- **Backend**: FastAPI, MongoDB, Redis, Stripe API
- **Frontend**: React 18, TypeScript, Vite, TailwindCSS
- **Infrastructure**: Docker, Nginx, Prometheus, Grafana
- **Security**: JWT, bcrypt, rate limiting, CORS

### Quick Start

#### Backend Setup
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your credentials
uvicorn app.main:app --reload
```

#### Frontend Setup
```bash
cd frontend-v2
npm install
cp .env.example .env.local
npm run dev
```

#### Docker Production
```bash
docker-compose -f docker-compose.production.yml up -d
```

### Features
- Complete product catalog with inventory management
- Secure authentication with JWT tokens
- Shopping cart persistence
- Stripe payment integration
- Order management system
- Email notifications
- Admin dashboard
- Real-time analytics
- Mobile responsive design

### Security
- OWASP compliance
- PCI DSS via Stripe
- GDPR/CCPA ready
- Rate limiting
- Security headers
- Input validation

### Testing
```bash
# Backend tests
cd backend && pytest

# Frontend tests
cd frontend-v2 && npm test
```

### Documentation
- [API Documentation](http://localhost:8000/docs)
- [Testing Guide](../TESTING_GUIDE.md)
- [Security Checklist](../SECURITY_CHECKLIST.md)
- [Legal Compliance](../LEGAL_COMPLIANCE.md)

### License
Copyright 2024 NitePutter Pro. All rights reserved.