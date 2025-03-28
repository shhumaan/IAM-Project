import React, { createContext, useContext, useEffect, useState } from 'react';
import { useRouter } from 'next/router';
import { User, AuthResponse } from '@/types';
import { api } from '@/services/api';

interface AuthContextType {
  user: User | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  login: (email: string, password: string) => Promise<void>;
  register: (data: {
    email: string;
    password: string;
    firstName: string;
    lastName: string;
  }) => Promise<void>;
  logout: () => void;
  verifyMFA: (code: string) => Promise<void>;
  setupMFA: () => Promise<{ secret: string; qrCode: string }>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();

  useEffect(() => {
    checkAuth();
  }, []);

  const checkAuth = async () => {
    try {
      const token = localStorage.getItem('accessToken');
      if (token) {
        const user = await api.getCurrentUser();
        setUser(user);
      }
    } catch (error) {
      console.error('Auth check failed:', error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleAuthResponse = (response: AuthResponse) => {
    localStorage.setItem('accessToken', response.accessToken);
    localStorage.setItem('refreshToken', response.refreshToken);
    setUser(response.user);
  };

  const login = async (email: string, password: string) => {
    try {
      const response = await api.login({ email, password });
      handleAuthResponse(response);
      router.push('/dashboard');
    } catch (error) {
      console.error('Login failed:', error);
      throw error;
    }
  };

  const register = async (data: {
    email: string;
    password: string;
    firstName: string;
    lastName: string;
  }) => {
    try {
      const response = await api.register(data);
      handleAuthResponse(response);
      router.push('/dashboard');
    } catch (error) {
      console.error('Registration failed:', error);
      throw error;
    }
  };

  const logout = () => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    setUser(null);
    router.push('/auth/login');
  };

  const verifyMFA = async (code: string) => {
    try {
      const response = await api.verifyMFA(code);
      handleAuthResponse(response);
      router.push('/dashboard');
    } catch (error) {
      console.error('MFA verification failed:', error);
      throw error;
    }
  };

  const setupMFA = async () => {
    try {
      return await api.setupMFA();
    } catch (error) {
      console.error('MFA setup failed:', error);
      throw error;
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        isLoading,
        isAuthenticated: !!user,
        login,
        register,
        logout,
        verifyMFA,
        setupMFA,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
} 