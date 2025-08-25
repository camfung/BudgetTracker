/**
 * Transaction context for managing global transaction state.
 */

import React, { createContext, useContext } from 'react';
import { useTransactions, UseTransactionsReturn } from '../hooks/useTransactions';

interface TransactionContextType extends UseTransactionsReturn {}

const TransactionContext = createContext<TransactionContextType | undefined>(undefined);

interface TransactionProviderProps {
  children: React.ReactNode;
}

export const TransactionProvider: React.FC<TransactionProviderProps> = ({ children }) => {
  const transactionData = useTransactions();

  return (
    <TransactionContext.Provider value={transactionData}>
      {children}
    </TransactionContext.Provider>
  );
};

export const useTransactionContext = (): TransactionContextType => {
  const context = useContext(TransactionContext);
  if (context === undefined) {
    throw new Error('useTransactionContext must be used within a TransactionProvider');
  }
  return context;
};