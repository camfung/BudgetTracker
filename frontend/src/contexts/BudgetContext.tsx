/**
 * Budget context for managing budget and transaction state.
 */

import { createContext, useState, useEffect, ReactNode, useCallback } from 'react';
import { PayPeriod, PeriodSummary } from '../types/budget';
import { Transaction, SpendingAnalytics } from '../types/transaction';
import { 
  getPayPeriods, 
  getPayPeriod, 
  getCurrentActivePeriod,
  getPeriodSummary 
} from '../services/budget.service';
import { 
  getTransactions, 
  getSpendingAnalytics 
} from '../services/transaction.service';
import { useUser } from '../hooks/useUser';

export interface BudgetContextType {
  // Pay Periods
  payPeriods: PayPeriod[];
  currentPeriod: PayPeriod | null;
  isLoadingPeriods: boolean;
  
  // Current Period Details
  currentSummary: PeriodSummary | null;
  recentTransactions: Transaction[];
  isLoadingCurrentData: boolean;
  
  // Analytics
  analytics: SpendingAnalytics | null;
  isLoadingAnalytics: boolean;
  
  // Actions
  refreshPayPeriods: () => Promise<void>;
  refreshCurrentPeriod: () => Promise<void>;
  refreshSummary: () => Promise<void>;
  refreshTransactions: () => Promise<void>;
  refreshAnalytics: () => Promise<void>;
  setCurrentPeriod: (period: PayPeriod | null) => void;
}

export const BudgetContext = createContext<BudgetContextType | undefined>(undefined);

interface BudgetProviderProps {
  children: ReactNode;
}

export const BudgetProvider: React.FC<BudgetProviderProps> = ({ children }) => {
  const { isAuthenticated } = useUser();
  
  // State
  const [payPeriods, setPayPeriods] = useState<PayPeriod[]>([]);
  const [currentPeriod, setCurrentPeriod] = useState<PayPeriod | null>(null);
  const [currentSummary, setCurrentSummary] = useState<PeriodSummary | null>(null);
  const [recentTransactions, setRecentTransactions] = useState<Transaction[]>([]);
  const [analytics, setAnalytics] = useState<SpendingAnalytics | null>(null);
  
  // Loading states
  const [isLoadingPeriods, setIsLoadingPeriods] = useState(false);
  const [isLoadingCurrentData, setIsLoadingCurrentData] = useState(false);
  const [isLoadingAnalytics, setIsLoadingAnalytics] = useState(false);

  // Refresh functions
  const refreshPayPeriods = useCallback(async () => {
    if (!isAuthenticated) return;
    
    setIsLoadingPeriods(true);
    try {
      const periods = await getPayPeriods();
      setPayPeriods(periods);
      
      // Set current period if none selected
      if (!currentPeriod && periods.length > 0) {
        try {
          const activePeriod = await getCurrentActivePeriod();
          setCurrentPeriod(activePeriod);
        } catch {
          // If no active period, use the most recent one
          setCurrentPeriod(periods[0]);
        }
      }
    } catch (error) {
      console.error('Failed to fetch pay periods:', error);
    } finally {
      setIsLoadingPeriods(false);
    }
  }, [isAuthenticated, currentPeriod]);

  const refreshCurrentPeriod = useCallback(async () => {
    if (!isAuthenticated || !currentPeriod) return;
    
    try {
      const updatedPeriod = await getPayPeriod(currentPeriod.id);
      setCurrentPeriod(updatedPeriod);
    } catch (error) {
      console.error('Failed to refresh current period:', error);
    }
  }, [isAuthenticated, currentPeriod]);

  const refreshSummary = useCallback(async () => {
    if (!isAuthenticated || !currentPeriod) return;
    
    setIsLoadingCurrentData(true);
    try {
      const summary = await getPeriodSummary(currentPeriod.id);
      setCurrentSummary(summary);
    } catch (error) {
      console.error('Failed to fetch period summary:', error);
    } finally {
      setIsLoadingCurrentData(false);
    }
  }, [isAuthenticated, currentPeriod]);

  const refreshTransactions = useCallback(async () => {
    if (!isAuthenticated || !currentPeriod) return;
    
    try {
      const transactions = await getTransactions({
        pay_period_id: currentPeriod.id,
        limit: 10
      });
      setRecentTransactions(transactions);
    } catch (error) {
      console.error('Failed to fetch transactions:', error);
    }
  }, [isAuthenticated, currentPeriod]);

  const refreshAnalytics = useCallback(async () => {
    if (!isAuthenticated) return;
    
    setIsLoadingAnalytics(true);
    try {
      const analyticsData = await getSpendingAnalytics();
      setAnalytics(analyticsData);
    } catch (error) {
      console.error('Failed to fetch analytics:', error);
    } finally {
      setIsLoadingAnalytics(false);
    }
  }, [isAuthenticated]);

  // Initial data loading
  useEffect(() => {
    if (isAuthenticated) {
      refreshPayPeriods();
      refreshAnalytics();
    } else {
      // Clear data when not authenticated
      setPayPeriods([]);
      setCurrentPeriod(null);
      setCurrentSummary(null);
      setRecentTransactions([]);
      setAnalytics(null);
    }
  }, [isAuthenticated, refreshPayPeriods, refreshAnalytics]);

  // Load current period data when current period changes
  useEffect(() => {
    if (currentPeriod) {
      refreshSummary();
      refreshTransactions();
    } else {
      setCurrentSummary(null);
      setRecentTransactions([]);
    }
  }, [currentPeriod, refreshSummary, refreshTransactions]);

  const value: BudgetContextType = {
    // Data
    payPeriods,
    currentPeriod,
    currentSummary,
    recentTransactions,
    analytics,
    
    // Loading states
    isLoadingPeriods,
    isLoadingCurrentData,
    isLoadingAnalytics,
    
    // Actions
    refreshPayPeriods,
    refreshCurrentPeriod,
    refreshSummary,
    refreshTransactions,
    refreshAnalytics,
    setCurrentPeriod,
  };

  return (
    <BudgetContext.Provider value={value}>
      {children}
    </BudgetContext.Provider>
  );
};