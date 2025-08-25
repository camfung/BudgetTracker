/**
 * Dashboard page component - main overview page.
 */

import React from 'react';
import { Box, Typography, Grid, Alert } from '@mui/material';
import { Layout } from '../components/layout/Layout';
import { BudgetSummary } from '../components/budget/BudgetSummary';
import { TransactionList } from '../components/transactions/TransactionList';
import { QuickActions } from '../components/dashboard/QuickActions';
import { useBudget } from '../hooks/useBudget';
import { useTransactions } from '../hooks/useTransactions';

export const DashboardPage: React.FC = () => {
  const { currentPayPeriod, isLoading: budgetLoading, error: budgetError } = useBudget();
  const { transactions, isLoading: transactionsLoading, error: transactionsError } = useTransactions();

  if (budgetLoading || transactionsLoading) {
    return (
      <Layout>
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <Typography variant="h6" color="textSecondary">
            Loading dashboard...
          </Typography>
        </Box>
      </Layout>
    );
  }

  if (budgetError || transactionsError) {
    return (
      <Layout>
        <Alert severity="error" sx={{ mb: 3 }}>
          {budgetError || transactionsError}
        </Alert>
      </Layout>
    );
  }

  return (
    <Layout>
      <Box>
        <Typography variant="h4" gutterBottom color="primary">
          Dashboard
        </Typography>
        
        <Typography variant="body1" color="textSecondary" sx={{ mb: 4 }}>
          Your biweekly budget overview
        </Typography>

        <Grid container spacing={3}>
          {/* Budget Summary */}
          <Grid item xs={12}>
            {currentPayPeriod ? (
              <BudgetSummary payPeriod={currentPayPeriod} />
            ) : (
              <Alert severity="info" sx={{ mb: 3 }}>
                Welcome! Create your first pay period to get started with budget tracking.
              </Alert>
            )}
          </Grid>

          {/* Quick Actions */}
          <Grid item xs={12} md={4}>
            <QuickActions payPeriod={currentPayPeriod} />
          </Grid>

          {/* Recent Transactions */}
          <Grid item xs={12} md={8}>
            <TransactionList 
              transactions={transactions} 
              payPeriod={currentPayPeriod}
              maxItems={5}
            />
          </Grid>
        </Grid>
      </Box>
    </Layout>
  );
};