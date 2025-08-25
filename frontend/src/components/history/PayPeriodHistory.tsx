/**
 * Pay period history component showing past budget periods.
 */

import React from 'react';
import { 
  Paper, 
  Typography, 
  Box,
  List,
  ListItem,
  ListItemText,
  Chip,
  Divider,
  LinearProgress
} from '@mui/material';
import { Timeline, CalendarToday, AccountBalance } from '@mui/icons-material';
import { PayPeriod } from '../../types/budget';
import { formatCurrency, formatDate } from '../../utils/formatters';

interface PayPeriodHistoryProps {
  payPeriods: PayPeriod[];
}

export const PayPeriodHistory: React.FC<PayPeriodHistoryProps> = ({ payPeriods }) => {
  if (payPeriods.length === 0) {
    return (
      <Paper elevation={2} sx={{ p: 3, textAlign: 'center' }}>
        <Timeline sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
        <Typography variant="h6" color="textSecondary">
          No budget history yet
        </Typography>
        <Typography variant="body2" color="textSecondary">
          Complete your first pay period to see budget history here
        </Typography>
      </Paper>
    );
  }

  const completedPeriods = payPeriods.filter(p => p.status === 'completed');
  const activePeriod = payPeriods.find(p => p.status === 'active');

  const calculateSpentAmount = (payPeriod: PayPeriod): number => {
    if (!payPeriod.budget_categories) return 0;
    return payPeriod.budget_categories.reduce((total, category) => {
      const allocated = parseFloat(category.allocated_amount);
      const remaining = parseFloat(category.remaining_amount);
      return total + (allocated - remaining);
    }, 0);
  };

  const calculateSpentPercentage = (payPeriod: PayPeriod): number => {
    const totalIncome = parseFloat(payPeriod.total_income);
    const spentAmount = calculateSpentAmount(payPeriod);
    return totalIncome > 0 ? (spentAmount / totalIncome) * 100 : 0;
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active':
        return 'primary';
      case 'completed':
        return 'success';
      default:
        return 'default';
    }
  };

  return (
    <Box>
      {/* Current Active Period */}
      {activePeriod && (
        <Paper elevation={2} sx={{ mb: 3, overflow: 'hidden' }}>
          <Box sx={{ p: 2, bgcolor: 'primary.main', color: 'white' }}>
            <Typography variant="h6">
              Current Pay Period
            </Typography>
          </Box>
          
          <Box sx={{ p: 3 }}>
            <Box display="flex" justifyContent="space-between" alignItems="center" sx={{ mb: 2 }}>
              <Box display="flex" alignItems="center" gap={1}>
                <CalendarToday fontSize="small" />
                <Typography variant="subtitle1">
                  {formatDate(activePeriod.start_date)} - {formatDate(activePeriod.end_date)}
                </Typography>
              </Box>
              <Chip 
                label={activePeriod.status.toUpperCase()} 
                color={getStatusColor(activePeriod.status)} 
                size="small"
              />
            </Box>

            <Box sx={{ mb: 2 }}>
              <Box display="flex" justifyContent="space-between" alignItems="center" sx={{ mb: 1 }}>
                <Typography variant="body2" color="textSecondary">
                  Spending Progress
                </Typography>
                <Typography variant="body2" color="textSecondary">
                  {formatCurrency(calculateSpentAmount(activePeriod))} / {formatCurrency(activePeriod.total_income)}
                </Typography>
              </Box>
              <LinearProgress 
                variant="determinate" 
                value={calculateSpentPercentage(activePeriod)}
                sx={{ height: 8, borderRadius: 4 }}
              />
            </Box>

            <Typography variant="h6" color="primary">
              Total Income: {formatCurrency(activePeriod.total_income)}
            </Typography>
          </Box>
        </Paper>
      )}

      {/* Completed Pay Periods */}
      {completedPeriods.length > 0 && (
        <Paper elevation={2} sx={{ overflow: 'hidden' }}>
          <Box sx={{ p: 2, bgcolor: 'grey.100' }}>
            <Typography variant="h6" color="primary">
              Past Pay Periods
            </Typography>
          </Box>

          <List sx={{ py: 0 }}>
            {completedPeriods
              .sort((a, b) => new Date(b.start_date).getTime() - new Date(a.start_date).getTime())
              .map((payPeriod, index) => (
                <React.Fragment key={payPeriod.id}>
                  <ListItem sx={{ py: 2 }}>
                    <ListItemText
                      primary={
                        <Box display="flex" alignItems="center" justifyContent="space-between">
                          <Box display="flex" alignItems="center" gap={1}>
                            <CalendarToday fontSize="small" color="action" />
                            <Typography variant="subtitle1">
                              {formatDate(payPeriod.start_date)} - {formatDate(payPeriod.end_date)}
                            </Typography>
                            <Chip 
                              label={payPeriod.status.toUpperCase()} 
                              color={getStatusColor(payPeriod.status)} 
                              size="small"
                            />
                          </Box>
                          <Typography variant="h6" color="primary">
                            {formatCurrency(payPeriod.total_income)}
                          </Typography>
                        </Box>
                      }
                      secondary={
                        <Box sx={{ mt: 1 }}>
                          <Box display="flex" justifyContent="space-between" alignItems="center" sx={{ mb: 1 }}>
                            <Typography variant="body2" color="textSecondary">
                              Total Spent: {formatCurrency(calculateSpentAmount(payPeriod))} 
                              ({calculateSpentPercentage(payPeriod).toFixed(1)}%)
                            </Typography>
                            <Typography variant="body2" color="textSecondary">
                              Remaining: {formatCurrency(parseFloat(payPeriod.total_income) - calculateSpentAmount(payPeriod))}
                            </Typography>
                          </Box>
                          <LinearProgress 
                            variant="determinate" 
                            value={calculateSpentPercentage(payPeriod)}
                            sx={{ height: 6, borderRadius: 3 }}
                          />
                        </Box>
                      }
                    />
                  </ListItem>
                  {index < completedPeriods.length - 1 && <Divider />}
                </React.Fragment>
              ))}
          </List>
        </Paper>
      )}

      {completedPeriods.length === 0 && !activePeriod && (
        <Paper elevation={2} sx={{ p: 3, textAlign: 'center' }}>
          <AccountBalance sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" color="textSecondary">
            No completed pay periods yet
          </Typography>
          <Typography variant="body2" color="textSecondary">
            Start tracking your budget to see historical data here
          </Typography>
        </Paper>
      )}
    </Box>
  );
};