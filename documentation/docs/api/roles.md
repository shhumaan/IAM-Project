---
sidebar_position: 5
---

# Roles API

The Roles API allows managing role definitions and assignments in AzureShield IAM.

## List Roles

```http
GET /api/v1/roles
Authorization: Bearer {access_token}
```

Query Parameters:
- `page` - Page number (default: 1)
- `limit` - Results per page (default: 20)

Response:

```json
{
  "data": [
    {
      "id": "role123",
      "name": "admin",
      "description": "Administrator role with full access",
      "created_at": "2023-01-01T00:00:00Z"
    },
    {
      "id": "role124",
      "name": "user",
      "description": "Standard user role with limited access",
      "created_at": "2023-01-01T00:00:00Z"
    }
  ],
  "total": 8,
  "page": 1,
  "limit": 20,
  "pages": 1
}
```

## Get Role Details

```http
GET /api/v1/roles/{role_id}
Authorization: Bearer {access_token}
```

Response:

```json
{
  "id": "role123",
  "name": "admin",
  "description": "Administrator role with full access",
  "permissions": [
    "users:read",
    "users:write",
    "roles:read",
    "roles:write",
    "policies:read",
    "policies:write"
  ],
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-15T00:00:00Z"
}
```

## Create Role

```http
POST /api/v1/roles
Content-Type: application/json
Authorization: Bearer {access_token}

{
  "name": "auditor",
  "description": "Role for security auditors",
  "permissions": [
    "users:read",
    "roles:read",
    "policies:read",
    "audit:read"
  ]
}
```

Response:

```json
{
  "id": "role125",
  "name": "auditor",
  "description": "Role for security auditors",
  "permissions": [
    "users:read",
    "roles:read",
    "policies:read",
    "audit:read"
  ],
  "created_at": "2023-02-15T00:00:00Z"
}
```

## Update Role

```http
PUT /api/v1/roles/{role_id}
Content-Type: application/json
Authorization: Bearer {access_token}

{
  "description": "Updated role description",
  "permissions": [
    "users:read",
    "roles:read",
    "policies:read",
    "audit:read",
    "audit:export"
  ]
}
```

Response:

```json
{
  "id": "role125",
  "name": "auditor",
  "description": "Updated role description",
  "permissions": [
    "users:read",
    "roles:read",
    "policies:read",
    "audit:read",
    "audit:export"
  ],
  "updated_at": "2023-02-20T00:00:00Z"
}
```

## Delete Role

```http
DELETE /api/v1/roles/{role_id}
Authorization: Bearer {access_token}
```

Response:

```json
{
  "message": "Role deleted successfully"
}
```

## Assign Role to User

```http
POST /api/v1/roles/{role_id}/assign
Content-Type: application/json
Authorization: Bearer {access_token}

{
  "user_id": "user123"
}
```

Response:

```json
{
  "message": "Role assigned successfully"
}
```

## Remove Role from User

```http
POST /api/v1/roles/{role_id}/remove
Content-Type: application/json
Authorization: Bearer {access_token}

{
  "user_id": "user123"
}
```

Response:

```json
{
  "message": "Role removed successfully"
}
``` 