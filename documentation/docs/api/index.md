---
sidebar_position: 5
---

# API Documentation

AzureShield IAM provides a comprehensive RESTful API for integrating with the platform. This section documents the available endpoints, request formats, and response examples.

## API Base URL

The base URL for all API endpoints is:

- **Development**: `http://localhost:8000/api/v1`
- **Production**: `https://your-domain.com/api/v1`

## Authentication

Most API endpoints require authentication. AzureShield IAM uses JWT tokens for authentication.

### Obtaining a Token

To get a JWT token, make a POST request to the login endpoint:

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "username": "admin@example.com",
  "password": "your-password"
}
```

Response:

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

### Using the Token

Include the JWT token in the Authorization header for all authenticated requests:

```http
GET /api/v1/users/me
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

## API Endpoints

The AzureShield IAM API is organized into several categories:

### Authentication & Authorization

- [Authentication API](./authentication.md) - Login, logout, token refresh
- [Multi-Factor Authentication API](./mfa.md) - MFA setup, verification
- [Authorization API](./authorization.md) - Permissions and policy checking

### User Management

- [Users API](./users.md) - CRUD operations for users
- [Roles API](./roles.md) - Role management endpoints
- [Permissions API](./permissions.md) - Permission definition and assignment

### Policy Management

- [RBAC API](./rbac.md) - Role-based access control endpoints
- [ABAC API](./abac.md) - Attribute-based access control endpoints
- [Policies API](./policies.md) - Policy management endpoints

### Monitoring & Auditing

- [Audit Logs API](./audit.md) - Access and change history
- [Monitoring API](./monitoring.md) - System health and metrics

## Swagger Documentation

The API includes interactive Swagger documentation that allows you to explore and test all endpoints.

Access the Swagger UI at:

- **Development**: `http://localhost:8000/docs`
- **Production**: `https://your-domain.com/docs`

## Error Handling

The API uses standard HTTP status codes to indicate the success or failure of requests:

- `200 OK` - The request was successful
- `201 Created` - A new resource was successfully created
- `400 Bad Request` - Invalid request syntax or parameters
- `401 Unauthorized` - Authentication failed or is missing
- `403 Forbidden` - The client does not have the required permissions
- `404 Not Found` - The requested resource does not exist
- `500 Internal Server Error` - An unexpected server error occurred

Error responses include a JSON object with details:

```json
{
  "error": "FORBIDDEN",
  "message": "Not enough permissions",
  "detail": "User does not have the required permission: users:write"
}
```

## Rate Limiting

The API implements rate limiting to protect against abuse. The default limits are:

- 100 requests per minute for authenticated users
- 20 requests per minute for unauthenticated requests

Rate limit headers are included in each response:

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1620000000
```

## API Versioning

The API uses URL-based versioning with the format `/api/v{version_number}/`. The current version is `v1`.

When a new incompatible API version is released, the previous version will be maintained for a deprecation period. 