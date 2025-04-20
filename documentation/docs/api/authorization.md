---
sidebar_position: 3
---

# Authorization API

The Authorization API allows checking permissions and evaluating access policies dynamically.

## Permission Checking

### Check User Permission

```http
POST /api/v1/auth/check-permission
Content-Type: application/json
Authorization: Bearer {access_token}

{
  "permission": "users:read",
  "resource_id": "user123",
  "context": {
    "location": "us-west",
    "ip_address": "192.168.1.1"
  }
}
```

Response:

```json
{
  "has_permission": true,
  "evaluated_policies": [
    "admin_policy",
    "geo_restriction_policy"
  ],
  "evaluation_time_ms": 5
}
```

### Batch Check Permissions

```http
POST /api/v1/auth/batch-check-permissions
Content-Type: application/json
Authorization: Bearer {access_token}

{
  "checks": [
    {
      "permission": "users:read",
      "resource_id": "user123"
    },
    {
      "permission": "users:write",
      "resource_id": "user123"
    }
  ],
  "context": {
    "location": "us-west",
    "ip_address": "192.168.1.1"
  }
}
```

Response:

```json
{
  "results": [
    {
      "permission": "users:read",
      "resource_id": "user123",
      "has_permission": true
    },
    {
      "permission": "users:write",
      "resource_id": "user123",
      "has_permission": false,
      "reason": "POLICY_DENIED"
    }
  ],
  "evaluation_time_ms": 8
}
```

## Policy Evaluation

### Evaluate Policy

```http
POST /api/v1/auth/evaluate-policy
Content-Type: application/json
Authorization: Bearer {access_token}

{
  "policy_id": "geo_restriction_policy",
  "context": {
    "user_id": "user123",
    "location": "us-west",
    "ip_address": "192.168.1.1",
    "device_id": "device456"
  }
}
```

Response:

```json
{
  "policy_id": "geo_restriction_policy",
  "allowed": true,
  "evaluation_details": {
    "rules_evaluated": 3,
    "rules_passed": 3,
    "rules_failed": 0,
    "evaluation_time_ms": 3
  }
}
``` 