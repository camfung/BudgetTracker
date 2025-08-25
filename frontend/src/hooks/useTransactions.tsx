/**
 * Custom hook for managing transaction state and operations.
 */

import { useState, useEffect } from 'react';
import { Transaction } from '../types/transaction';
import { getTransactions } from '../services/transaction.service';
import { useBudget } from './useBudget';

export interface UseTransactionsReturn {
  transactions: Transaction[];
  isLoading: boolean;
  error: string | null;
  refreshTransactions: () => Promise<void>;
}

export const useTransactions = (): UseTransactionsReturn => {
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const { currentPayPeriod } = useBudget();

  const refreshTransactions = async () => {
    if (!currentPayPeriod) {
      setTransactions([]);
      setIsLoading(false);
      return;
    }

    try {
      setIsLoading(true);
      setError(null);
      
      const transactionData = await getTransactions({ pay_period_id: currentPayPeriod.id });
      setTransactions(transactionData);
    } catch (err: any) {
      console.error('Error fetching transactions:', err);
      setError(err.message || 'Failed to fetch transactions');
      setTransactions([]);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    refreshTransactions();
  }, [currentPayPeriod]);

  return {
    transactions,
    isLoading,
    error,
    refreshTransactions,
  };
};