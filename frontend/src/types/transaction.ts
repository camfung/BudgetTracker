/**
 * Transaction-related TypeScript interfaces.
 */

export interface Transaction {
  id: number;
  pay_period_id: number;
  budget_category_id: number;
  amount: string;
  description: string;
  transaction_date: string;
  source: 'manual' | 'api';
  created_at: string;
}

export interface TransactionCreate {
  budget_category_id: number;
  amount: string;
  description: string;
  transaction_date?: string;
  source?: 'manual' | 'api';
}

export interface TransactionUpdate {
  description?: string;
  amount?: string;
}

export interface TransactionBulkCreate {
  transactions: TransactionCreate[];
}

export interface TransactionSummary {
  budget_category_id: number;
  category_name: string;
  allocated_amount: string;
  total_spent: string;
  remaining_amount: string;
  transaction_count: number;
}

export interface SpendingAnalytics {
  total_periods: number;
  total_income: string;
  total_spent: string;
  average_spending_per_period: string;
  top_categories: Array<{
    category: string;
    total_spent: string;
  }>;
  spending_trend: Array<{
    period: string;
    amount: string;
  }>;
}