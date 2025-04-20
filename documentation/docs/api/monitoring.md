---
sidebar_position: 11
---

# Monitoring API

The Monitoring API allows accessing system health and performance metrics.

## System Health

```http
GET /api/v1/monitoring/health
Authorization: Bearer {access_token}
```

Response:

```json
{
  "status": "healthy",
  "api_version": "1.0.0",
  "uptime": 1209600,
  "database_status": "connected",
  "cache_status": "connected",
  "last_checked": "2023-04-01T00:00:00Z"
}
```

## Component Status

```http
GET /api/v1/monitoring/components
Authorization: Bearer {access_token}
```

Response:

```json
{
  "components": [
    {
      "name": "api_service",
      "status": "healthy",
      "version": "1.0.0",
      "uptime": 1209600
    },
    {
      "name": "database",
      "status": "healthy",
      "version": "14.2",
      "connections": 15,
      "max_connections": 100
    },
    {
      "name": "cache",
      "status": "healthy",
      "version": "7.0.8",
      "memory_usage": "256MB",
      "total_memory": "1GB"
    }
  ],
  "last_checked": "2023-04-01T00:00:00Z"
}
```

## Performance Metrics

```http
GET /api/v1/monitoring/metrics
Authorization: Bearer {access_token}
```

Query Parameters:
- `start_time` - Start time for metrics (ISO 8601 format)
- `end_time` - End time for metrics (ISO 8601 format)
- `interval` - Time interval for data points (minute, hour, day)

Response:

```json
{
  "timeframe": {
    "start": "2023-04-01T00:00:00Z",
    "end": "2023-04-01T23:59:59Z",
    "interval": "hour"
  },
  "metrics": {
    "requests_per_second": [
      {"timestamp": "2023-04-01T00:00:00Z", "value": 15.5},
      {"timestamp": "2023-04-01T01:00:00Z", "value": 12.3},
      {"timestamp": "2023-04-01T02:00:00Z", "value": 8.7}
    ],
    "response_time_ms": [
      {"timestamp": "2023-04-01T00:00:00Z", "value": 250},
      {"timestamp": "2023-04-01T01:00:00Z", "value": 275},
      {"timestamp": "2023-04-01T02:00:00Z", "value": 225}
    ],
    "error_rate": [
      {"timestamp": "2023-04-01T00:00:00Z", "value": 0.02},
      {"timestamp": "2023-04-01T01:00:00Z", "value": 0.01},
      {"timestamp": "2023-04-01T02:00:00Z", "value": 0.03}
    ],
    "cpu_usage": [
      {"timestamp": "2023-04-01T00:00:00Z", "value": 45},
      {"timestamp": "2023-04-01T01:00:00Z", "value": 40},
      {"timestamp": "2023-04-01T02:00:00Z", "value": 35}
    ],
    "memory_usage": [
      {"timestamp": "2023-04-01T00:00:00Z", "value": 60},
      {"timestamp": "2023-04-01T01:00:00Z", "value": 62},
      {"timestamp": "2023-04-01T02:00:00Z", "value": 58}
    ]
  }
}
```

## Active Users

```http
GET /api/v1/monitoring/active-users
Authorization: Bearer {access_token}
```

Query Parameters:
- `timeframe` - Timeframe to check (minute, hour, day, week, month)

Response:

```json
{
  "timeframe": "day",
  "active_users": 152,
  "unique_sessions": 187,
  "peak_concurrent_users": 45,
  "peak_time": "2023-04-01T14:30:00Z"
}
```

## API Usage Statistics

```http
GET /api/v1/monitoring/api-usage
Authorization: Bearer {access_token}
```

Query Parameters:
- `start_time` - Start time for metrics (ISO 8601 format)
- `end_time` - End time for metrics (ISO 8601 format)
- `group_by` - Group results by (endpoint, method, user, none)

Response:

```json
{
  "timeframe": {
    "start": "2023-04-01T00:00:00Z",
    "end": "2023-04-01T23:59:59Z"
  },
  "grouped_by": "endpoint",
  "data": [
    {
      "endpoint": "/api/v1/users",
      "method": "GET",
      "requests": 1250,
      "avg_response_time_ms": 180,
      "errors": 5,
      "error_rate": 0.004
    },
    {
      "endpoint": "/api/v1/users",
      "method": "POST",
      "requests": 75,
      "avg_response_time_ms": 350,
      "errors": 3,
      "error_rate": 0.04
    },
    {
      "endpoint": "/api/v1/auth/login",
      "method": "POST",
      "requests": 580,
      "avg_response_time_ms": 420,
      "errors": 45,
      "error_rate": 0.078
    }
  ],
  "total_requests": 3456,
  "avg_response_time_ms": 275,
  "total_errors": 78,
  "overall_error_rate": 0.023
}
```

## Alert Configuration

```http
GET /api/v1/monitoring/alerts/config
Authorization: Bearer {access_token}
```

Response:

```json
{
  "alert_configurations": [
    {
      "id": "alert1",
      "name": "High CPU Usage",
      "metric": "cpu_usage",
      "threshold": 85,
      "condition": "above",
      "duration": 300,
      "notification_channels": ["email", "slack"],
      "status": "active"
    },
    {
      "id": "alert2",
      "name": "High Error Rate",
      "metric": "error_rate",
      "threshold": 0.05,
      "condition": "above",
      "duration": 300,
      "notification_channels": ["email", "slack", "sms"],
      "status": "active"
    }
  ]
}
```

## Alert History

```http
GET /api/v1/monitoring/alerts/history
Authorization: Bearer {access_token}
```

Query Parameters:
- `start_time` - Start time for alert history (ISO 8601 format)
- `end_time` - End time for alert history (ISO 8601 format)
- `status` - Filter by status (triggered, resolved, all)

Response:

```json
{
  "alerts": [
    {
      "id": "incident123",
      "alert_config_id": "alert1",
      "alert_name": "High CPU Usage",
      "triggered_at": "2023-04-01T14:25:00Z",
      "resolved_at": "2023-04-01T14:45:00Z",
      "duration": 1200,
      "peak_value": 92,
      "status": "resolved"
    },
    {
      "id": "incident124",
      "alert_config_id": "alert2",
      "alert_name": "High Error Rate",
      "triggered_at": "2023-04-01T18:30:00Z",
      "resolved_at": null,
      "duration": null,
      "peak_value": 0.08,
      "status": "triggered"
    }
  ],
  "total": 2
}
``` 