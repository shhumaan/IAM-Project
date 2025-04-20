---
sidebar_position: 7
---

# RBAC API

The RBAC (Role-Based Access Control) API allows managing role-based access control configurations.

## Role Hierarchy Management

### Get Role Hierarchy

```http
GET /api/v1/rbac/hierarchy
Authorization: Bearer {access_token}
```

Response:

```json
{
  "data": {
    "admin": {
      "description": "Administrator role with full access",
      "children": ["manager", "auditor"]
    },
    "manager": {
      "description": "Manager role with department access",
      "children": ["user"]
    },
    "auditor": {
      "description": "Auditor role with read-only access",
      "children": ["viewer"]
    },
    "user": {
      "description": "Regular user role",
      "children": []
    },
    "viewer": {
      "description": "Limited view-only role",
      "children": []
    }
  }
}
```

### Update Role Hierarchy

```http
PUT /api/v1/rbac/hierarchy
Content-Type: application/json
Authorization: Bearer {access_token}

{
  "parent_role": "manager",
  "child_role": "auditor"
}
```

Response:

```json
{
  "message": "Role hierarchy updated successfully"
}
```

### Remove Role Hierarchy Relationship

```http
DELETE /api/v1/rbac/hierarchy
Content-Type: application/json
Authorization: Bearer {access_token}

{
  "parent_role": "manager",
  "child_role": "auditor"
}
```

Response:

```json
{
  "message": "Role hierarchy relationship removed successfully"
}
```

## Role Permission Management

### Add Permission to Role

```http
POST /api/v1/rbac/roles/{role_id}/permissions
Content-Type: application/json
Authorization: Bearer {access_token}

{
  "permission_id": "perm123"
}
```

Response:

```json
{
  "message": "Permission added to role successfully"
}
```

### Remove Permission from Role

```http
DELETE /api/v1/rbac/roles/{role_id}/permissions/{permission_id}
Authorization: Bearer {access_token}
```

Response:

```json
{
  "message": "Permission removed from role successfully"
}
```

### Get Role Effective Permissions

```http
GET /api/v1/rbac/roles/{role_id}/effective-permissions
Authorization: Bearer {access_token}
```

Response:

```json
{
  "data": [
    {
      "id": "perm123",
      "name": "users:read",
      "description": "Ability to view user details",
      "scope": "users",
      "inherited_from": null
    },
    {
      "id": "perm125",
      "name": "roles:read",
      "description": "Ability to view role details",
      "scope": "roles",
      "inherited_from": "admin"
    }
  ],
  "total": 2
}
```

## User Role Management

### Assign Role to User

```http
POST /api/v1/rbac/users/{user_id}/roles
Content-Type: application/json
Authorization: Bearer {access_token}

{
  "role_id": "role123"
}
```

Response:

```json
{
  "message": "Role assigned to user successfully"
}
```

### Remove Role from User

```http
DELETE /api/v1/rbac/users/{user_id}/roles/{role_id}
Authorization: Bearer {access_token}
```

Response:

```json
{
  "message": "Role removed from user successfully"
}
```

### Get User Effective Roles

```http
GET /api/v1/rbac/users/{user_id}/effective-roles
Authorization: Bearer {access_token}
```

Response:

```json
{
  "data": [
    {
      "id": "role123",
      "name": "admin",
      "description": "Administrator role with full access",
      "directly_assigned": true
    },
    {
      "id": "role125",
      "name": "manager",
      "description": "Manager role with department access",
      "directly_assigned": false,
      "inherited_from": "admin"
    }
  ],
  "total": 2
}
``` 