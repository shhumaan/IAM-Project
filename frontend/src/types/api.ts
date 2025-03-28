export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
}

export interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  roles: string[];
  created_at: string;
  updated_at: string;
}

export interface Role {
  id: string;
  name: string;
  description: string;
  permissions: string[];
  created_at: string;
}

export interface Policy {
  id: string;
  name: string;
  description: string;
  rules: PolicyRule[];
  created_at: string;
  version: number;
}

export interface PolicyRule {
  effect: 'allow' | 'deny';
  action: string[];
  resource: string[];
  conditions?: Record<string, string[]>;
}

export interface AuditLog {
  id: string;
  timestamp: string;
  event_type: string;
  severity: 'info' | 'warning' | 'error' | 'critical';
  user_id: string;
  action: string;
  resource_type: string;
  result: 'success' | 'failure';
  details: Record<string, any>;
}

export interface SecurityAlert {
  id: string;
  timestamp: string;
  alert_type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  status: 'open' | 'in_progress' | 'resolved';
  created_by: string;
  resolved_by?: string;
  resolved_at?: string;
}

export interface SystemMetric {
  id: string;
  timestamp: string;
  metric_type: string;
  value: number;
  tags: Record<string, string>;
}

export interface HealthCheck {
  id: string;
  timestamp: string;
  component: string;
  status: 'healthy' | 'degraded' | 'unhealthy';
  response_time: number;
  details: Record<string, any>;
}

export interface PaginatedResponse<T> {
  total: number;
  page: number;
  page_size: number;
  items: T[];
}

export interface SecurityEvent {
  id: string;
  timestamp: string;
  event_type: string;
  severity: 'info' | 'warning' | 'error' | 'critical';
  description: string;
  source: string;
  details: Record<string, any>;
}

export interface AuditLogResponse extends PaginatedResponse<AuditLog> {}
export interface SecurityAlertResponse extends PaginatedResponse<SecurityAlert> {}
export interface SystemMetricResponse extends PaginatedResponse<SystemMetric> {} 