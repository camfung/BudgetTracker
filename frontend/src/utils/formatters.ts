/**
 * Utility functions for formatting data.
 */

import { format, parseISO } from 'date-fns';

/**
 * Format currency amount.
 */
export const formatCurrency = (amount: string | number): string => {
  const numAmount = typeof amount === 'string' ? parseFloat(amount) : amount;
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(numAmount);
};

/**
 * Format date string for display.
 */
export const formatDate = (dateString: string, formatStr: string = 'MMM dd, yyyy'): string => {
  try {
    return format(parseISO(dateString), formatStr);
  } catch (error) {
    return dateString;
  }
};

/**
 * Format date for form inputs (YYYY-MM-DD).
 */
export const formatDateForInput = (date: Date | string): string => {
  const dateObj = typeof date === 'string' ? new Date(date) : date;
  return format(dateObj, 'yyyy-MM-dd');
};

/**
 * Format percentage.
 */
export const formatPercentage = (value: number, decimalPlaces: number = 1): string => {
  return `${(value * 100).toFixed(decimalPlaces)}%`;
};

/**
 * Calculate percentage of amount used.
 */
export const calculateUsagePercentage = (spent: string | number, total: string | number): number => {
  const spentNum = typeof spent === 'string' ? parseFloat(spent) : spent;
  const totalNum = typeof total === 'string' ? parseFloat(total) : total;
  
  if (totalNum === 0) return 0;
  return Math.min(spentNum / totalNum, 1); // Cap at 100%
};

/**
 * Get status color based on usage percentage.
 */
export const getUsageColor = (percentage: number): string => {
  if (percentage >= 0.9) return '#f44336'; // Red
  if (percentage >= 0.7) return '#ff9800'; // Orange
  return '#4caf50'; // Green
};

/**
 * Truncate text to specified length.
 */
export const truncateText = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength - 3) + '...';
};

/**
 * Capitalize first letter of each word.
 */
export const titleCase = (str: string): string => {
  return str.replace(/\w\S*/g, (txt) => 
    txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase()
  );
};