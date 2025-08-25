/**
 * Budget service for pay periods and budget categories.
 */

import api from './api';
import { 
  PayPeriod, 
  PayPeriodCreate, 
  BudgetAllocation, 
  BudgetCategory, 
  PeriodSummary 
} from '../types/budget';

/**
 * Create a new pay period.
 */
export const createPayPeriod = async (payPeriodData: PayPeriodCreate): Promise<PayPeriod> => {
  const response = await api.post<PayPeriod>('/budget/pay-periods', payPeriodData);
  return response.data;
};

/**
 * Get all pay periods for the current user.
 */
export const getPayPeriods = async (status?: 'active' | 'completed'): Promise<PayPeriod[]> => {
  const params = status ? { status_filter: status } : {};
  const response = await api.get<PayPeriod[]>('/budget/pay-periods', { params });
  return response.data;
};

/**
 * Get a specific pay period by ID.
 */
export const getPayPeriod = async (payPeriodId: number): Promise<PayPeriod> => {
  const response = await api.get<PayPeriod>(`/budget/pay-periods/${payPeriodId}`);
  return response.data;
};

/**
 * Update a pay period.
 */
export const updatePayPeriod = async (
  payPeriodId: number, 
  updateData: { status?: 'active' | 'completed'; total_income?: string }
): Promise<PayPeriod> => {
  const response = await api.put<PayPeriod>(`/budget/pay-periods/${payPeriodId}`, updateData);
  return response.data;
};

/**
 * Allocate budget to categories for a pay period.
 */
export const allocateBudget = async (allocationData: BudgetAllocation): Promise<BudgetCategory[]> => {
  const response = await api.post<BudgetCategory[]>('/budget/allocate', allocationData);
  return response.data;
};

/**
 * Get spending summary for a pay period.
 */
export const getPeriodSummary = async (payPeriodId: number): Promise<PeriodSummary> => {
  const response = await api.get<PeriodSummary>(`/budget/pay-periods/${payPeriodId}/summary`);
  return response.data;
};

/**
 * Get the current active pay period.
 */
export const getCurrentActivePeriod = async (): Promise<PayPeriod> => {
  const response = await api.get<PayPeriod>('/budget/pay-periods/active/current');
  return response.data;
};