export interface User {
  id: string;
  email: string;
  firstName: string;
  lastName: string;
  isActive: boolean;
  roles: Role[];
  permissions: Permission[];
  mfaEnabled: boolean;
  lastLoginAt?: string;
  createdAt: string;
  updatedAt: string;
}

export interface Role {
  id: string;
  name: string;
  description: string;
  permissions: Permission[];
  createdAt: string;
  updatedAt: string;
}

export interface Permission {
  id: string;
  name: string;
  description: string;
  resource: string;
  action: string;
  createdAt: string;
  updatedAt: string;
}

export interface AuthResponse {
  accessToken: string;
  refreshToken: string;
  user: User;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface RegisterData {
  email: string;
  password: string;
  firstName: string;
  lastName: string;
}

export interface MFAVerification {
  code: string;
}

export interface SecurityEvent {
  id: string;
  type: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  description: string;
  userId?: string;
  ipAddress: string;
  userAgent: string;
  timestamp: string;
  metadata: Record<string, any>;
}

export interface AuditLog {
  id: string;
  eventType: string;
  userId: string;
  action: string;
  resourceType: string;
  resourceId: string;
  result: 'success' | 'failure';
  details: Record<string, any>;
  timestamp: string;
}

export interface SystemMetric {
  id: string;
  name: string;
  value: number;
  unit: string;
  timestamp: string;
  tags: Record<string, string>;
}

export interface ABACPolicy {
  id: string;
  name: string;
  description: string;
  effect: 'allow' | 'deny';
  conditions: ABACCondition[];
  createdAt: string;
  updatedAt: string;
}

export interface ABACCondition {
  attribute: string;
  operator: 'equals' | 'contains' | 'startsWith' | 'endsWith' | 'greaterThan' | 'lessThan';
  value: any;
}

export interface ApiError {
  code: string;
  message: string;
  details?: Record<string, any>;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
  totalPages: number;
} 