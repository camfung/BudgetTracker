/**
 * Custom hook for accessing budget context.
 */

import { useContext } from 'react';
import { BudgetContext } from '../contexts/BudgetContext';

export interface UseBudgetReturn {
  currentPayPeriod: any;
  allPayPeriods: any[];
  isLoading: boolean;
  error: string | null;
  refreshBudget: () => Promise<void>;
}

export const useBudget = (): UseBudgetReturn => {
  const context = useContext(BudgetContext);
  
  if (!context) {
    throw new Error('useBudget must be used within a BudgetProvider');
  }
  
  return {
    currentPayPeriod: context.currentPeriod,
    allPayPeriods: context.payPeriods,
    isLoading: context.isLoadingPeriods || context.isLoadingCurrentData,
    error: null, // We'll add error handling later
    refreshBudget: context.refreshCurrentPeriod,
  };
};