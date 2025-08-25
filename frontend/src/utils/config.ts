/**
 * Configuration utility for environment-based settings
 */

// Environment detection
export const isDevelopment = import.meta.env.DEV;
export const isProduction = import.meta.env.PROD;

// API Configuration
export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';
export const API_URL = `${API_BASE_URL}/api`;

// App Configuration
export const APP_NAME = import.meta.env.VITE_APP_NAME || 'GeminiPay Budget App';

// Debug function to log configuration (only in development)
export const logConfig = () => {
  if (isDevelopment) {
    console.group('🔧 App Configuration');
    console.log('Environment:', isDevelopment ? 'Development' : 'Production');
    console.log('API Base URL:', API_BASE_URL);
    console.log('API URL:', API_URL);
    console.log('App Name:', APP_NAME);
    console.groupEnd();
  }
};

// Export configuration object
export const config = {
  isDevelopment,
  isProduction,
  API_BASE_URL,
  API_URL,
  APP_NAME,
} as const;