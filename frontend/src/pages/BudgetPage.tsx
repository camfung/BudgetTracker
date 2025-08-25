/**
 * Budget management page component.
 */

import React from 'react';
import { Box, Typography, Grid, Alert } from '@mui/material';
import { Layout } from '../components/layout/Layout';
import { PaycheckInput } from '../components/budget/PaycheckInput';
import { BudgetAllocation } from '../components/budget/BudgetAllocation';
import { BudgetSummary } from '../components/budget/BudgetSummary';
import { useBudget } from '../hooks/useBudget';

export const BudgetPage: React.FC = () => {
  const { 
    currentPayPeriod, 
    isLoading, 
    error, 
    refreshBudget 
  } = useBudget();

  if (isLoading) {
    return (
      <Layout>
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <Typography variant="h6" color="textSecondary">
            Loading budget...
          </Typography>
        </Box>
      </Layout>
    );
  }

  if (error) {
    return (
      <Layout>
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      </Layout>
    );
  }

  const handleBudgetUpdate = () => {
    refreshBudget();
  };

  return (
    <Layout>
      <Box>
        <Typography variant="h4" gutterBottom color="primary">
          Budget Management
        </Typography>
        
        <Typography variant="body1" color="textSecondary" sx={{ mb: 4 }}>
          Set up your biweekly budget and allocate funds to categories
        </Typography>

        <Grid container spacing={3}>
          {/* Current Budget Summary */}
          {currentPayPeriod && (
            <Grid item xs={12}>
              <BudgetSummary payPeriod={currentPayPeriod} />
            </Grid>
          )}

          {/* Paycheck Input */}
          <Grid item xs={12} md={6}>
            <PaycheckInput 
              onPayPeriodCreated={handleBudgetUpdate}
              currentPayPeriod={currentPayPeriod}
            />
          </Grid>

          {/* Budget Allocation */}
          <Grid item xs={12} md={6}>
            {currentPayPeriod ? (
              <BudgetAllocation 
                payPeriod={currentPayPeriod}
                onBudgetUpdated={handleBudgetUpdate}
              />
            ) : (
              <Alert severity="info">
                Create a pay period first to allocate your budget
              </Alert>
            )}
          </Grid>
        </Grid>
      </Box>
    </Layout>
  );
};