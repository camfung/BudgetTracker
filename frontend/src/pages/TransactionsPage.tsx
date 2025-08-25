/**
 * Transactions page component for managing expenses.
 */

import React from 'react';
import { Box, Typography, Grid, Alert } from '@mui/material';
import { Layout } from '../components/layout/Layout';
import { TransactionForm } from '../components/transactions/TransactionForm';
import { TransactionList } from '../components/transactions/TransactionList';
import { useBudget } from '../hooks/useBudget';
import { useTransactions } from '../hooks/useTransactions';

export const TransactionsPage: React.FC = () => {
  const { currentPayPeriod, isLoading: budgetLoading, error: budgetError } = useBudget();
  const { 
    transactions, 
    isLoading: transactionsLoading, 
    error: transactionsError,
    refreshTransactions 
  } = useTransactions();

  if (budgetLoading || transactionsLoading) {
    return (
      <Layout>
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <Typography variant="h6" color="textSecondary">
            Loading transactions...
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

  const handleTransactionCreated = () => {
    refreshTransactions();
  };

  const handleTransactionDeleted = () => {
    refreshTransactions();
  };

  return (
    <Layout>
      <Box>
        <Typography variant="h4" gutterBottom color="primary">
          Transactions
        </Typography>
        
        <Typography variant="body1" color="textSecondary" sx={{ mb: 4 }}>
          Add expenses and track your spending against your budget
        </Typography>

        <Grid container spacing={3}>
          {/* Transaction Form */}
          <Grid item xs={12} md={5}>
            {currentPayPeriod ? (
              <TransactionForm
                payPeriod={currentPayPeriod}
                onTransactionCreated={handleTransactionCreated}
              />
            ) : (
              <Alert severity="info">
                Create a pay period and set up budget categories before adding transactions
              </Alert>
            )}
          </Grid>

          {/* Transaction List */}
          <Grid item xs={12} md={7}>
            <TransactionList
              transactions={transactions}
              payPeriod={currentPayPeriod}
              onTransactionDeleted={handleTransactionDeleted}
            />
          </Grid>
        </Grid>
      </Box>
    </Layout>
  );
};