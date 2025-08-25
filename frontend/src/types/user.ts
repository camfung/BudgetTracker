/**
 * User-related TypeScript interfaces.
 */

export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  created_at: string;
}

export interface UserCreate {
  email: string;
  password: string;
  first_name: string;
  last_name: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

export interface GoogleOAuthRequest {
  authorization_code: string;
  redirect_uri: string;
}

export interface MessageResponse {
  message: string;
  success: boolean;
}