# AzureShield IAM API Documentation

## Overview

The AzureShield IAM API provides a comprehensive set of endpoints for identity and access management. This documentation outlines the available endpoints, their usage, and examples.

## Authentication

All API endpoints require authentication using JWT tokens. Include the token in the Authorization header:

```http
Authorization: Bearer <your_jwt_token>
```

## Base URL

- Development: `http://localhost:8000/api/v1`
- Production: `https://api.azureshield-iam.com/api/v1`

## Rate Limiting

- 100 requests per minute per IP
- 1000 requests per hour per user
- Rate limit headers included in responses

## Endpoints

### Authentication

#### Login

```http
POST /auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "secure_password"
}
```

Response:
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 3600
}
```

#### MFA Setup

```http
POST /auth/mfa/setup
Authorization: Bearer <token>

Response:
{
  "qr_code": "otpauth://totp/AzureShield:user@example.com?secret=JBSWY3DPEHPK3PXP",
  "secret": "JBSWY3DPEHPK3PXP",
  "backup_codes": ["12345678", "87654321"]
}
```

### User Management

#### Create User

```http
POST /users
Authorization: Bearer <token>
Content-Type: application/json

{
  "email": "newuser@example.com",
  "password": "secure_password",
  "first_name": "John",
  "last_name": "Doe",
  "roles": ["user"]
}
```

Response:
```json
{
  "id": "uuid",
  "email": "newuser@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "roles": ["user"],
  "created_at": "2024-02-20T12:00:00Z",
  "updated_at": "2024-02-20T12:00:00Z"
}
```

### Role Management

#### Create Role

```http
POST /roles
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "admin",
  "description": "System Administrator",
  "permissions": ["read:all", "write:all", "delete:all"]
}
```

Response:
```json
{
  "id": "uuid",
  "name": "admin",
  "description": "System Administrator",
  "permissions": ["read:all", "write:all", "delete:all"],
  "created_at": "2024-02-20T12:00:00Z"
}
```

### Policy Management

#### Create Policy

```http
POST /policies
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "restricted-access",
  "description": "Restrict access to sensitive resources",
  "rules": [
    {
      "effect": "deny",
      "action": ["read", "write"],
      "resource": ["/api/sensitive/*"],
      "conditions": {
        "ip": ["192.168.1.0/24"],
        "time": ["09:00-17:00"]
      }
    }
  ]
}
```

Response:
```json
{
  "id": "uuid",
  "name": "restricted-access",
  "description": "Restrict access to sensitive resources",
  "rules": [...],
  "created_at": "2024-02-20T12:00:00Z",
  "version": 1
}
```

### Audit Logs

#### Get Audit Logs

```http
GET /audit-logs
Authorization: Bearer <token>
Query Parameters:
  - start_date: ISO 8601 date
  - end_date: ISO 8601 date
  - event_type: string
  - severity: string
  - user_id: uuid
  - page: integer
  - page_size: integer
```

Response:
```json
{
  "total": 100,
  "page": 1,
  "page_size": 10,
  "logs": [
    {
      "id": "uuid",
      "timestamp": "2024-02-20T12:00:00Z",
      "event_type": "user.login",
      "severity": "info",
      "user_id": "uuid",
      "action": "login",
      "resource_type": "user",
      "result": "success",
      "details": {
        "ip_address": "192.168.1.1",
        "user_agent": "Mozilla/5.0..."
      }
    }
  ]
}
```

## Error Responses

All endpoints may return the following error responses:

### 400 Bad Request

```json
{
  "error": "validation_error",
  "message": "Invalid input data",
  "details": {
    "email": ["Invalid email format"],
    "password": ["Password must be at least 8 characters"]
  }
}
```

### 401 Unauthorized

```json
{
  "error": "unauthorized",
  "message": "Invalid or expired token"
}
```

### 403 Forbidden

```json
{
  "error": "forbidden",
  "message": "Insufficient permissions"
}
```

### 404 Not Found

```json
{
  "error": "not_found",
  "message": "Resource not found"
}
```

### 429 Too Many Requests

```json
{
  "error": "rate_limit_exceeded",
  "message": "Rate limit exceeded",
  "retry_after": 60
}
```

### 500 Internal Server Error

```json
{
  "error": "internal_server_error",
  "message": "An unexpected error occurred"
}
```

## Webhooks

AzureShield IAM supports webhooks for real-time event notifications. Configure webhooks through the API:

```http
POST /webhooks
Authorization: Bearer <token>
Content-Type: application/json

{
  "url": "https://your-webhook-url.com/events",
  "events": ["user.created", "user.updated", "security.alert"],
  "secret": "your-webhook-secret"
}
```

## SDK Examples

### Python

```python
from azureshield_iam import AzureShieldIAM

client = AzureShieldIAM(
    base_url="https://api.azureshield-iam.com/api/v1",
    api_key="your-api-key"
)

# Create user
user = client.users.create(
    email="user@example.com",
    password="secure_password",
    first_name="John",
    last_name="Doe"
)

# Get audit logs
logs = client.audit_logs.list(
    start_date="2024-02-01",
    end_date="2024-02-20",
    event_type="user.login"
)
```

### JavaScript/TypeScript

```typescript
import { AzureShieldIAM } from '@azureshield/iam-sdk';

const client = new AzureShieldIAM({
  baseUrl: 'https://api.azureshield-iam.com/api/v1',
  apiKey: 'your-api-key'
});

// Create user
const user = await client.users.create({
  email: 'user@example.com',
  password: 'secure_password',
  firstName: 'John',
  lastName: 'Doe'
});

// Get audit logs
const logs = await client.auditLogs.list({
  startDate: '2024-02-01',
  endDate: '2024-02-20',
  eventType: 'user.login'
});
``` 