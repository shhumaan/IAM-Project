import axios, { AxiosError, AxiosInstance, AxiosRequestConfig } from 'axios';
import { ApiError, AuthResponse } from '@/types';
import {
  LoginResponse,
  User,
  Role,
  Policy,
  AuditLog,
  SecurityAlert,
  SystemMetric,
  HealthCheck,
  PaginatedResponse,
  SecurityEvent,
  AuditLogResponse,
  SecurityAlertResponse,
  SystemMetricResponse,
} from '@/types/api';

class ApiService {
  private api: AxiosInstance;
  private static instance: ApiService;

  private constructor() {
    this.api = axios.create({
      baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    this.setupInterceptors();
  }

  public static getInstance(): ApiService {
    if (!ApiService.instance) {
      ApiService.instance = new ApiService();
    }
    return ApiService.instance;
  }

  private setupInterceptors(): void {
    // Request interceptor
    this.api.interceptors.request.use(
      (config) => {
        const token = localStorage.getItem('access_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.api.interceptors.response.use(
      (response) => response,
      async (error: AxiosError) => {
        if (error.response?.status === 401) {
          // Handle token expiration
          await this.refreshToken();
        }
        return Promise.reject(error);
      }
    );
  }

  private async refreshToken(): Promise<void> {
    try {
      const refreshToken = localStorage.getItem('refresh_token');
      if (!refreshToken) {
        throw new Error('No refresh token available');
      }

      const response = await this.api.post<LoginResponse>('/auth/refresh', {
        refresh_token: refreshToken,
      });

      localStorage.setItem('access_token', response.data.access_token);
      localStorage.setItem('refresh_token', response.data.refresh_token);
    } catch (error) {
      this.handleAuthError();
      throw error;
    }
  }

  private handleAuthError(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    window.location.href = '/auth/login';
  }

  private handleApiError(error: AxiosError): ApiError {
    if (error.response) {
      return {
        code: error.response.data.code || 'UNKNOWN_ERROR',
        message: error.response.data.message || 'An unexpected error occurred',
        details: error.response.data.details,
      };
    }

    return {
      code: 'NETWORK_ERROR',
      message: 'Network error occurred',
    };
  }

  // Auth endpoints
  public async login(email: string, password: string): Promise<LoginResponse> {
    try {
      const response = await this.api.post<LoginResponse>('/auth/login', {
        email,
        password,
      });
      return response.data;
    } catch (error) {
      this.handleError(error);
      throw error;
    }
  }

  public async register(data: {
    email: string;
    password: string;
    firstName: string;
    lastName: string;
  }): Promise<AuthResponse> {
    const response = await this.api.post<AuthResponse>('/auth/register', data);
    return response.data;
  }

  public async verifyMFA(code: string): Promise<AuthResponse> {
    const response = await this.api.post<AuthResponse>('/auth/verify-mfa', { code });
    return response.data;
  }

  public async setupMFA(): Promise<{ secret: string; qrCode: string }> {
    const response = await this.api.post<{ secret: string; qrCode: string }>('/auth/setup-mfa');
    return response.data;
  }

  // User endpoints
  public async getCurrentUser(): Promise<User> {
    const response = await this.api.get<User>('/users/me');
    return response.data;
  }

  public async updateProfile(data: {
    firstName: string;
    lastName: string;
  }): Promise<User> {
    const response = await this.api.patch<User>('/users/me', data);
    return response.data;
  }

  // Admin endpoints
  public async getUsers(params: {
    page: number;
    pageSize: number;
    search?: string;
  }): Promise<PaginatedResponse<User>> {
    const response = await this.api.get<PaginatedResponse<User>>('/admin/users', { params });
    return response.data;
  }

  public async updateUserRole(
    userId: string,
    roleIds: string[]
  ): Promise<User> {
    const response = await this.api.patch<User>(`/admin/users/${userId}/roles`, {
      roleIds,
    });
    return response.data;
  }

  // Security endpoints
  public async getSecurityEvents(params: {
    page: number;
    pageSize: number;
    severity?: string;
    startDate?: string;
    endDate?: string;
  }): Promise<PaginatedResponse<SecurityEvent>> {
    const response = await this.api.get<PaginatedResponse<SecurityEvent>>('/security/events', {
      params,
    });
    return response.data;
  }

  public async getAuditLogs(params: {
    page: number;
    pageSize: number;
    userId?: string;
    eventType?: string;
    startDate?: string;
    endDate?: string;
  }): Promise<PaginatedResponse<AuditLog>> {
    const response = await this.api.get<PaginatedResponse<AuditLog>>('/security/audit-logs', {
      params,
    });
    return response.data;
  }

  // System endpoints
  public async getSystemMetrics(): Promise<SystemMetric[]> {
    const response = await this.api.get<SystemMetric[]>('/system/metrics');
    return response.data;
  }

  public async getSystemHealth(): Promise<{
    status: string;
    components: Record<string, { status: string; details?: string }>;
  }> {
    const response = await this.api.get('/system/health');
    return response.data;
  }

  // Error handling
  private handleError(error: unknown): void {
    if (axios.isAxiosError(error)) {
      const axiosError = error as AxiosError;
      if (axiosError.response) {
        // The request was made and the server responded with a status code
        // that falls out of the range of 2xx
        const responseData = axiosError.response.data as Record<string, unknown>;
        console.error('API Error:', {
          status: axiosError.response.status,
          data: responseData,
          headers: axiosError.response.headers,
        });
      } else if (axiosError.request) {
        // The request was made but no response was received
        console.error('No response received:', axiosError.request);
      } else {
        // Something happened in setting up the request that triggered an Error
        console.error('Error setting up request:', axiosError.message);
      }
    } else {
      // Handle non-Axios errors
      console.error('Unexpected error:', error);
    }
  }
}

export const api = ApiService.getInstance(); 