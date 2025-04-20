---
sidebar_position: 6
---

# Permissions API

The Permissions API allows managing permission definitions in AzureShield IAM.

## List Permissions

```http
GET /api/v1/permissions
Authorization: Bearer {access_token}
```

Query Parameters:
- `page` - Page number (default: 1)
- `limit` - Results per page (default: 50)
- `scope` - Filter by scope (e.g., 'users', 'roles')

Response:

```json
{
  "data": [
    {
      "id": "perm123",
      "name": "users:read",
      "description": "Ability to view user details",
      "scope": "users"
    },
    {
      "id": "perm124",
      "name": "users:write",
      "description": "Ability to create and modify users",
      "scope": "users"
    },
    {
      "id": "perm125",
      "name": "roles:read",
      "description": "Ability to view role details",
      "scope": "roles"
    }
  ],
  "total": 25,
  "page": 1,
  "limit": 50,
  "pages": 1
}
```

## Get Permission Details

```http
GET /api/v1/permissions/{permission_id}
Authorization: Bearer {access_token}
```

Response:

```json
{
  "id": "perm123",
  "name": "users:read",
  "description": "Ability to view user details",
  "scope": "users",
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-15T00:00:00Z",
  "roles_with_permission": [
    "admin",
    "user_manager",
    "auditor"
  ]
}
```

## Create Permission

```http
POST /api/v1/permissions
Content-Type: application/json
Authorization: Bearer {access_token}

{
  "name": "reports:export",
  "description": "Ability to export system reports",
  "scope": "reports"
}
```

Response:

```json
{
  "id": "perm126",
  "name": "reports:export",
  "description": "Ability to export system reports",
  "scope": "reports",
  "created_at": "2023-02-15T00:00:00Z"
}
```

## Update Permission

```http
PUT /api/v1/permissions/{permission_id}
Content-Type: application/json
Authorization: Bearer {access_token}

{
  "description": "Updated permission description",
  "scope": "reporting"
}
```

Response:

```json
{
  "id": "perm126",
  "name": "reports:export",
  "description": "Updated permission description",
  "scope": "reporting",
  "updated_at": "2023-02-20T00:00:00Z"
}
```

## Delete Permission

```http
DELETE /api/v1/permissions/{permission_id}
Authorization: Bearer {access_token}
```

Response:

```json
{
  "message": "Permission deleted successfully"
}
```

## Get Roles with Permission

```http
GET /api/v1/permissions/{permission_id}/roles
Authorization: Bearer {access_token}
```

Response:

```json
{
  "data": [
    {
      "id": "role123",
      "name": "admin",
      "description": "Administrator role with full access"
    },
    {
      "id": "role127",
      "name": "report_manager",
      "description": "Role for managing reports"
    }
  ],
  "total": 2
}
```

## Get Users with Permission

```http
GET /api/v1/permissions/{permission_id}/users
Authorization: Bearer {access_token}
```

Response:

```json
{
  "data": [
    {
      "id": "user123",
      "username": "johndoe",
      "email": "john.doe@example.com"
    },
    {
      "id": "user129",
      "username": "reportuser",
      "email": "reports@example.com"
    }
  ],
  "total": 2,
  "page": 1,
  "limit": 20,
  "pages": 1
}
``` 