---
sidebar_position: 4
---

# Users API

The Users API allows managing user accounts in the AzureShield IAM system.

## List Users

```http
GET /api/v1/users
Authorization: Bearer {access_token}
```

Query Parameters:
- `page` - Page number (default: 1)
- `limit` - Results per page (default: 20)
- `sort` - Sort field (default: created_at)
- `direction` - Sort direction (asc/desc, default: desc)
- `search` - Search term for username or email

Response:

```json
{
  "data": [
    {
      "id": "user123",
      "username": "johndoe",
      "email": "john.doe@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "status": "active",
      "created_at": "2023-01-01T00:00:00Z"
    },
    ...
  ],
  "total": 42,
  "page": 1,
  "limit": 20,
  "pages": 3
}
```

## Get User Details

```http
GET /api/v1/users/{user_id}
Authorization: Bearer {access_token}
```

Response:

```json
{
  "id": "user123",
  "username": "johndoe",
  "email": "john.doe@example.com",
  "first_name": "John",
  "last_name": "Doe",
  "status": "active",
  "roles": ["admin", "user"],
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-15T00:00:00Z",
  "last_login": "2023-02-01T00:00:00Z",
  "mfa_enabled": true
}
```

## Create User

```http
POST /api/v1/users
Content-Type: application/json
Authorization: Bearer {access_token}

{
  "username": "janedoe",
  "email": "jane.doe@example.com",
  "password": "securepassword",
  "first_name": "Jane",
  "last_name": "Doe",
  "roles": ["user"]
}
```

Response:

```json
{
  "id": "user124",
  "username": "janedoe",
  "email": "jane.doe@example.com",
  "first_name": "Jane",
  "last_name": "Doe",
  "status": "active",
  "roles": ["user"],
  "created_at": "2023-02-15T00:00:00Z"
}
```

## Update User

```http
PUT /api/v1/users/{user_id}
Content-Type: application/json
Authorization: Bearer {access_token}

{
  "first_name": "Jane",
  "last_name": "Smith",
  "status": "active"
}
```

Response:

```json
{
  "id": "user124",
  "username": "janedoe",
  "email": "jane.doe@example.com",
  "first_name": "Jane",
  "last_name": "Smith",
  "status": "active",
  "roles": ["user"],
  "updated_at": "2023-02-20T00:00:00Z"
}
```

## Delete User

```http
DELETE /api/v1/users/{user_id}
Authorization: Bearer {access_token}
```

Response:

```json
{
  "message": "User deleted successfully"
}
``` 