---
sidebar_position: 8
---

# ABAC API

The ABAC (Attribute-Based Access Control) API allows managing attribute-based access control configurations.

## Attributes Management

### List Attributes

```http
GET /api/v1/abac/attributes
Authorization: Bearer {access_token}
```

Response:

```json
{
  "data": [
    {
      "id": "attr1",
      "name": "department",
      "description": "User's department",
      "type": "string",
      "allowed_values": ["engineering", "finance", "hr", "marketing"]
    },
    {
      "id": "attr2",
      "name": "location",
      "description": "User's physical location",
      "type": "string",
      "allowed_values": ["us-east", "us-west", "eu-central", "asia-pacific"]
    },
    {
      "id": "attr3",
      "name": "access_level",
      "description": "User's access level",
      "type": "integer",
      "allowed_values": [1, 2, 3, 4, 5]
    }
  ],
  "total": 3
}
```

### Create Attribute

```http
POST /api/v1/abac/attributes
Content-Type: application/json
Authorization: Bearer {access_token}

{
  "name": "project",
  "description": "Project the user is assigned to",
  "type": "string",
  "allowed_values": ["alpha", "beta", "gamma", "delta"]
}
```

Response:

```json
{
  "id": "attr4",
  "name": "project",
  "description": "Project the user is assigned to",
  "type": "string",
  "allowed_values": ["alpha", "beta", "gamma", "delta"],
  "created_at": "2023-03-15T00:00:00Z"
}
```

### Get Attribute Details

```http
GET /api/v1/abac/attributes/{attribute_id}
Authorization: Bearer {access_token}
```

Response:

```json
{
  "id": "attr1",
  "name": "department",
  "description": "User's department",
  "type": "string",
  "allowed_values": ["engineering", "finance", "hr", "marketing"],
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-15T00:00:00Z"
}
```

### Update Attribute

```http
PUT /api/v1/abac/attributes/{attribute_id}
Content-Type: application/json
Authorization: Bearer {access_token}

{
  "description": "Updated attribute description",
  "allowed_values": ["engineering", "finance", "hr", "marketing", "operations"]
}
```

Response:

```json
{
  "id": "attr1",
  "name": "department",
  "description": "Updated attribute description",
  "type": "string",
  "allowed_values": ["engineering", "finance", "hr", "marketing", "operations"],
  "updated_at": "2023-03-20T00:00:00Z"
}
```

### Delete Attribute

```http
DELETE /api/v1/abac/attributes/{attribute_id}
Authorization: Bearer {access_token}
```

Response:

```json
{
  "message": "Attribute deleted successfully"
}
```

## User Attributes

### Get User Attributes

```http
GET /api/v1/abac/users/{user_id}/attributes
Authorization: Bearer {access_token}
```

Response:

```json
{
  "data": {
    "department": "engineering",
    "location": "us-west",
    "access_level": 3,
    "project": "alpha"
  }
}
```

### Set User Attribute

```http
PUT /api/v1/abac/users/{user_id}/attributes/{attribute_name}
Content-Type: application/json
Authorization: Bearer {access_token}

{
  "value": "finance"
}
```

Response:

```json
{
  "user_id": "user123",
  "attribute": "department",
  "value": "finance",
  "updated_at": "2023-03-25T00:00:00Z"
}
```

### Delete User Attribute

```http
DELETE /api/v1/abac/users/{user_id}/attributes/{attribute_name}
Authorization: Bearer {access_token}
```

Response:

```json
{
  "message": "User attribute removed successfully"
}
```

## Resource Attributes

### Get Resource Attributes

```http
GET /api/v1/abac/resources/{resource_type}/{resource_id}/attributes
Authorization: Bearer {access_token}
```

Response:

```json
{
  "data": {
    "sensitivity": "confidential",
    "owner_department": "finance",
    "created_by": "user123"
  }
}
```

### Set Resource Attribute

```http
PUT /api/v1/abac/resources/{resource_type}/{resource_id}/attributes/{attribute_name}
Content-Type: application/json
Authorization: Bearer {access_token}

{
  "value": "restricted"
}
```

Response:

```json
{
  "resource_type": "document",
  "resource_id": "doc123",
  "attribute": "sensitivity",
  "value": "restricted",
  "updated_at": "2023-03-25T00:00:00Z"
}
```

### Delete Resource Attribute

```http
DELETE /api/v1/abac/resources/{resource_type}/{resource_id}/attributes/{attribute_name}
Authorization: Bearer {access_token}
```

Response:

```json
{
  "message": "Resource attribute removed successfully"
}
``` 