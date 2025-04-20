---
sidebar_position: 2
---

# Docker Deployment

This guide explains how to deploy AzureShield IAM using Docker Compose for a streamlined setup.

## Prerequisites

- Docker and Docker Compose installed
- Git (to clone the repository)

## Deployment Steps

### 1. Clone the Repository

```bash
git clone https://github.com/yourusername/azure-shield-iam.git
cd azure-shield-iam
```

### 2. Configure Environment Variables

```bash
cp .env.example .env
```

Edit the `.env` file to update the following variables:

```
# Use internal Docker network hostnames for services
DATABASE_URL=postgresql://postgres:postgres@db:5432/azureshield_iam
REDIS_URL=redis://redis:6379/0

# Security settings (change these for production)
SECRET_KEY=your_strong_secret_key_here

# SMTP settings
SMTP_HOST=your-smtp-server
SMTP_USER=your-smtp-user
SMTP_PASSWORD=your-smtp-password
EMAILS_FROM_EMAIL=noreply@yourdomain.com
EMAILS_FROM_NAME=AzureShield
```

### 3. Fix Dockerfiles (if needed)

If you encounter build issues related to COPY commands, you may need to edit the Dockerfiles:

1. Edit `docker/backend/Dockerfile`:
   ```dockerfile
   # Change these lines
   COPY requirements.txt .
   # ...
   COPY . .
   ```

2. Edit `docker/frontend/Dockerfile`:
   ```dockerfile
   # Change these lines
   COPY package*.json ./
   # ...
   COPY . .
   ```

### 4. Start the Services

```bash
docker-compose up -d
```

This will:
- Build and start the PostgreSQL database
- Build and start the Redis cache
- Build and start the API server
- Build and start the frontend application
- Start Prometheus for metrics collection
- Start Grafana for monitoring

### 5. Run Database Migrations

Once all services are running, execute the database migrations:

```bash
docker-compose exec api alembic upgrade head
```

### 6. Access the Application

- Frontend interface: http://localhost:3000
- API endpoints: http://localhost:8000
- API documentation: http://localhost:8000/docs
- Grafana dashboard: http://localhost:3001 (login with admin/admin)
- Prometheus metrics: http://localhost:9090

## Troubleshooting

### Container Startup Issues

If containers fail to start:

1. Check logs for each service:
   ```bash
   docker-compose logs api
   docker-compose logs frontend
   docker-compose logs db
   ```

2. Verify network connectivity between containers:
   ```bash
   docker-compose exec api ping db
   docker-compose exec api ping redis
   ```

### Port Conflicts

If you have services already using the required ports:

1. Edit `docker-compose.yml` to change the port mappings:
   ```yaml
   api:
     ports:
       - "8001:8000"  # Change 8000 to 8001
   
   frontend:
     ports:
       - "3001:3000"  # Change 3000 to 3001
   
   redis:
     ports:
       - "6380:6379"  # Change 6379 to 6380
   ```

2. Update related environment variables accordingly

### Permission Issues

If you encounter permission issues with mounted volumes:

```bash
# Stop all containers
docker-compose down

# Remove volumes (be careful - this deletes data)
docker-compose down -v

# Rebuild and start containers
docker-compose up -d --build
```

## Updating

To update your deployment to the latest version:

```bash
git pull
docker-compose down
docker-compose up -d --build
docker-compose exec api alembic upgrade head
``` 