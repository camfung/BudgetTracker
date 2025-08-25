/**
 * Budget-related TypeScript interfaces.
 */

export type PayFrequency = 'weekly' | 'bi_weekly' | 'monthly';

export interface BudgetCategory {
  id: number;
  pay_period_id: number;
  name: string;
  allocated_amount: string;
  remaining_amount: string;
  created_at: string;
}

export interface BudgetCategoryCreate {
  name: string;
  allocated_amount: string;
}

export interface PayPeriod {
  id: number;
  user_id: number;
  start_date: string;
  end_date: string;
  frequency: PayFrequency;
  total_income: string;
  status: 'active' | 'completed';
  created_at: string;
  budget_categories: BudgetCategory[];
}

export interface PayPeriodCreate {
  start_date: string;
  frequency: PayFrequency;
  total_income: string;
  budget_categories?: BudgetCategoryCreate[];
}

export interface BudgetAllocation {
  pay_period_id: number;
  allocations: BudgetCategoryCreate[];
}

export interface PeriodSummary {
  pay_period: PayPeriod;
  total_allocated: string;
  total_spent: string;
  total_remaining: string;
  categories_summary: CategorySummary[];
}

export interface CategorySummary {
  category: BudgetCategory;
  allocated: string;
  spent: string;
  remaining: string;
}