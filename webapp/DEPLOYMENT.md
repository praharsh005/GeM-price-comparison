# Deployment Guide

## Quick Start (Docker Compose)

```bash
# Start all services
docker compose up -d

# Check status
docker compose ps

# View logs
docker compose logs -f backend
```

## Production Deployment (Render)

### Prerequisites
1. Render account
2. GitHub repository connected to Render

### Backend Service
1. Create new **Web Service** on Render
2. Connect repository
3. Configure:
   - **Runtime**: Docker
   - **Dockerfile**: `./backend/Dockerfile`
   - **Context**: `./backend`
   - **Port**: 8000
   - **Health Check**: `/health`

### Environment Variables (Backend)
| Variable | Value |
|----------|-------|
| `DATABASE_URL` | From Render PostgreSQL (auto-injected) |
| `REDIS_URL` | From Render Redis (auto-injected) |
| `SECRET_KEY` | Auto-generated |
| `ALGORITHM` | `HS256` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` |
| `SCRAPER_RATE_LIMIT` | `2.0` |
| `SCRAPER_MAX_PAGES` | `15` |

### Frontend Service
1. Create new **Web Service** on Render
2. Configure:
   - **Runtime**: Docker
   - **Dockerfile**: `./frontend/Dockerfile`
   - **Context**: `./frontend`
   - **Port**: 80 (nginx)

### Environment Variables (Frontend)
| Variable | Value |
|----------|-------|
| `VITE_API_BASE_URL` | `https://your-backend.onrender.com` |

### Databases
1. Create **PostgreSQL** database: `gem-postgres`
   - Plan: Starter
   - Database: `gem_price`
   - User: `gem`

2. Create **Redis** instance: `gem-redis`
   - Plan: Starter

### Using Blueprint (Recommended)
```bash
render blueprint apply render.yaml
```

## Local Development

```bash
# Start services
docker compose up -d

# Backend only
cd backend
python -m app.seed  # Seed database
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Frontend
cd frontend
npm install
npm run dev
```

## Mobile App Build

```bash
cd mobile
npm install
npx expo prebuild --platform android
cd android
./gradlew assembleRelease

# Output: android/app/build/outputs/apk/release/app-release.apk
```

## Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "description"

# Apply migrations
alembic upgrade head

# Downgrade
alembic downgrade -1
```

## Health Checks

```bash
# Backend
curl http://localhost:8000/health
# {"status": "ok"}

# Database
curl http://localhost:8000/categories

# Frontend
curl http://localhost:5173
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| DB connection failed | Check DATABASE_URL, ensure DB is running |
| Migrations fail | Check alembic version, manually run if needed |
| Scraper blocked | Increase SCRAPER_RATE_LIMIT, check robots.txt |
| Mobile can't connect | Check API_BASE_URL, use 10.0.2.2 for emulator |
| Render build fails | Check Dockerfile, ensure requirements.txt complete |

## Monitoring

```bash
# View logs
docker compose logs -f backend
docker compose logs -f frontend

# Render logs
render logs -s gem-price-backend
render logs -s gem-price-frontend
```

## Rollback

```bash
# Database rollback
alembic downgrade -1

# Docker rollback
docker compose down
docker compose up -d  # Uses previous image
```