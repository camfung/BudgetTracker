/**
 * Authentication service for API calls.
 */

import api from './api';
import { 
  LoginCredentials, 
  UserCreate, 
  TokenResponse, 
  User, 
  GoogleOAuthRequest,
  MessageResponse 
} from '../types/user';

/**
 * Login with email and password.
 */
export const login = async (credentials: LoginCredentials): Promise<TokenResponse> => {
  const response = await api.post<TokenResponse>('/auth/login', credentials);
  return response.data;
};

/**
 * Register a new user.
 */
export const register = async (userData: UserCreate): Promise<TokenResponse> => {
  const response = await api.post<TokenResponse>('/auth/register', userData);
  return response.data;
};

/**
 * Login with Google OAuth.
 */
export const googleLogin = async (oauthData: GoogleOAuthRequest): Promise<TokenResponse> => {
  const response = await api.post<TokenResponse>('/auth/google', oauthData);
  return response.data;
};

/**
 * Get current user information.
 */
export const getCurrentUser = async (): Promise<User> => {
  const response = await api.get<User>('/auth/me');
  return response.data;
};

/**
 * Refresh access token.
 */
export const refreshToken = async (refreshToken: string): Promise<TokenResponse> => {
  const response = await api.post<TokenResponse>('/auth/refresh', {
    refresh_token: refreshToken,
  });
  return response.data;
};

/**
 * Logout user.
 */
export const logout = async (): Promise<MessageResponse> => {
  const response = await api.post<MessageResponse>('/auth/logout');
  return response.data;
};

/**
 * Test authentication (for debugging).
 */
export const testAuth = async (): Promise<MessageResponse> => {
  const response = await api.get<MessageResponse>('/auth/test');
  return response.data;
};