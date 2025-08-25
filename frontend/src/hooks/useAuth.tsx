/**
 * Custom hook for authentication actions.
 */

import { useState } from 'react';
import { useUser } from './useUser';
import { LoginCredentials, UserCreate, TokenResponse } from '../types/user';
import { login as loginService, register as registerService } from '../services/auth.service';

export interface UseAuthReturn {
  isLoading: boolean;
  error: string | null;
  login: (credentials: LoginCredentials) => Promise<boolean>;
  register: (userData: UserCreate) => Promise<boolean>;
  clearError: () => void;
}

export const useAuth = (): UseAuthReturn => {
  const { login: setUser } = useUser();
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const login = async (credentials: LoginCredentials): Promise<boolean> => {
    setIsLoading(true);
    setError(null);

    try {
      const tokenResponse: TokenResponse = await loginService(credentials);
      setUser(tokenResponse);
      return true;
    } catch (err: any) {
      setError(err.response?.data?.message || 'Login failed. Please try again.');
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const register = async (userData: UserCreate): Promise<boolean> => {
    setIsLoading(true);
    setError(null);

    try {
      const tokenResponse: TokenResponse = await registerService(userData);
      setUser(tokenResponse);
      return true;
    } catch (err: any) {
      setError(err.response?.data?.message || 'Registration failed. Please try again.');
      return false;
    } finally {
      setIsLoading(false);
    }
  };

  const clearError = () => {
    setError(null);
  };

  return {
    isLoading,
    error,
    login,
    register,
    clearError,
  };
};