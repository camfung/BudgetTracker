/**
 * Transaction service for expense tracking.
 */

import api from './api';
import { 
  Transaction, 
  TransactionCreate, 
  TransactionUpdate, 
  TransactionBulkCreate,
  SpendingAnalytics 
} from '../types/transaction';
import { MessageResponse } from '../types/user';

interface GetTransactionsParams {
  pay_period_id?: number;
  category_id?: number;
  limit?: number;
  offset?: number;
}

/**
 * Create a new transaction.
 */
export const createTransaction = async (transactionData: TransactionCreate): Promise<Transaction> => {
  const response = await api.post<Transaction>('/transactions/', transactionData);
  return response.data;
};

/**
 * Create multiple transactions (bulk).
 */
export const createBulkTransactions = async (bulkData: TransactionBulkCreate): Promise<Transaction[]> => {
  const response = await api.post<Transaction[]>('/transactions/bulk', bulkData);
  return response.data;
};

/**
 * Get transactions with optional filters.
 */
export const getTransactions = async (params?: GetTransactionsParams): Promise<Transaction[]> => {
  const response = await api.get<Transaction[]>('/transactions/', { params });
  return response.data;
};

/**
 * Get a specific transaction by ID.
 */
export const getTransaction = async (transactionId: number): Promise<Transaction> => {
  const response = await api.get<Transaction>(`/transactions/${transactionId}`);
  return response.data;
};

/**
 * Update a transaction.
 */
export const updateTransaction = async (
  transactionId: number, 
  updateData: TransactionUpdate
): Promise<Transaction> => {
  const response = await api.put<Transaction>(`/transactions/${transactionId}`, updateData);
  return response.data;
};

/**
 * Delete a transaction.
 */
export const deleteTransaction = async (transactionId: number): Promise<MessageResponse> => {
  const response = await api.delete<MessageResponse>(`/transactions/${transactionId}`);
  return response.data;
};

/**
 * Get spending summary by category for a pay period.
 */
export const getSpendingSummary = async (payPeriodId: number): Promise<any[]> => {
  const response = await api.get<any[]>(`/transactions/summary/${payPeriodId}`);
  return response.data;
};

/**
 * Get comprehensive spending analytics across all periods.
 */
export const getSpendingAnalytics = async (): Promise<SpendingAnalytics> => {
  const response = await api.get<SpendingAnalytics>('/transactions/analytics/spending');
  return response.data;
};