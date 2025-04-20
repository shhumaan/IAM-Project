---
sidebar_position: 1
---

# Local Development Setup

This guide will walk you through setting up AzureShield IAM for local development.

## Clone the Repository

First, clone the repository and navigate to the project folder:

```bash
git clone https://github.com/yourusername/azure-shield-iam.git
cd azure-shield-iam
```

## Environment Setup

1. Copy the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Open the `.env` file and update the following variables:
   ```
   # Database settings
   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/azureshield_iam
   POSTGRES_SERVER=localhost
   POSTGRES_USER=postgres
   POSTGRES_PASSWORD=postgres
   POSTGRES_DB=azureshield_iam
   
   # Security settings (change these for production)
   SECRET_KEY=your_secret_key_here_change_this_in_production
   
   # SMTP settings for email functionality
   SMTP_HOST=mailhog
   SMTP_USER=user
   SMTP_PASSWORD=password
   EMAILS_FROM_EMAIL=noreply@azureshield.com
   EMAILS_FROM_NAME=AzureShield
   ```

## Start Docker Services

Start the essential services using Docker Compose:

```bash
# In case of port conflicts for Redis (6379), edit docker-compose.yml to use 6380:6379
docker-compose up -d db redis prometheus grafana
```

## Backend Setup

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a Python virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: .\venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run database migrations:
   ```bash
   alembic upgrade head
   ```

5. Start the backend server:
   ```bash
   uvicorn app.main:app --reload
   ```

## Frontend Setup

1. Open a new terminal and navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Start the development server:
   ```bash
   npm run dev
   ```

## Accessing the Application

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs
- Grafana: http://localhost:3001 (admin/admin)
- Prometheus: http://localhost:9090

## Common Issues and Solutions

### Redis Port Conflict

If you have Redis running locally, you may encounter a port conflict. To resolve this:

1. Edit `docker-compose.yml` and change the Redis port mapping from `6379:6379` to `6380:6379`:
   ```yaml
   redis:
     image: redis:7-alpine
     ports:
       - "6380:6379"
   ```

2. Update the `REDIS_URL` in your `.env` file to:
   ```
   REDIS_URL=redis://localhost:6380/0
   ```

### Backend Cannot Connect to Database

If the backend can't connect to the database:

1. Ensure the PostgreSQL container is running: `docker-compose ps`
2. Check that your `.env` file has the correct database credentials
3. Verify the `DATABASE_URL` matches the settings in `docker-compose.yml`

### Permission Issues in Docker Containers

If you see permission errors like `EACCES: permission denied` in the logs:

1. Check that volume mounts have appropriate permissions
2. For development, you may need to run Docker Compose with:
   ```bash
   docker-compose down
   docker-compose up -d --build
   ``` 