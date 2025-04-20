---
sidebar_position: 10
---

# Audit Logs API

The Audit Logs API allows retrieving and querying audit log entries.

## List Audit Logs

```http
GET /api/v1/audit
Authorization: Bearer {access_token}
```

Query Parameters:
- `page` - Page number (default: 1)
- `limit` - Results per page (default: 50)
- `start_time` - Filter logs after this time (ISO 8601 format)
- `end_time` - Filter logs before this time (ISO 8601 format)
- `user_id` - Filter by user ID
- `action_type` - Filter by action type (login, logout, create, update, delete, etc.)
- `resource_type` - Filter by resource type (user, role, permission, policy, etc.)
- `resource_id` - Filter by resource ID
- `status` - Filter by status (success, failure)

Response:

```json
{
  "data": [
    {
      "id": "log123",
      "timestamp": "2023-04-01T12:00:00Z",
      "user_id": "user123",
      "action_type": "login",
      "status": "success",
      "ip_address": "192.168.1.1",
      "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/90.0.4430.212"
    },
    {
      "id": "log124",
      "timestamp": "2023-04-01T12:05:00Z",
      "user_id": "user123",
      "action_type": "create",
      "resource_type": "user",
      "resource_id": "user456",
      "details": {
        "email": "jane.doe@example.com",
        "roles": ["user"]
      },
      "status": "success",
      "ip_address": "192.168.1.1",
      "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/90.0.4430.212"
    }
  ],
  "total": 253,
  "page": 1,
  "limit": 50,
  "pages": 6
}
```

## Get Audit Log Details

```http
GET /api/v1/audit/{log_id}
Authorization: Bearer {access_token}
```

Response:

```json
{
  "id": "log124",
  "timestamp": "2023-04-01T12:05:00Z",
  "user_id": "user123",
  "user_email": "john.doe@example.com",
  "action_type": "create",
  "resource_type": "user",
  "resource_id": "user456",
  "details": {
    "email": "jane.doe@example.com",
    "first_name": "Jane",
    "last_name": "Doe",
    "roles": ["user"]
  },
  "status": "success",
  "ip_address": "192.168.1.1",
  "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/90.0.4430.212",
  "session_id": "sess789"
}
```

## Export Audit Logs

```http
GET /api/v1/audit/export
Authorization: Bearer {access_token}
```

Query Parameters:
- `format` - Export format (csv, json)
- `start_time` - Filter logs after this time (ISO 8601 format)
- `end_time` - Filter logs before this time (ISO 8601 format)
- `user_id` - Filter by user ID
- `action_type` - Filter by action type (login, logout, create, update, delete, etc.)
- `resource_type` - Filter by resource type (user, role, permission, policy, etc.)
- `resource_id` - Filter by resource ID
- `status` - Filter by status (success, failure)

Response:

For CSV format, the response will be a CSV file download.

For JSON format:

```json
{
  "audit_logs": [
    {
      "id": "log123",
      "timestamp": "2023-04-01T12:00:00Z",
      "user_id": "user123",
      "user_email": "john.doe@example.com",
      "action_type": "login",
      "status": "success",
      "ip_address": "192.168.1.1",
      "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/90.0.4430.212"
    },
    // Additional logs...
  ],
  "export_time": "2023-04-02T09:00:00Z",
  "filter_criteria": {
    "start_time": "2023-04-01T00:00:00Z",
    "end_time": "2023-04-01T23:59:59Z",
    "action_type": "login"
  },
  "total_records": 45
}
```

## Get User Activity

```http
GET /api/v1/audit/users/{user_id}/activity
Authorization: Bearer {access_token}
```

Query Parameters:
- `page` - Page number (default: 1)
- `limit` - Results per page (default: 20)
- `start_time` - Filter logs after this time (ISO 8601 format)
- `end_time` - Filter logs before this time (ISO 8601 format)

Response:

```json
{
  "user_id": "user123",
  "user_email": "john.doe@example.com",
  "data": [
    {
      "id": "log123",
      "timestamp": "2023-04-01T12:00:00Z",
      "action_type": "login",
      "status": "success",
      "ip_address": "192.168.1.1"
    },
    {
      "id": "log124",
      "timestamp": "2023-04-01T12:05:00Z",
      "action_type": "create",
      "resource_type": "user",
      "resource_id": "user456",
      "status": "success",
      "ip_address": "192.168.1.1"
    }
  ],
  "total": 45,
  "page": 1,
  "limit": 20,
  "pages": 3
}
```

## Get Resource History

```http
GET /api/v1/audit/resources/{resource_type}/{resource_id}/history
Authorization: Bearer {access_token}
```

Query Parameters:
- `page` - Page number (default: 1)
- `limit` - Results per page (default: 20)

Response:

```json
{
  "resource_type": "user",
  "resource_id": "user456",
  "data": [
    {
      "id": "log124",
      "timestamp": "2023-04-01T12:05:00Z",
      "user_id": "user123",
      "action_type": "create",
      "details": {
        "email": "jane.doe@example.com",
        "roles": ["user"]
      },
      "status": "success"
    },
    {
      "id": "log125",
      "timestamp": "2023-04-01T14:30:00Z",
      "user_id": "user123",
      "action_type": "update",
      "details": {
        "changes": {
          "roles": {
            "old": ["user"],
            "new": ["user", "manager"]
          }
        }
      },
      "status": "success"
    }
  ],
  "total": 3,
  "page": 1,
  "limit": 20,
  "pages": 1
}
``` 