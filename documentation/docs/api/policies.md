---
sidebar_position: 9
---

# Policies API

The Policies API allows managing advanced access control policies.

## List Policies

```http
GET /api/v1/policies
Authorization: Bearer {access_token}
```

Query Parameters:
- `page` - Page number (default: 1)
- `limit` - Results per page (default: 20)
- `type` - Filter by policy type (rbac, abac, custom)

Response:

```json
{
  "data": [
    {
      "id": "policy1",
      "name": "geo_restriction",
      "description": "Restricts access based on geographic location",
      "type": "abac",
      "status": "active",
      "created_at": "2023-01-01T00:00:00Z"
    },
    {
      "id": "policy2",
      "name": "time_based_access",
      "description": "Allows access only during business hours",
      "type": "abac",
      "status": "active",
      "created_at": "2023-01-15T00:00:00Z"
    }
  ],
  "total": 8,
  "page": 1,
  "limit": 20,
  "pages": 1
}
```

## Get Policy Details

```http
GET /api/v1/policies/{policy_id}
Authorization: Bearer {access_token}
```

Response:

```json
{
  "id": "policy1",
  "name": "geo_restriction",
  "description": "Restricts access based on geographic location",
  "type": "abac",
  "status": "active",
  "rules": [
    {
      "effect": "allow",
      "condition": {
        "attribute": "user.location",
        "operator": "in",
        "value": ["us-east", "us-west", "eu-central"]
      }
    },
    {
      "effect": "deny",
      "condition": {
        "attribute": "user.location",
        "operator": "in",
        "value": ["asia-pacific"]
      }
    }
  ],
  "created_at": "2023-01-01T00:00:00Z",
  "updated_at": "2023-01-15T00:00:00Z"
}
```

## Create Policy

```http
POST /api/v1/policies
Content-Type: application/json
Authorization: Bearer {access_token}

{
  "name": "data_sensitivity",
  "description": "Controls access to sensitive data",
  "type": "abac",
  "rules": [
    {
      "effect": "allow",
      "condition": {
        "attribute": "user.access_level",
        "operator": ">=",
        "value": 3
      }
    },
    {
      "effect": "allow",
      "condition": {
        "attribute": "user.department",
        "operator": "==",
        "value": "engineering"
      }
    },
    {
      "effect": "deny",
      "condition": {
        "attribute": "resource.sensitivity",
        "operator": "==",
        "value": "restricted"
      }
    }
  ]
}
```

Response:

```json
{
  "id": "policy3",
  "name": "data_sensitivity",
  "description": "Controls access to sensitive data",
  "type": "abac",
  "status": "active",
  "rules": [
    {
      "effect": "allow",
      "condition": {
        "attribute": "user.access_level",
        "operator": ">=",
        "value": 3
      }
    },
    {
      "effect": "allow",
      "condition": {
        "attribute": "user.department",
        "operator": "==",
        "value": "engineering"
      }
    },
    {
      "effect": "deny",
      "condition": {
        "attribute": "resource.sensitivity",
        "operator": "==",
        "value": "restricted"
      }
    }
  ],
  "created_at": "2023-03-15T00:00:00Z"
}
```

## Update Policy

```http
PUT /api/v1/policies/{policy_id}
Content-Type: application/json
Authorization: Bearer {access_token}

{
  "description": "Updated policy description",
  "status": "inactive",
  "rules": [
    {
      "effect": "allow",
      "condition": {
        "attribute": "user.access_level",
        "operator": ">=",
        "value": 4
      }
    }
  ]
}
```

Response:

```json
{
  "id": "policy3",
  "name": "data_sensitivity",
  "description": "Updated policy description",
  "type": "abac",
  "status": "inactive",
  "rules": [
    {
      "effect": "allow",
      "condition": {
        "attribute": "user.access_level",
        "operator": ">=",
        "value": 4
      }
    }
  ],
  "updated_at": "2023-03-20T00:00:00Z"
}
```

## Delete Policy

```http
DELETE /api/v1/policies/{policy_id}
Authorization: Bearer {access_token}
```

Response:

```json
{
  "message": "Policy deleted successfully"
}
```

## Evaluate Policy

```http
POST /api/v1/policies/{policy_id}/evaluate
Content-Type: application/json
Authorization: Bearer {access_token}

{
  "user_id": "user123",
  "resource_type": "document",
  "resource_id": "doc123",
  "context": {
    "ip_address": "192.168.1.1",
    "request_time": "2023-04-01T14:30:00Z"
  }
}
```

Response:

```json
{
  "allowed": false,
  "policy_id": "policy3",
  "reason": "Resource sensitivity is restricted",
  "rule_index": 2,
  "evaluation_time_ms": 5
}
``` 