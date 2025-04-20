---
sidebar_position: 4
---

# Troubleshooting Guide

This guide provides solutions to common issues you might encounter when working with AzureShield IAM.

## Docker Setup Issues

### Error: Port is already allocated

**Problem**: When running `docker-compose up`, you see an error like:
```
Error response from daemon: driver failed programming external connectivity on endpoint: Bind for 0.0.0.0:6379 failed: port is already allocated
```

**Solution**:
1. Identify which service is using the port:
   ```bash
   sudo lsof -i :6379
   ```

2. Either stop the conflicting service or modify `docker-compose.yml` to use a different port:
   ```yaml
   redis:
     image: redis:7-alpine
     ports:
       - "6380:6379"  # Changed from 6379:6379
   ```

3. Update your `.env` file to reflect the new port:
   ```
   REDIS_URL=redis://redis:6380/0
   ```

### Error: Permission denied error in Docker logs

**Problem**: You see errors like:
```
Error: EACCES: permission denied, open '/app/.next/package.json'
```

**Solution**:
1. Fix permissions in the Docker container:
   ```bash
   docker-compose down
   docker-compose up -d --build
   ```

2. Modify the Dockerfile to ensure proper permissions:
   ```dockerfile
   # After copying files
   RUN chown -R appuser:appuser /app
   USER appuser
   ```

3. For local development, you can mount volumes with appropriate permissions:
   ```yaml
   volumes:
     - ./frontend:/app:delegated
   ```

## Database Connection Issues

### Error: Role "postgres" does not exist

**Problem**: When running database migrations, you see:
```
connection to server at "localhost" (::1), port 5432 failed: FATAL: role "postgres" does not exist
```

**Solution**:
1. Verify the PostgreSQL container is running:
   ```bash
   docker-compose ps db
   ```

2. Check database connection settings in your `.env` file:
   ```
   DATABASE_URL=postgresql://postgres:postgres@localhost:5432/azureshield_iam
   ```

3. For commands run from your local machine, ensure you're using the correct port and credentials:
   ```bash
   # If running migrations locally
   PGPASSWORD=postgres psql -U postgres -h localhost -p 5432 -d azureshield_iam
   ```

4. Create the postgres role if it doesn't exist:
   ```bash
   docker-compose exec db psql -U postgres -c "CREATE ROLE postgres WITH SUPERUSER LOGIN PASSWORD 'postgres';"
   ```

## Backend Application Issues

### Error: name 'get_db' is not defined

**Problem**: The API container crashes with:
```
NameError: name 'get_db' is not defined
```

**Solution**:
1. Check `backend/app/dependencies.py` file and ensure the `get_db` function is defined before it's used:
   ```python
   from app.db.session import AsyncSessionLocal, get_db as session_get_db
   
   # Define immediately after imports
   get_db = session_get_db
   
   # Then use it in functions
   async def get_current_user(
       db: AsyncSession = Depends(get_db),
       # ...
   ):
   ```

2. Restart the API container after making changes:
   ```bash
   docker-compose restart api
   ```

### Error: Table is already defined for this MetaData instance

**Problem**: You see an error like:
```
sqlalchemy.exc.InvalidRequestError: Table 'health_checks' is already defined for this MetaData instance.
```

**Solution**:
1. Check for duplicate model definitions or circular imports
2. Add `extend_existing=True` to the model definition:
   ```python
   class HealthCheck(Base):
       __tablename__ = 'health_checks'
       __table_args__ = {'extend_existing': True}
       # ...
   ```

3. Run migrations with the `--autogenerate` flag:
   ```bash
   alembic revision --autogenerate -m "fix duplicate tables"
   alembic upgrade head
   ```

## Frontend Application Issues

### Error: Cannot find module

**Problem**: The frontend fails to start with:
```
Error: Cannot find module '@/components/...'
```

**Solution**:
1. Check that all dependencies are installed:
   ```bash
   cd frontend
   npm install
   ```

2. Verify the module path and correct any import issues:
   ```jsx
   // Change from
   import Component from '@/components/Component'
   
   // To
   import Component from '../components/Component'
   ```

3. Clear the Next.js cache:
   ```bash
   cd frontend
   rm -rf .next
   npm run dev
   ```

### Error: API Connection Failed

**Problem**: Frontend can't connect to the backend API.

**Solution**:
1. Check the API service is running:
   ```bash
   docker-compose ps api
   ```

2. Verify the API URL in your frontend environment:
   ```
   # In frontend/.env
   NEXT_PUBLIC_API_URL=http://localhost:8000
   ```

3. Check browser network tab for CORS errors or network issues
4. Ensure the API service has CORS properly configured

## Environment Setup Issues

### Error: Missing Environment Variables

**Problem**: The application fails with errors about missing environment variables.

**Solution**:
1. Ensure you've copied the example environment file:
   ```bash
   cp .env.example .env
   ```

2. Add required variables to `docker-compose.yml`:
   ```yaml
   api:
     environment:
       - SECRET_KEY=your_secret_key_here
       - POSTGRES_SERVER=db
       - POSTGRES_USER=postgres
       - POSTGRES_PASSWORD=postgres
       - POSTGRES_DB=azureshield_iam
   ```

3. Restart services to load new environment variables:
   ```bash
   docker-compose down
   docker-compose up -d
   ```

## Still Having Issues?

If you continue to experience problems:

1. Check the detailed logs for each service:
   ```bash
   docker-compose logs api
   docker-compose logs frontend
   docker-compose logs db
   docker-compose logs redis
   ```

2. Review GitHub issues for similar problems and solutions
3. Consider raising a new issue with detailed error information and steps to reproduce 