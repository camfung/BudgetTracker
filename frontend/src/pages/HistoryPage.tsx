/**
 * History page component showing past pay periods and analytics.
 */

import React from 'react';
import { Box, Typography, Alert } from '@mui/material';
import { Layout } from '../components/layout/Layout';
import { PayPeriodHistory } from '../components/history/PayPeriodHistory';
import { useBudget } from '../hooks/useBudget';

export const HistoryPage: React.FC = () => {
  const { allPayPeriods, isLoading, error } = useBudget();

  if (isLoading) {
    return (
      <Layout>
        <Box sx={{ textAlign: 'center', py: 4 }}>
          <Typography variant="h6" color="textSecondary">
            Loading history...
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

  return (
    <Layout>
      <Box>
        <Typography variant="h4" gutterBottom color="primary">
          Budget History
        </Typography>
        
        <Typography variant="body1" color="textSecondary" sx={{ mb: 4 }}>
          View your past pay periods and spending patterns
        </Typography>

        <PayPeriodHistory payPeriods={allPayPeriods || []} />
      </Box>
    </Layout>
  );
};