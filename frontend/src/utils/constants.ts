/**
 * Application constants.
 */

export const APP_NAME = import.meta.env.VITE_APP_NAME || 'GeminiPay Budget App';

export const ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  REGISTER: '/register',
  DASHBOARD: '/dashboard',
  BUDGET: '/budget',
  TRANSACTIONS: '/transactions',
  HISTORY: '/history',
} as const;

export const API_ENDPOINTS = {
  AUTH: {
    LOGIN: '/auth/login',
    REGISTER: '/auth/register',
    LOGOUT: '/auth/logout',
    REFRESH: '/auth/refresh',
    ME: '/auth/me',
    GOOGLE: '/auth/google',
  },
  BUDGET: {
    PAY_PERIODS: '/budget/pay-periods',
    ALLOCATE: '/budget/allocate',
    CURRENT: '/budget/pay-periods/active/current',
  },
  TRANSACTIONS: {
    BASE: '/transactions',
    BULK: '/transactions/bulk',
    ANALYTICS: '/transactions/analytics/spending',
  },
} as const;

export const LOCAL_STORAGE_KEYS = {
  ACCESS_TOKEN: 'access_token',
  REFRESH_TOKEN: 'refresh_token',
  USER: 'user',
} as const;

export const DEFAULT_BUDGET_CATEGORIES = [
  'Groceries',
  'Rent/Mortgage',
  'Utilities',
  'Transportation',
  'Entertainment',
  'Dining Out',
  'Healthcare',
  'Savings',
  'Emergency Fund',
  'Miscellaneous',
] as const;