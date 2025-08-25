/**
 * Budget summary component showing current budget status.
 */

import React from 'react';
import {
  Box,
  Typography,
  Paper,
  LinearProgress,
  Grid,
  Card,
  CardContent,
  Chip,
} from '@mui/material';
import { TrendingUp, TrendingDown, AccountBalance } from '@mui/icons-material';
import { PayPeriod } from '../../types/budget';
import { formatCurrency, calculateUsagePercentage, getUsageColor } from '../../utils/formatters';

interface BudgetSummaryProps {
  payPeriod: PayPeriod;
  summary?: {
    total_allocated: string;
    total_spent: string;
    total_remaining: string;
    categories_summary: Array<{
      category: any;
      allocated: string;
      spent: string;
      remaining: string;
    }>;
  };
}

export const BudgetSummary: React.FC<BudgetSummaryProps> = ({ payPeriod, summary }) => {
  if (!payPeriod.budget_categories || payPeriod.budget_categories.length === 0) {
    return (
      <Paper elevation={2} sx={{ p: 3, textAlign: 'center' }}>
        <AccountBalance sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
        <Typography variant="h6" color="textSecondary">
          No budget categories yet
        </Typography>
        <Typography variant="body2" color="textSecondary">
          Create your first budget allocation to get started
        </Typography>
      </Paper>
    );
  }

  const totalIncome = parseFloat(payPeriod.total_income);
  const totalAllocated = summary ? parseFloat(summary.total_allocated) : 0;
  const totalSpent = summary ? parseFloat(summary.total_spent) : 0;
  const totalRemaining = totalAllocated - totalSpent;

  return (
    <Box>
      {/* Overview Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={3}>
          <Card elevation={1}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom variant="body2">
                Total Income
              </Typography>
              <Typography variant="h6" color="primary">
                {formatCurrency(totalIncome)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={3}>
          <Card elevation={1}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom variant="body2">
                Allocated
              </Typography>
              <Typography variant="h6" color="info.main">
                {formatCurrency(totalAllocated)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={3}>
          <Card elevation={1}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom variant="body2">
                Spent
              </Typography>
              <Typography variant="h6" color="error.main">
                {formatCurrency(totalSpent)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
        
        <Grid item xs={12} sm={3}>
          <Card elevation={1}>
            <CardContent>
              <Typography color="textSecondary" gutterBottom variant="body2">
                Remaining
              </Typography>
              <Typography variant="h6" color="success.main">
                {formatCurrency(totalRemaining)}
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Category Breakdown */}
      <Paper elevation={2} sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom color="primary">
          Budget Categories
        </Typography>
        
        <Grid container spacing={2}>
          {payPeriod.budget_categories.map((category) => {
            const allocated = parseFloat(category.allocated_amount);
            const remaining = parseFloat(category.remaining_amount);
            const spent = allocated - remaining;
            const usagePercentage = calculateUsagePercentage(spent, allocated);
            const progressColor = getUsageColor(usagePercentage);
            
            return (
              <Grid item xs={12} sm={6} md={4} key={category.id}>
                <Card elevation={1} sx={{ height: '100%' }}>
                  <CardContent>
                    <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                      <Typography variant="subtitle1" fontWeight="medium">
                        {category.name}
                      </Typography>
                      <Chip
                        size="small"
                        label={`${Math.round(usagePercentage * 100)}%`}
                        color={usagePercentage >= 0.9 ? 'error' : usagePercentage >= 0.7 ? 'warning' : 'success'}
                        variant="outlined"
                      />
                    </Box>
                    
                    <LinearProgress
                      variant="determinate"
                      value={Math.min(usagePercentage * 100, 100)}
                      sx={{
                        mb: 2,
                        height: 8,
                        borderRadius: 4,
                        '& .MuiLinearProgress-bar': {
                          backgroundColor: progressColor,
                        },
                      }}
                    />
                    
                    <Grid container spacing={1}>
                      <Grid item xs={6}>
                        <Typography variant="caption" color="textSecondary">
                          Allocated
                        </Typography>
                        <Typography variant="body2" fontWeight="medium">
                          {formatCurrency(allocated)}
                        </Typography>
                      </Grid>
                      
                      <Grid item xs={6}>
                        <Typography variant="caption" color="textSecondary">
                          Remaining
                        </Typography>
                        <Typography 
                          variant="body2" 
                          fontWeight="medium"
                          color={remaining < 0 ? 'error.main' : 'success.main'}
                        >
                          {formatCurrency(remaining)}
                        </Typography>
                      </Grid>
                    </Grid>
                    
                    <Box display="flex" alignItems="center" mt={1}>
                      {spent > 0 ? (
                        <TrendingUp sx={{ fontSize: 16, color: 'error.main', mr: 0.5 }} />
                      ) : (
                        <TrendingDown sx={{ fontSize: 16, color: 'success.main', mr: 0.5 }} />
                      )}
                      <Typography variant="caption" color="textSecondary">
                        Spent: {formatCurrency(spent)}
                      </Typography>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            );
          })}
        </Grid>
      </Paper>
    </Box>
  );
};